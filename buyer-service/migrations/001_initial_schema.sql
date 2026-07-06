-- KisanGPT Buyer Service — Initial Schema
-- Run: psql -U postgres -d kisangpt_buyer -f migrations/001_initial_schema.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Buyers ──────────────────────────────────────────────────────
CREATE TABLE buyers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_number    VARCHAR(30) UNIQUE NOT NULL,
    buyer_type      VARCHAR(20) NOT NULL CHECK (buyer_type IN ('individual', 'organization')),

    -- Individual fields
    individual_name VARCHAR(100),
    aadhaar_hash    VARCHAR(128),
    upi_id          VARCHAR(50),

    -- Organization fields
    company_name    VARCHAR(200),
    gstin           VARCHAR(15),
    pan_number      VARCHAR(10),
    cin_number      VARCHAR(21),
    org_tier        VARCHAR(10) DEFAULT 'tier_3',
    business_type   VARCHAR(50),
    buyer_segment   VARCHAR(50),
    password_hash   VARCHAR(128),

    -- Contact
    primary_phone   VARCHAR(15) UNIQUE NOT NULL,
    primary_email   VARCHAR(255),

    -- KYC
    kyc_status          VARCHAR(30) DEFAULT 'pending',
    phone_verified      BOOLEAN DEFAULT FALSE,
    email_verified      BOOLEAN DEFAULT FALSE,
    aadhaar_verified    BOOLEAN DEFAULT FALSE,
    aadhaar_verified_at TIMESTAMPTZ,
    gstin_verified      BOOLEAN DEFAULT FALSE,
    upi_verified        BOOLEAN DEFAULT FALSE,
    bank_verified       BOOLEAN DEFAULT FALSE,

    -- Bank
    bank_account    VARCHAR(20),
    bank_ifsc       VARCHAR(11),
    bank_holder_name VARCHAR(100),

    -- Trust & stats
    trust_score         INTEGER DEFAULT 50,
    orders_completed    INTEGER DEFAULT 0,
    avg_rating          NUMERIC(3,2) DEFAULT 0,
    total_spent         NUMERIC(14,2) DEFAULT 0,
    total_gmv           NUMERIC(14,2) DEFAULT 0,
    disputes_count      INTEGER DEFAULT 0,
    dispute_loss_rate   NUMERIC(5,2) DEFAULT 0,
    pan_verified        BOOLEAN DEFAULT FALSE,

    -- Preferences
    language                VARCHAR(5) DEFAULT 'te',
    preferred_crops         JSONB,
    default_quality_grade   VARCHAR(20),
    min_order_kg            INTEGER,
    max_order_kg            INTEGER,
    preferred_districts     JSONB,

    -- Device
    device_token    VARCHAR(255),
    device_platform VARCHAR(10),
    app_version     VARCHAR(20),

    -- Status
    is_active       BOOLEAN DEFAULT TRUE,
    suspension_until TIMESTAMPTZ,
    suspension_reason VARCHAR(255),
    last_active_at  TIMESTAMPTZ,

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_buyers_phone ON buyers(primary_phone);
CREATE INDEX idx_buyers_email ON buyers(primary_email);
CREATE INDEX idx_buyers_type ON buyers(buyer_type);
CREATE INDEX idx_buyers_kyc ON buyers(kyc_status);

-- ── Buyer Users (Org) ───────────────────────────────────────────
CREATE TABLE buyer_users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id        UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    email           VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100) NOT NULL,
    phone           VARCHAR(15),
    role            VARCHAR(20) DEFAULT 'viewer',
    password_hash   VARCHAR(128),
    is_active       BOOLEAN DEFAULT FALSE,
    invitation_token VARCHAR(64),
    invitation_accepted BOOLEAN DEFAULT FALSE,
    invitation_accepted_at TIMESTAMPTZ,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (buyer_id, email)
);

-- ── Delivery Locations ──────────────────────────────────────────
CREATE TABLE buyer_locations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id        UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    label           VARCHAR(50) DEFAULT 'default',
    address_line1   VARCHAR(255) NOT NULL,
    address_line2   VARCHAR(255),
    village         VARCHAR(100),
    mandal          VARCHAR(100),
    district        VARCHAR(50) NOT NULL,
    state           VARCHAR(50) DEFAULT 'Andhra Pradesh',
    pincode         VARCHAR(6) NOT NULL,
    gps_lat         NUMERIC(10,7),
    gps_lon         NUMERIC(10,7),
    contact_name    VARCHAR(100),
    contact_phone   VARCHAR(15),
    is_default      BOOLEAN DEFAULT FALSE,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_locations_buyer ON buyer_locations(buyer_id);

