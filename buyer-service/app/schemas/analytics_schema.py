"""Analytics request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_spent: float = 0
    orders_completed: int = 0
    active_requirements: int = 0
    pending_deliveries: int = 0
    avg_price_paid: float | None = None
    top_crops: list[dict] | None = None
    recent_orders: list[dict] | None = None


class SpendTrendResponse(BaseModel):
    period: str
    data: list[dict] = []


class VendorPerformanceResponse(BaseModel):
    vendors: list[dict] = []
    total_vendors: int = 0


class GSTSummaryResponse(BaseModel):
    period: str
    total_gst_paid: float = 0
    invoices: list[dict] = []


class ExportResponse(BaseModel):
    download_url: str
    format: str
    generated_at: str
