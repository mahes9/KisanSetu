"""KisanGPT Buyer Service - FastAPI application entry point."""

from __future__ import annotations

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db, close_db
from app.api.exceptions_handler import register_exception_handlers
from app.api.v1.auth_router import router as auth_router
from app.api.v1.buyer_router import router as buyer_router
from app.api.v1.kyc_router import router as kyc_router
from app.api.v1.requirement_router import router as requirement_router
from app.api.v1.offer_router import router as offer_router
from app.api.v1.location_router import router as location_router
from app.api.v1.user_router import router as user_router
from app.api.v1.browse_router import router as browse_router
from app.api.v1.order_router import router as order_router
from app.api.v1.analytics_router import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="KisanGPT Buyer Service",
    version=settings.APP_VERSION,
    description="Buyer-side microservice for the KisanGPT marketplace",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "buyer-service",
        "version": settings.APP_VERSION,
    }


app.include_router(auth_router, prefix="/api/v1")
app.include_router(buyer_router, prefix="/api/v1")
app.include_router(kyc_router, prefix="/api/v1")
app.include_router(requirement_router, prefix="/api/v1")
app.include_router(offer_router, prefix="/api/v1")
app.include_router(location_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(browse_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
    )
