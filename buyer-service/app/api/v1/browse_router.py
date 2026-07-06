"""Browse and discovery endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_buyer
from app.controllers.browse_controller import BrowseController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.browse_schema import PriceAlertRequest, PreferredSellerRequest, SavedSearchRequest

router = APIRouter(prefix="/browse", tags=["Browse & Discovery"])


@router.get("/listings", summary="Browse seller listings")
async def browse_listings(
    crop: str | None = Query(None),
    grade: str | None = Query(None),
    district: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    filters = {
        "crop": crop, "grade": grade, "district": district,
        "min_price": min_price, "max_price": max_price,
        "page": page, "per_page": per_page,
    }
    return await BrowseController.browse_listings(
        {k: v for k, v in filters.items() if v is not None}, db,
    )


@router.get("/listings/{listing_id}", summary="Get listing detail")
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.get_listing(listing_id, db)


@router.post("/saved-searches", summary="Save a search")
async def save_search(
    body: SavedSearchRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.save_search(buyer, body.label, body.filters, db)


@router.post("/preferred-sellers/{seller_id}", summary="Add preferred seller")
async def add_preferred_seller(
    seller_id: UUID,
    body: PreferredSellerRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.add_preferred_seller(buyer, seller_id, body.notes, db)


@router.post("/price-alerts", summary="Create a price alert")
async def create_price_alert(
    body: PriceAlertRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.create_price_alert(buyer, body.model_dump(), db)


# ── Enquiry proxy endpoints (buyer → seller service) ──

@router.post("/listings/{listing_id}/enquiry", summary="Send enquiry on a listing")
async def send_enquiry(
    listing_id: str,
    body: dict,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse

    body["buyer_id"] = str(buyer.id)
    body["buyer_name"] = buyer.individual_name or buyer.company_name or ""
    body["buyer_phone"] = buyer.primary_phone
    # Pull district from buyer's default delivery location
    primary_loc = next((loc for loc in (buyer.locations or []) if getattr(loc, "is_default", False)), None)
    if not primary_loc and buyer.locations:
        primary_loc = buyer.locations[0]
    body["buyer_district"] = primary_loc.district if primary_loc else None

    client = SellerServiceClient()
    result = await client.send_enquiry(listing_id, body)
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Enquiry sent!", data=result)


@router.get("/my-enquiries", summary="Get my sent enquiries")
async def get_my_enquiries(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse

    client = SellerServiceClient()
    result = await client.get_buyer_enquiries(str(buyer.id), page, per_page)
    return StandardResponse(success=True, data=result)


@router.post("/enquiries/{enquiry_id}/counter", summary="Counter an enquiry")
async def counter_enquiry(
    enquiry_id: str,
    body: dict,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse

    body["buyer_id"] = str(buyer.id)
    client = SellerServiceClient()
    result = await client.counter_enquiry(enquiry_id, body)
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Counter sent!", data=result)


@router.post("/enquiries/{enquiry_id}/withdraw", summary="Withdraw an enquiry")
async def withdraw_enquiry(
    enquiry_id: str,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse

    client = SellerServiceClient()
    result = await client.withdraw_enquiry(enquiry_id, str(buyer.id))
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Enquiry withdrawn.", data=result)


# ── Order proxy endpoints (buyer → seller service) ──

@router.get("/my-orders", summary="Get my orders")
async def get_my_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse
    client = SellerServiceClient()
    result = await client.get_buyer_orders(str(buyer.id), page, per_page)
    return StandardResponse(success=True, data=result)


@router.post("/orders/{order_id}/escrow-pay", summary="Pay into escrow")
async def escrow_pay(
    order_id: str,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse
    client = SellerServiceClient()
    result = await client.escrow_pay(order_id, str(buyer.id))
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Payment received. Escrow held. Delivery OTP generated.", data=result)


@router.post("/orders/{order_id}/confirm-delivery", summary="Confirm delivery with OTP")
async def confirm_delivery(
    order_id: str,
    body: dict,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse
    otp = body.get("otp", "")
    if not otp:
        return StandardResponse(success=False, message="OTP required")
    client = SellerServiceClient()
    result = await client.confirm_delivery(order_id, str(buyer.id), otp)
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Delivery confirmed! Payment released. Invoice generated.", data=result)


@router.post("/orders/{order_id}/cancel", summary="Cancel order")
async def cancel_order(
    order_id: str,
    body: dict,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse
    reason = body.get("reason", "")
    if not reason:
        return StandardResponse(success=False, message="Reason required")
    client = SellerServiceClient()
    result = await client.cancel_order(order_id, str(buyer.id), reason)
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Order cancelled.", data=result)


@router.post("/orders/{order_id}/dispute", summary="Raise dispute on order")
async def raise_dispute(
    order_id: str,
    body: dict,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse
    reason = body.get("reason", "")
    if not reason:
        return StandardResponse(success=False, message="Reason required")
    client = SellerServiceClient()
    result = await client.raise_dispute(order_id, str(buyer.id), reason, body.get("evidence_url"))
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, message="Dispute raised. Escrow frozen.", data=result)


@router.get("/orders/{order_id}/invoice", summary="Get order invoice")
async def get_invoice(
    order_id: str,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    from app.clients.seller_service_client import SellerServiceClient
    from app.schemas.common_schema import StandardResponse
    client = SellerServiceClient()
    result = await client.get_invoice(order_id, str(buyer.id))
    if result is None:
        return StandardResponse(success=False, message="Seller service unavailable")
    if "error" in result:
        return StandardResponse(success=False, message=result["error"])
    return StandardResponse(success=True, data=result)
