"""Order service — escrow, OTP verification, invoice, disputes."""

from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enquiry import Enquiry
from app.models.listing import Listing
from app.models.order import Order


COMMISSION_RATE = 0.02  # 2% platform commission
TDS_RATE = 0.01  # 1% TDS on seller payout


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def _generate_invoice_number() -> str:
    now = datetime.now(timezone.utc)
    rand = random.randint(10000, 99999)
    return f"INV-{now.strftime('%Y%m%d')}-{rand}"


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── Layer 2: Create order in awaiting_payment (escrow pending) ──

    async def create_from_enquiry(self, enquiry: Enquiry, listing: Listing) -> Order:
        now = datetime.now(timezone.utc)
        order_number = f"ORD-{now.strftime('%Y%m%d')}-{random.randint(10000, 99999)}"

        agreed_price = enquiry.seller_quoted_price or enquiry.offered_price_per_q or listing.ask_price_per_q
        quantity = enquiry.quantity_kg
        total = (quantity / 100) * agreed_price

        commission = round(total * COMMISSION_RATE, 2)
        tds = round(total * TDS_RATE, 2)
        net_payout = round(total - commission - tds, 2)

        order = Order(
            order_number=order_number,
            listing_id=listing.id,
            enquiry_id=enquiry.id,
            seller_id=listing.seller_id,
            buyer_id=enquiry.buyer_id,
            buyer_name=enquiry.buyer_name,
            crop=listing.crop,
            variety=listing.variety,
            quantity_kg=quantity,
            price_per_q=agreed_price,
            total_amount=round(total, 2),
            commission_rate=COMMISSION_RATE,
            commission_amount=commission,
            tds_rate=TDS_RATE,
            tds_amount=tds,
            net_seller_payout=net_payout,
            payment_mode=enquiry.payment_mode,
            delivery_district=enquiry.delivery_district,
            delivery_pincode=enquiry.delivery_pincode,
            status="awaiting_payment",
            escrow_status="pending",
        )
        self.session.add(order)
        await self.session.flush()
        return order

    # ── Layer 2: Buyer pays into escrow ──

    async def escrow_pay(self, order_id: UUID, buyer_id: str) -> Order:
        order = await self.get_order(order_id)
        if not order or order.buyer_id != buyer_id:
            raise ValueError("Order not found")
        if order.status != "awaiting_payment":
            raise ValueError("Order is not awaiting payment")

        now = datetime.now(timezone.utc)
        otp = _generate_otp()

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(
                status="confirmed",
                escrow_status="held",
                escrow_paid_at=now,
                delivery_otp=otp,
            )
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Seller dispatches ──

    async def mark_dispatched(self, order_id: UUID, seller_id: UUID) -> Order:
        order = await self.get_order(order_id)
        if not order or order.seller_id != seller_id:
            raise ValueError("Order not found")
        if order.status != "confirmed":
            raise ValueError("Order must be in confirmed status (payment held in escrow)")

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(
                status="dispatched",
                dispatched_at=datetime.now(timezone.utc),
            )
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Seller marks delivered ──

    async def mark_delivered(self, order_id: UUID, seller_id: UUID) -> Order:
        order = await self.get_order(order_id)
        if not order or order.seller_id != seller_id:
            raise ValueError("Order not found")
        if order.status != "dispatched":
            raise ValueError("Order must be in dispatched status")

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(
                status="delivered",
                delivered_at=datetime.now(timezone.utc),
            )
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Layer 3: Buyer confirms delivery with OTP ──

    async def confirm_delivery_with_otp(self, order_id: UUID, buyer_id: str, otp: str) -> Order:
        order = await self.get_order(order_id)
        if not order or order.buyer_id != buyer_id:
            raise ValueError("Order not found")
        if order.status != "delivered":
            raise ValueError("Order must be in delivered status")
        if order.delivery_otp != otp:
            raise ValueError("Invalid OTP. Please check and try again.")

        now = datetime.now(timezone.utc)
        invoice_number = _generate_invoice_number()

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(
                status="completed",
                delivery_otp_verified=True,
                delivery_confirmed_at=now,
                escrow_status="released",
                escrow_released_at=now,
                payment_released_at=now,
                invoice_number=invoice_number,
                invoice_generated_at=now,
            )
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Layer 6: Raise dispute ──

    async def raise_dispute(self, order_id: UUID, raised_by: str, raiser_id: str, reason: str, evidence_url: str | None = None) -> Order:
        order = await self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")

        if raised_by == "buyer" and order.buyer_id != raiser_id:
            raise ValueError("Access denied")
        if raised_by == "seller" and str(order.seller_id) != raiser_id:
            raise ValueError("Access denied")

        if order.status not in ("delivered", "completed"):
            raise ValueError("Disputes can only be raised on delivered or completed orders")
        if order.dispute_status == "open":
            raise ValueError("A dispute is already open for this order")

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(
                status="disputed",
                dispute_status="open",
                dispute_reason=reason,
                dispute_raised_by=raised_by,
                dispute_raised_at=datetime.now(timezone.utc),
                dispute_evidence_url=evidence_url,
                escrow_status="frozen",
            )
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Layer 6: Resolve dispute (platform admin) ──

    async def resolve_dispute(self, order_id: UUID, resolution: str, action: str) -> Order:
        order = await self.get_order(order_id)
        if not order or order.dispute_status != "open":
            raise ValueError("No open dispute found")

        now = datetime.now(timezone.utc)
        values = {
            "dispute_status": "resolved",
            "dispute_resolved_at": now,
            "dispute_resolution": resolution,
        }

        if action == "release_to_seller":
            values["status"] = "completed"
            values["escrow_status"] = "released"
            values["escrow_released_at"] = now
            values["payment_released_at"] = now
            if not order.invoice_number:
                values["invoice_number"] = _generate_invoice_number()
                values["invoice_generated_at"] = now
        elif action == "refund_buyer":
            values["status"] = "refunded"
            values["escrow_status"] = "refunded"
            values["escrow_refunded_at"] = now
        elif action == "partial_release":
            values["status"] = "completed"
            values["escrow_status"] = "released"
            values["escrow_released_at"] = now
            values["payment_released_at"] = now
            if not order.invoice_number:
                values["invoice_number"] = _generate_invoice_number()
                values["invoice_generated_at"] = now
        else:
            raise ValueError("Invalid action. Use: release_to_seller, refund_buyer, partial_release")

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(**values)
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Cancel order (before dispatch) ──

    async def cancel_order(self, order_id: UUID, cancelled_by: str, canceller_id: str, reason: str) -> Order:
        order = await self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")

        if cancelled_by == "buyer" and order.buyer_id != canceller_id:
            raise ValueError("Access denied")
        if cancelled_by == "seller" and str(order.seller_id) != canceller_id:
            raise ValueError("Access denied")

        if order.status not in ("awaiting_payment", "confirmed"):
            raise ValueError("Can only cancel before dispatch")

        now = datetime.now(timezone.utc)
        values = {
            "status": "cancelled",
            "cancelled_at": now,
            "cancellation_reason": f"[{cancelled_by}] {reason}",
        }

        if order.escrow_status == "held":
            values["escrow_status"] = "refunded"
            values["escrow_refunded_at"] = now

        await self.session.execute(
            update(Order).where(Order.id == order_id).values(**values)
        )
        await self.session.commit()
        return await self.get_order(order_id)

    # ── Layer 5: Get invoice ──

    async def get_invoice(self, order_id: UUID, requester_id: str) -> dict:
        order = await self.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
        if order.buyer_id != requester_id and str(order.seller_id) != requester_id:
            raise ValueError("Access denied")
        if not order.invoice_number:
            raise ValueError("Invoice not generated yet. Complete the order first.")

        return {
            "invoice_number": order.invoice_number,
            "order_number": order.order_number,
            "date": str(order.invoice_generated_at),
            "platform": "KisanSetu",
            "gstin": "PENDING_REGISTRATION",
            "buyer_name": order.buyer_name,
            "buyer_id": order.buyer_id,
            "seller_id": str(order.seller_id),
            "crop": order.crop,
            "variety": order.variety,
            "quantity_kg": order.quantity_kg,
            "price_per_quintal": order.price_per_q,
            "gross_amount": order.total_amount,
            "platform_commission_pct": order.commission_rate * 100,
            "platform_commission": order.commission_amount,
            "tds_pct": order.tds_rate * 100,
            "tds_amount": order.tds_amount,
            "net_seller_payout": order.net_seller_payout,
            "payment_mode": order.payment_mode,
            "delivery_district": order.delivery_district,
        }

    # ── Queries ──

    async def get_order(self, order_id: UUID) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_orders_for_seller(self, seller_id: UUID, status: str | None = None, page: int = 1, per_page: int = 20) -> dict:
        query = select(Order).where(Order.seller_id == seller_id)
        count_query = select(func.count(Order.id)).where(Order.seller_id == seller_id)

        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)

        query = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)
        orders = list(result.scalars().all())
        total = total_result.scalar() or 0

        return {
            "orders": [self._to_dict(o, viewer="seller") for o in orders],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_orders_for_buyer(self, buyer_id: str, page: int = 1, per_page: int = 20) -> dict:
        query = select(Order).where(Order.buyer_id == buyer_id)
        count_query = select(func.count(Order.id)).where(Order.buyer_id == buyer_id)

        query = query.order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)
        orders = list(result.scalars().all())
        total = total_result.scalar() or 0

        return {
            "orders": [self._to_dict(o, viewer="buyer") for o in orders],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_platform_revenue(self) -> dict:
        non_cancelled = Order.status.notin_(["cancelled", "refunded", "awaiting_payment"])
        total_commission = await self.session.execute(
            select(func.sum(Order.commission_amount)).where(non_cancelled)
        )
        total_tds = await self.session.execute(
            select(func.sum(Order.tds_amount)).where(non_cancelled)
        )
        total_gmv = await self.session.execute(
            select(func.sum(Order.total_amount)).where(non_cancelled)
        )
        order_count = await self.session.execute(
            select(func.count(Order.id)).where(non_cancelled)
        )

        return {
            "total_gmv": round(total_gmv.scalar() or 0, 2),
            "total_commission_earned": round(total_commission.scalar() or 0, 2),
            "total_tds_collected": round(total_tds.scalar() or 0, 2),
            "total_orders": order_count.scalar() or 0,
            "commission_rate_percent": COMMISSION_RATE * 100,
            "tds_rate_percent": TDS_RATE * 100,
        }

    def _to_dict(self, o: Order, viewer: str = "public") -> dict:
        d = {
            "id": str(o.id),
            "order_number": o.order_number,
            "listing_id": str(o.listing_id),
            "enquiry_id": str(o.enquiry_id),
            "seller_id": str(o.seller_id),
            "buyer_id": o.buyer_id,
            "buyer_name": o.buyer_name,
            "crop": o.crop,
            "variety": o.variety,
            "quantity_kg": o.quantity_kg,
            "price_per_q": o.price_per_q,
            "total_amount": o.total_amount,
            "commission_rate_pct": o.commission_rate * 100,
            "commission_amount": o.commission_amount,
            "tds_rate_pct": o.tds_rate * 100,
            "tds_amount": o.tds_amount,
            "net_seller_payout": o.net_seller_payout,
            "payment_mode": o.payment_mode,
            "delivery_district": o.delivery_district,
            "escrow_status": o.escrow_status,
            "escrow_paid_at": str(o.escrow_paid_at) if o.escrow_paid_at else None,
            "delivery_otp": o.delivery_otp if viewer == "buyer" else None,
            "delivery_otp_verified": o.delivery_otp_verified,
            "invoice_number": o.invoice_number,
            "dispute_status": o.dispute_status,
            "dispute_reason": o.dispute_reason,
            "dispute_raised_by": o.dispute_raised_by,
            "status": o.status,
            "dispatched_at": str(o.dispatched_at) if o.dispatched_at else None,
            "delivered_at": str(o.delivered_at) if o.delivered_at else None,
            "delivery_confirmed_at": str(o.delivery_confirmed_at) if o.delivery_confirmed_at else None,
            "payment_released_at": str(o.payment_released_at) if o.payment_released_at else None,
            "cancelled_at": str(o.cancelled_at) if o.cancelled_at else None,
            "created_at": str(o.created_at) if o.created_at else None,
        }
        return d
