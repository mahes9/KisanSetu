"""KisanGPT Seller Service - FastAPI application entry point."""

from __future__ import annotations

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db, close_db
from app.api.exceptions_handler import register_exception_handlers
from app.api.v1.auth_router import router as auth_router
from app.api.v1.seller_router import router as seller_router
from app.api.v1.farm_router import router as farm_router
from app.api.v1.draft_router import router as draft_router
from app.api.v1.listing_router import router as listing_router
from app.api.v1.photo_router import router as photo_router
from app.api.v1.analytics_router import router as analytics_router
from app.api.v1.enquiry_router import router as enquiry_router
from app.api.v1.order_router import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="KisanGPT Seller Service",
    version=settings.APP_VERSION,
    description="Seller-side microservice for the KisanGPT marketplace",
    lifespan=lifespan,
)

# ── CORS middleware ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ─────────────────────────────────────────
register_exception_handlers(app)

# ── Health check ────────────────────────────────────────────────


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "seller-service",
        "version": settings.APP_VERSION,
    }


# ── V1 API routers ─────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(seller_router, prefix="/api/v1")
app.include_router(farm_router, prefix="/api/v1")
app.include_router(draft_router, prefix="/api/v1")
app.include_router(listing_router, prefix="/api/v1")
app.include_router(photo_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(enquiry_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
    )