-- ── Requirements (RFQ) ─────────────────────────────────────────
CREATE TABLE buyer_requirements (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_number  VARCHAR(30) UNIQUE NOT NULL,
    buyer_id            UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    crop                VARCHAR(30) NOT NULL,
    variety             VARCHAR(50),
    quantity_min_kg     NUMERIC(10,2) NOT NULL,
    quantity_max_kg     NUMERIC(10,2) NOT NULL,
    quality_grade       VARCHAR(20),
    quality_specs       JSONB,
    price_type          VARCHAR(20) DEFAULT 'negotiable',
    offer_price_per_q   NUMERIC(10,2),
    modal_price_at_create NUMERIC(10,2),
    ai_suggested_price  NUMERIC(10,2),
    delivery_location_id UUID REFERENCES buyer_locations(id),
    delivery_district   VARCHAR(50),
    delivery_by_date    TIMESTAMPTZ,
    gst_invoice_required BOOLEAN DEFAULT FALSE,
    allow_partial_match BOOLEAN DEFAULT TRUE,
    urgency             VARCHAR(20),
    notes               TEXT,
    status              VARCHAR(20) DEFAULT 'active',
    offers_received     INTEGER DEFAULT 0,
    views_count         INTEGER DEFAULT 0,
    matched_at          TIMESTAMPTZ,
    cancelled_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_requirements_buyer ON buyer_requirements(buyer_id);
CREATE INDEX idx_requirements_status ON buyer_requirements(status);
CREATE INDEX idx_requirements_crop ON buyer_requirements(crop);

-- ── Requirement Offers ──────────────────────────────────────────
CREATE TABLE requirement_offers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id      UUID NOT NULL REFERENCES buyer_requirements(id) ON DELETE CASCADE,
    seller_listing_id   UUID,
    seller_id           UUID,
    offer_price_per_q   NUMERIC(10,2) NOT NULL,
    quantity_kg         NUMERIC(10,2) NOT NULL,
    quality_grade       VARCHAR(20),
    round_number        INTEGER DEFAULT 1,
    parent_offer_id     UUID REFERENCES requirement_offers(id),
    counter_price_per_q NUMERIC(10,2),
    counter_quantity_kg NUMERIC(10,2),
    status              VARCHAR(20) DEFAULT 'pending',
    notes               TEXT,
    ai_suggestion       JSONB,
    responded_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_offers_requirement ON requirement_offers(requirement_id);
CREATE INDEX idx_offers_status ON requirement_offers(status);

-- ── Buyer Preferences ───────────────────────────────────────────
CREATE TABLE buyer_preferences (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id        UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    preference_type VARCHAR(30) NOT NULL,
    label           VARCHAR(100),
    filter_data     JSONB,
    target_seller_id UUID,
    notes           TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prefs_buyer ON buyer_preferences(buyer_id);

-- ── KYC Verifications (audit) ───────────────────────────────────
CREATE TABLE kyc_verifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id            UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    verification_type   VARCHAR(20) NOT NULL,
    status              VARCHAR(20) NOT NULL,
    success             BOOLEAN DEFAULT FALSE,
    failure_reason      TEXT,
    api_request_id      VARCHAR(100),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ── User Activity Log ───────────────────────────────────────────
CREATE TABLE user_activity_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id        UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    user_id         UUID REFERENCES buyer_users(id),
    action          VARCHAR(50) NOT NULL,
    entity_type     VARCHAR(30),
    entity_id       UUID,
    details         JSONB,
    ip_address      VARCHAR(45),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Language Changes ────────────────────────────────────────────
CREATE TABLE language_changes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id        UUID NOT NULL REFERENCES buyers(id) ON DELETE CASCADE,
    from_language   VARCHAR(5),
    to_language     VARCHAR(5) NOT NULL,
    changed_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Buyer Documents (Phase 1 stub) ─────────────────────────────
CREATE TABLE buyer_documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id        UUID REFERENCES buyers(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
