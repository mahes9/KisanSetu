"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration for the Buyer Service, loaded from .env file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # ── Application ──────────────────────────────────────
    APP_NAME: str = "buyer-service"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    PORT: int = 8002

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kisangpt_buyer"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # ── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/1"

    # ── JWT ──────────────────────────────────────────────
    JWT_SECRET: str = "change-me-to-a-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_DAYS: int = 7

    # ── Internal Services ────────────────────────────────
    SELLER_SERVICE_URL: str = "http://localhost:8001"
    PRICE_SERVICE_URL: str = "http://localhost:8006"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8007"

    # ── Razorpay ─────────────────────────────────────────
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # ── UIDAI (Aadhaar) ─────────────────────────────────
    UIDAI_API_URL: str = ""
    UIDAI_API_KEY: str = ""

    # ── GSTN API ─────────────────────────────────────────
    GSTN_API_URL: str = ""
    GSTN_API_KEY: str = ""

    # ── Feature Flags ────────────────────────────────────
    ENABLE_AADHAAR_VERIFICATION: bool = False
    ENABLE_BANK_VERIFICATION: bool = False
    ENABLE_UPI_VERIFICATION: bool = False
    ENABLE_GSTIN_VERIFICATION: bool = False
    ENABLE_REAL_PRICE_DATA: bool = False
    ENABLE_NOTIFICATIONS: bool = False
    ENABLE_SELLER_SERVICE: bool = False

    # ── Phase 1 Scope ────────────────────────────────────
    PHASE1_CROPS: str = "tomato,chilli_dry,chilli_green,groundnut"
    PHASE1_DISTRICTS: str = "kurnool,nandyal"

    # ── Observability ────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── Computed helpers ─────────────────────────────────
    @property
    def phase1_crops_list(self) -> list[str]:
        return [c.strip() for c in self.PHASE1_CROPS.split(",") if c.strip()]

    @property
    def phase1_districts_list(self) -> list[str]:
        return [d.strip() for d in self.PHASE1_DISTRICTS.split(",") if d.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"


settings = Settings()
