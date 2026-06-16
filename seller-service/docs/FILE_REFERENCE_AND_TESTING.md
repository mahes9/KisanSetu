# KisanSetu Seller Service — Complete File Reference & Testing Guide

## Table of Contents

1. [How Every File Connects (The Big Picture)](#1-how-every-file-connects)
2. [Every File Explained](#2-every-file-explained)
3. [How to Test Every Function](#3-how-to-test-every-function)
4. [Connection Map Between Files](#4-connection-map-between-files)

---

## 1. How Every File Connects

When a farmer hits an API endpoint, here is the exact flow through the codebase:

```
FARMER'S PHONE
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  main.py  — FastAPI app starts here                         │
│  Registers all 7 routers, CORS, error handlers              │
│  Starts DB connection on boot, closes on shutdown            │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│  app/api/v1/*_router.py  — HTTP endpoints                   │
│  Extracts JWT → gets seller → validates request body         │
│  Calls: deps.py (auth), controller                          │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│  app/api/deps.py  — Authentication middleware                │
│  Decodes JWT token → looks up seller from DB                 │
│  Calls: core/security.py (JWT), seller_repo.py (DB lookup)  │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│  app/controllers/*_controller.py  — Thin pass-through        │
│  Creates service instance, passes seller_id + data           │
│  Returns StandardResponse wrapper                            │
│  Calls: services                                             │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│  app/services/*_service.py  — ALL BUSINESS LOGIC             │
│  Validates rules, coordinates between repos + clients        │
│  Calls: repositories (DB), clients (external), core/*        │
└────────────┬────────────────────┬────────────────────────────┘
             │                    │
    ┌────────┘                    └────────┐
    ▼                                      ▼
┌─────────────────────┐    ┌─────────────────────────────────┐
│  app/repositories/  │    │  app/clients/                   │
│  SQL queries only   │    │  External API calls only        │
│  Uses: models/      │    │  price_client → Price Service   │
│  Returns: ORM objs  │    │  event_bus → Redis pub/sub      │
└────────┬────────────┘    │  notification → SMS mock        │
         │                 │  supabase → Photo storage       │
         ▼                 └─────────────────────────────────┘
┌─────────────────────┐
│  app/models/        │
│  DB table schemas   │
│  SQLAlchemy ORM     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  PostgreSQL 16      │
│  9 tables           │
└─────────────────────┘
```

### Rule: Data flows DOWN, never UP.

- Router NEVER touches the database directly
- Service NEVER returns HTTP status codes
- Repository NEVER validates business rules
- Model NEVER calls external APIs

---

## 2. Every File Explained

### Root Files

| File | What It Does | Connects To |
|------|-------------|-------------|
| `main.py` | FastAPI app entry point. Registers all 7 routers, sets up CORS, health check `/health`, connects to DB on startup | `app/config.py`, `app/db/database.py`, all routers |
| `pyproject.toml` | Lists all Python dependencies (FastAPI, SQLAlchemy, anthropic, etc.) | pip/poetry uses this |
| `alembic.ini` | Alembic config — points to DB URL and migrations folder | `migrations/env.py` |
| `migrations/env.py` | Runs DB migrations asynchronously. Imports all models so Alembic can detect table changes | `app/models/__init__.py`, `app/config.py` |
| `Dockerfile` | Builds the Docker image. Two-stage: exports deps from poetry, then runs uvicorn | `main.py` |
| `docker-compose.yml` | Starts 3 containers: postgres:16, redis:7, seller-service | `Dockerfile` |
| `.env.example` | Template for all environment variables | `app/config.py` reads these |
| `pytest.ini` | Test config: asyncio_mode=auto, test paths | pytest uses this |

---

### app/config.py

```
What: Loads all env variables into a typed Python object using Pydantic BaseSettings
Why: So every file can do `from app.config import settings` and get typed config
Connects to: .env file (reads), every other file (imports settings)
```

**Key variables:** DATABASE_URL, REDIS_URL, JWT_SECRET, ANTHROPIC_API_KEY, ENABLE_AI_GRADING

---

### app/core/ — Shared Business Logic (No DB, No HTTP)

| File | What It Does | Used By |
|------|-------------|---------|
| `constants.py` | All magic numbers: PHASE1_CROPS (4 crops), MAX_ACTIVE_LISTINGS (5), commission tiers (3%/5%/8%), CONFIDENCE_THRESHOLD (60) | validators, services |
| `enums.py` | Python enums: ListingStatus, KycStatus, HarvestStatus, Grade, DraftStatus, etc. | models, schemas |
| `exceptions.py` | 30 custom errors (E001-E030) each with English + Telugu message. Example: `FloorPriceViolationError`, `MaxListingsReachedError` | services, handlers |
| `messages.py` | Success/error message dictionaries with `en` + `te` translations | controllers, services |
| `security.py` | `hash_password()` (bcrypt), `verify_password()`, `create_jwt()`, `decode_jwt()` (python-jose), `hash_aadhaar()` (SHA-256) | deps.py, auth flows |
| `state_machine.py` | Listing status rules: active→paused OK, sold→anything BLOCKED. `transition_listing()` raises error on invalid move | listing_service.py |
| `validators.py` | Pure functions: `validate_crop()`, `validate_quantity()`, `calculate_floor_price()`, `validate_floor_price()`, `calculate_payout_preview()` (commission calc), `validate_publish_preflight()` | services |

**How `state_machine.py` works:**
```
active  → [paused, matched, cancelled, expired]    ✓ allowed
paused  → [active, cancelled, expired]              ✓ allowed
matched → [sold, cancelled]                         ✓ allowed
sold    → []                                        ✗ terminal, nothing allowed
expired → []                                        ✗ terminal
cancelled → []                                      ✗ terminal
```

**How `validators.py` commission calc works:**
```
≤500kg  → 3% commission on total amount
≤2000kg → 5% commission
>2000kg → 8% commission
Example: 800kg × ₹1200/q = ₹9600 gross → 5% = ₹480 commission → ₹9120 payout
```

---

### app/models/ — Database Tables (SQLAlchemy ORM)

| File | Table Name | Columns | Connected To |
|------|-----------|---------|-------------|
| `base.py` | (none — base class) | Provides `created_at`, `updated_at` timestamps to ALL models | Every model inherits this |
| `seller.py` | `sellers` | id, phone, full_name, aadhaar_hash, kyc_status, upi_id, bank info, trust_score, cancellation_count, suspension_until | farms, listings, drafts (FK) |
| `farm.py` | `farms` | id, seller_id, gps coords, district, village, acreage, irrigation, soil, crops_grown | sellers (FK) |
| `listing_draft.py` | `listing_drafts` | id, seller_id, draft_status, current_step, completeness_score, step1-5_data (JSONB), step1-5_completed, last_active_at | sellers (FK), draft_save_log |
| `listing_draft.py` | `draft_save_log` | id, draft_id, save_trigger, step_number, data_snapshot, device, session_id | listing_drafts (FK) |
| `listing_photo.py` | `listing_photos` | id, listing_draft_id, listing_id, photo_type, storage_url, perceptual_hash, dimensions | listing_drafts (FK), listings (FK) |
| `ai_grading_log.py` | `ai_grading_log` | id, listing_draft_id, ai_provider, model_used, crop, photo_urls, raw_response, parsed_grade, confidence, tokens, cost | listing_drafts (FK) |
| `listing.py` | `listings` | id, seller_id, listing_number, crop, quantity, grade, prices, transport, status, price_edit_history, expires_at, views | sellers (FK), listing_drafts (FK) |
| `price_snapshot.py` | `price_snapshots_cache` | id, crop, district, modal_price, floor_price, fetched_at | standalone cache |
| `season_summary.py` | `season_summaries` | id, seller_id, season, year, earnings, sales counts, best_crop, avg_grade | sellers (FK) |
| `__init__.py` | Re-exports all models | Alembic imports this to discover tables |

---

### app/schemas/ — Request/Response Shapes (Pydantic v2)

| File | What It Defines |
|------|----------------|
| `common_schema.py` | `StandardResponse` (wraps every API response: success, message, data), `PaginatedResponse`, `ErrorResponse` |
| `draft_schema.py` | `Step1Data` (crop, quantity, harvest), `Step2Data` (photos, grade), `Step3Data` (price), `Step4Data` (transport), `Step5Data` (consents), `CreateDraftRequest`, `SaveDraftRequest`, `DraftResponse` |
| `listing_schema.py` | `PublishRequest`, `EditPriceRequest`, `CancelListingRequest`, `ListingResponse` (includes payout_preview, days_remaining), `PublicListingResponse` (NO seller_id — PII stripped) |
| `photo_schema.py` | `PhotoUploadResponse`, `GradingResult`, `GradingStatusResponse` |
| `analytics_schema.py` | `SeasonSummaryResponse`, `EarningsHistoryResponse`, `MandiComparisonResponse`, `DashboardResponse` |
| `auth_schema.py` | `SendOTPRequest`, `VerifyOTPRequest`, `TokenResponse` (stub) |
| `seller_schema.py` | `SellerProfile`, `UpdateSellerRequest` (stub) |
| `farm_schema.py` | `CreateFarmRequest`, `FarmResponse` (stub) |
| `price_schema.py` | `PriceResponse` for price service data |

---

### app/repositories/ — Database Queries

| File | Table | Key Methods |
|------|-------|------------|
| `draft_repo.py` | listing_drafts | `create_draft()`, `get_draft_by_id()`, `update_draft()`, `delete_draft()` (soft), `list_drafts_by_seller()`, `count_drafts_by_seller()`, `save_log_entry()`, `mark_published()`, `get_stale_drafts()` |
| `listing_repo.py` | listings | `create_from_draft()` (generates KGP-YYYYMMDD-XXXX number), `get_listing_by_id()`, `update_listing_status()`, `update_listing_price()`, `count_active_listings()`, `get_listings_paginated()`, `get_expired_active_listings()`, `increment_views()` |
| `photo_repo.py` | listing_photos | `create_photo()`, `get_photos_by_draft()`, `check_duplicate_hash()`, `update_listing_id()` |
| `ai_log_repo.py` | ai_grading_log | `create_log()`, `get_logs_by_draft()`, `get_latest_successful()` |
| `season_repo.py` | season_summaries | `get_season_summary()`, `upsert_season_summary()`, `get_all_seasons()`, `get_seller_total_earnings()` |
| `seller_repo.py` | sellers | `get_by_id()`, `get_by_phone()`, `get_for_update()` (row lock), `update_cancellation_count()`, `suspend_seller()` |
| `farm_repo.py` | farms | `create_farm()`, `get_farms_by_seller()` |

---

### app/services/ — Business Logic

#### draft_service.py (Module 3)

| Method | What It Does | Calls |
|--------|-------------|-------|
| `create_draft()` | Checks max 3 drafts → validates crop → creates in DB → calculates completeness | draft_repo, validators, completeness_service |
| `save_step()` | Merges step data → recalculates score → logs save event | draft_repo, completeness_service |
| `get_draft()` | Gets draft + checks ownership + checks price staleness | draft_repo |
| `list_drafts()` | Returns all drafts for a seller | draft_repo |
| `delete_draft()` | Soft deletes (marks as deleted, doesn't erase) | draft_repo |
| `clone_draft()` | Copies steps 1,3,4 (NOT step 2 photos, NOT step 5 consents) | draft_repo, completeness_service |

#### photo_service.py (Module 4)

| Method | What It Does | Calls |
|--------|-------------|-------|
| `upload_photos()` | Validates 3 photos → compresses with Pillow → calculates perceptual hash → checks for duplicates → uploads to Supabase → saves metadata | photo_repo, draft_repo, supabase_client |
| `trigger_grading()` | Sends photo URLs to AI → logs result → updates draft step2 | ai_router, ai_log_repo, draft_repo |
| `get_grading_status()` | Returns latest grading result for a draft | ai_log_repo, draft_repo |
| `_compress_photo()` | Reduces JPEG quality until under 2MB, resizes if needed | Pillow (PIL) |
| `_calculate_perceptual_hash()` | 8x8 grayscale → average → 64-bit hash for duplicate detection | Pillow (PIL) |

#### ai_service/ai_router.py (Module 4)

| Method | What It Does | Calls |
|--------|-------------|-------|
| `grade()` | Try Claude → if fails, try Gemini → if fails, return manual fallback. Adds `low_confidence_warning` if confidence < 60 | claude_service, gemini_service |

#### ai_service/claude_service.py

| Method | What It Does | Calls |
|--------|-------------|-------|
| `grade_photos()` | Sends 3 photo URLs + crop-specific prompt to Claude API → parses JSON response → returns grade A/B/C + confidence | Anthropic SDK, prompts.py |

#### ai_service/gemini_service.py

| Method | What It Does | Calls |
|--------|-------------|-------|
| `grade_photos()` | Same as Claude but uses Google Gemini API as fallback | google-generativeai SDK, prompts.py |

#### ai_service/prompts.py

| What | Content |
|------|---------|
| 4 crop-specific prompts | Detailed grading criteria for tomato, chilli_dry, chilli_green, groundnut. Tells AI to return JSON with grade (A/B/C), confidence (0-100), and reasoning |

#### listing_service.py (Module 5)

| Method | What It Does | Calls |
|--------|-------------|-------|
| `publish_from_draft()` | **ATOMIC operation**: lock draft → check KYC verified → check not suspended → count active < 5 → fetch fresh floor price → validate ask_price > floor → create listing → mark draft published → move photos → emit event → send SMS | draft_repo, seller_repo, listing_repo, photo_repo, price_client, event_bus, notification |
| `edit_price()` | Check max 3 edits → re-fetch floor price → validate → update | listing_repo, price_client |
| `pause_listing()` | Check state machine allows active→paused → update status | listing_repo, state_machine |
| `resume_listing()` | Check state machine allows paused→active → update | listing_repo, state_machine |
| `cancel_listing()` | Transition to cancelled → increment seller cancel count → if 3+ cancels, suspend seller 30 days | listing_repo, seller_repo, event_bus |
| `expire_listing()` | Transition to expired → emit event → send SMS | listing_repo, event_bus, notification |
| `get_public_listing()` | Returns listing WITHOUT seller_id (PII protected) → increments view count | listing_repo |
| `list_my_listings()` | Paginated list with optional status filter | listing_repo |

#### analytics_service.py (Module 6)

| Method | What It Does | Calls |
|--------|-------------|-------|
| `get_season_summary()` | Returns earnings summary for current/specified season (Kharif Jun-Oct, Rabi Nov-Mar, Zaid Apr-May) | season_repo |
| `get_earnings_history()` | All seasons + all-time totals | season_repo |
| `compare_with_mandi()` | Your price vs mandi modal price → verdict: above/below/at_mandi | listing_repo, price_client |
| `get_listing_analytics()` | Views, enquiries, time-to-match, price competitiveness for one listing | listing_repo, price_client |
| `get_dashboard()` | Combined: active listings count + season earnings + pending drafts | listing_repo, season_repo, draft_repo |
| `refresh_season_summary()` | Recalculates from sold listings: total earnings, commission, best crop, avg grade | listing_repo, season_repo, validators |

#### completeness_service.py

| Method | What It Does | Used By |
|--------|-------------|---------|
| `calculate_score()` | Weighted score 0-100: step1=25, step2=25, step3=20, step4=15, step5=15 | draft_service |
| `get_missing_required()` | Returns list like ["step2.photo_urls", "step5.consent_terms"] | draft_service |
| `get_step_completion()` | Returns {"step1": true, "step2": false, ...} | draft_service |
| `get_completion_message()` | Bilingual message based on score: "Making progress" / "పురోగతి" | draft_service |

---

### app/clients/ — External Service Connectors

| File | Connects To | Mock Mode |
|------|------------|-----------|
| `price_client.py` | Price Service (port 8006) via HTTP | When `ENABLE_REAL_PRICE_DATA=false`: returns preset prices per crop (tomato=₹1240, chilli_dry=₹8500, etc.) |
| `event_bus_client.py` | Redis pub/sub channel `seller-service-events` | When ENV=test or no Redis: just logs the event |
| `notification_client.py` | Notification Service (port 8007) via HTTP | When `ENABLE_NOTIFICATIONS=false`: just logs "MOCK SMS to seller" |
| `supabase_client.py` | Supabase Storage for photo uploads | Returns mock URLs like `https://mock-storage.supabase.co/...` |
| `razorpay_client.py` | Razorpay payment gateway | Stub — not implemented yet |
| `uidai_client.py` | UIDAI API for Aadhaar verification | Stub — not implemented yet |

---

### app/api/ — HTTP Layer

| File | What It Does |
|------|-------------|
| `deps.py` | `get_current_seller()`: extracts JWT from `Authorization: Bearer <token>` header → decodes → looks up seller. `require_kyc_verified()`: same + checks KYC status is "verified" and not suspended |
| `exceptions_handler.py` | Catches all errors: KisanGPTException → 4xx with bilingual message, ValidationError → 422, generic Exception → 500 |

---

### app/jobs/ — Background Tasks (APScheduler)

| File | Schedule | What It Does |
|------|----------|-------------|
| `draft_cleanup_job.py` | Daily 2 AM IST | Warns 7-day inactive drafts → abandons 14-day → deletes 30-day |
| `listing_expiry_job.py` | Every 30 min | Finds active listings past expires_at → transitions to expired → sends SMS |
| `season_summary_job.py` | Daily 3 AM IST | Refreshes season summary for all active sellers |
| `scheduler.py` | On app start | Registers all 3 jobs with CronTrigger |

---

### tests/ — Test Files

| File | What It Tests | # Tests |
|------|--------------|---------|
| `conftest.py` | Shared fixtures: sample_seller_id, verified_seller_data, complete_draft_data | fixtures |
| `fixtures/mock_responses.py` | Mock data for Claude/Gemini responses, seller objects, listing objects | test data |

---

## 3. How to Test Every Function

### A. Run ALL tests at once

```bash
cd seller-service
pytest -v
```

Output: `169 passed`

---

### B. Test each module individually

#### Module 3 — Draft

```bash
# Unit tests (pure logic — no mocks needed)
pytest tests/unit/test_completeness.py -v       # 19 tests — completeness scoring
pytest tests/unit/test_validators.py -v          # 30 tests — crop, quantity, floor price

# Integration tests (mocked DB)
pytest tests/integration/test_draft_flow.py -v   # 11 tests — full draft lifecycle
```

**What these test:**
```
test_completeness.py:
  ✓ Empty draft → score 0
  ✓ Step 1 only → score 25
  ✓ Full draft → score 100
  ✓ Missing photos reduces step 2 score
  ✓ Bilingual completion messages

test_draft_flow.py:
  ✓ Create draft succeeds
  ✓ Max 3 drafts limit enforced
  ✓ Invalid crop "cotton" rejected
  ✓ Save step increments completeness
  ✓ Wrong owner can't edit
  ✓ Published draft can't be edited
  ✓ Soft delete works
  ✓ Clone copies steps 1,3,4 but NOT step 5
  ✓ Price staleness detected after 30 min
  ✓ Fresh price not marked stale
```

---

#### Module 4 — AI Grading

```bash
pytest tests/integration/test_ai_grading.py -v   # 7 tests
```

**What these test:**
```
  ✓ Claude returns valid grade A with confidence 85
  ✓ When Claude fails → Gemini fallback works
  ✓ When both fail → manual fallback returned
  ✓ Confidence 40 → low_confidence_warning = true
  ✓ Confidence 60 → low_confidence_warning = false
  ✓ Grading result is logged to ai_grading_log table
  ✓ Duplicate photo (same perceptual hash) rejected
```

---

#### Module 5 — Listing Publish & Management

```bash
# Unit tests
pytest tests/unit/test_state_machine.py -v       # 18 tests — status transitions
pytest tests/unit/test_payout_calc.py -v          # 8 tests — commission calculation

# Integration tests
pytest tests/integration/test_publish_flow.py -v  # 11 tests — full publish lifecycle
pytest tests/integration/test_listing_flow.py -v  # 4 tests — public view, pagination
```

**What these test:**
```
test_state_machine.py:
  ✓ active → paused allowed
  ✓ active → matched allowed
  ✓ sold → anything BLOCKED
  ✓ expired → anything BLOCKED
  ✓ cancelled → anything BLOCKED
  ✓ active → sold INVALID (must go through matched first)

test_payout_calc.py:
  ✓ 500kg tier1 → 3% commission
  ✓ 800kg tier2 → 5% commission
  ✓ 5000kg tier3 → 8% commission
  ✓ Boundary: 2000kg → tier2, 2001kg → tier3

test_publish_flow.py:
  ✓ Happy path publish works end-to-end
  ✓ Price below floor → BLOCKED
  ✓ KYC not verified → BLOCKED
  ✓ Already 5 active listings → BLOCKED
  ✓ Already published draft → BLOCKED
  ✓ Price edit within 3 limit works
  ✓ 4th price edit → BLOCKED
  ✓ Cancel increments count
  ✓ 3rd cancellation → seller suspended 30 days
  ✓ Pause and resume cycle works
  ✓ Expired listing cannot resume

test_listing_flow.py:
  ✓ Public view has NO seller_id (PII protected)
  ✓ Pagination returns correct page/total
  ✓ Status filter returns only active listings
  ✓ Publish emits "listing.published" event
```

---

#### Module 6 — Analytics

No dedicated test file yet. To test:

```bash
# The analytics functions use the same validators and repos
pytest tests/unit/test_payout_calc.py -v    # Commission calc used by analytics
pytest tests/unit/test_constants.py -v      # Constants used everywhere
```

---

#### Security

```bash
pytest tests/unit/test_security.py -v    # 12 tests
```

**What these test:**
```
  ✓ Password hash is not plaintext
  ✓ Correct password verifies true
  ✓ Wrong password verifies false
  ✓ JWT roundtrip: create → decode → same seller_id
  ✓ Expired JWT raises error
  ✓ Invalid JWT raises error
  ✓ Aadhaar hash is consistent (same input → same hash)
  ✓ Different Aadhaar → different hash
  ✓ Hash is 64 chars (SHA-256)
  ✓ Hash is hex only
```

---

#### Constants

```bash
pytest tests/unit/test_constants.py -v    # 22 tests
```

**What these test:**
```
  ✓ Phase 1 has exactly 4 crops
  ✓ Phase 1 has exactly 2 districts (kurnool, nandyal)
  ✓ MIN_QUANTITY = 100kg, MAX_QUANTITY = 25000kg
  ✓ MAX_ACTIVE_LISTINGS = 5
  ✓ MAX_PRICE_EDITS = 3
  ✓ Commission tiers: 3%, 5%, 8%
  ✓ AI confidence threshold = 60
  ✓ Draft staleness = 30 minutes
  ✓ Photo limits: min 3, max 5, max size 5MB
```

---

### C. Test a single specific function

```bash
# Test ONLY floor price calculation
pytest tests/unit/test_validators.py::TestFloorPrice -v

# Test ONLY the JWT roundtrip
pytest tests/unit/test_security.py::TestJWT::test_roundtrip -v

# Test ONLY the publish happy path
pytest tests/integration/test_publish_flow.py::TestPublishFromDraft::test_happy_path -v

# Test ONLY 3-cancellation suspension
pytest tests/integration/test_publish_flow.py::TestCancelListing::test_3_cancellations_suspends -v
```

---

### D. Test with print output (see what's happening)

```bash
pytest tests/integration/test_publish_flow.py -v -s
```

The `-s` flag shows all print/log output so you can trace execution.

---

### E. Test with coverage report

```bash
pytest --cov=app --cov-report=term-missing
```

This shows which lines of code are NOT covered by tests.

---

## 4. Connection Map Between Files

### How `POST /api/v1/drafts` flows through the code:

```
1. Farmer sends: POST /api/v1/drafts
   Body: {"step1": {"crop": "tomato", "quantity_kg": 800, "harvest_status": "harvested_today"}}
   Header: Authorization: Bearer <jwt_token>

2. app/api/v1/draft_router.py :: create_draft()
   → Calls Depends(require_kyc_verified) → gets seller object
   → Calls Depends(get_db) → gets DB session
   → Calls DraftController.create_draft(step1_data, seller, db)

3. app/controllers/draft_controller.py :: create_draft()
   → Creates DraftService(db)
   → Calls svc.create_draft(seller.id, step1_data)
   → Wraps result in StandardResponse(success=True, data=...)

4. app/services/draft_service.py :: create_draft()
   → Calls self.repo.count_drafts_by_seller(seller_id)
     → If count >= 3, raises MaxDraftsReachedError
   → Calls validate_crop("tomato")
     → Checks if "tomato" is in PHASE1_CROPS set
   → Calls validate_quantity(800, "tomato")
     → Checks 100 ≤ 800 ≤ 25000
   → Calls self.repo.create_draft(seller_id, {"step1_data": {...}})
   → Calls CompletenessService.calculate_score(draft_dict)
     → Returns 25 (step1 filled = 25% weight)
   → Calls self.repo.update_draft(draft.id, {completeness_score: 25})
   → Returns response dict

5. app/repositories/draft_repo.py :: create_draft()
   → INSERT INTO listing_drafts (id, seller_id, step1_data, ...) VALUES (...)
   → Returns ListingDraft ORM object

6. Response back to farmer:
   {
     "success": true,
     "message": "Draft created.",
     "data": {
       "id": "abc-123",
       "completeness_score": 25,
       "step1_data": {"crop": "tomato", "quantity_kg": 800},
       "missing_fields": ["step2.photo_urls", "step2.grade", ...],
       "price_stale": false
     }
   }
```

---

### How `POST /api/v1/drafts/{id}/publish` flows:

```
1. Farmer sends: POST /api/v1/drafts/{draft_id}/publish
   Body: {"ask_price_per_q": 1200}

2. listing_router.py → ListingController → ListingService.publish_from_draft()

3. ListingService.publish_from_draft():
   ┌─── draft_repo.get_draft_for_update(draft_id) ← Locks row for atomic update
   │    └── Check: not already published
   │
   ├─── seller_repo.get_for_update(seller_id) ← Locks seller row
   │    ├── Check: kyc_status == "verified"
   │    └── Check: suspension_until is null or in past
   │
   ├─── listing_repo.count_active_listings(seller_id)
   │    └── Check: count < 5
   │
   ├─── price_client.get_floor_price("tomato", "kurnool")
   │    └── Returns: {modal_price: 1240, floor_price: 1054}
   │
   ├─── validate_floor_price(1200, 1054, 1240)
   │    └── 1200 >= 1054 → PASS (if 900, would raise FloorPriceViolationError)
   │
   ├─── listing_repo.create_from_draft(draft, publish_data, floor, modal)
   │    └── INSERT INTO listings with generated listing_number "KGP-20260613-4821"
   │
   ├─── draft_repo.mark_published(draft_id, listing.id)
   │    └── UPDATE listing_drafts SET draft_status='published', published_listing_id=...
   │
   ├─── photo_repo.update_listing_id(draft_id, listing.id)
   │    └── UPDATE listing_photos SET listing_id=... WHERE listing_draft_id=...
   │
   ├─── event_bus.emit_event("listing.published", {...})
   │    └── PUBLISH to Redis channel "seller-service-events"
   │
   └─── notification.send_sms(seller_id, "listing_published", {...})
        └── HTTP POST to notification service (or mock log)
```

---

### How AI Grading flows:

```
POST /api/v1/drafts/{id}/grade
    │
    ▼
PhotoService.trigger_grading()
    │
    ├── Get draft → verify ownership
    ├── Get photos from DB (need ≥3)
    ├── Update step2_data.grading_status = "processing"
    │
    ▼
AIGradingRouter.grade(photo_urls, crop)
    │
    ├── TRY: ClaudeGradingService.grade_photos()
    │   ├── Build crop-specific prompt from prompts.py
    │   ├── Call Anthropic API: claude-sonnet-4-20250514
    │   ├── Send 3 photos as image URLs
    │   ├── Parse JSON response → grade, confidence
    │   └── Return: {grade: "A", confidence: 85, ai_provider: "claude"}
    │
    ├── CATCH AIGradingError → FALLBACK:
    │   ├── GeminiGradingService.grade_photos()
    │   │   ├── Call Google Gemini API
    │   │   └── Return: {grade: "B", confidence: 72, ai_provider: "gemini"}
    │   │
    │   └── CATCH AIGradingError → MANUAL FALLBACK:
    │       └── Return: {grade: null, ai_provider: "manual", requires_manual_grading: true}
    │
    ├── Add low_confidence_warning: true if confidence < 60
    │
    ▼
Back in PhotoService:
    ├── ai_log_repo.create_log() → INSERT INTO ai_grading_log
    ├── Update draft step2_data with grade + confidence
    └── Return grading result
```

---

### How Cancel + Suspension flows:

```
POST /api/v1/listings/{id}/cancel
Body: {"reason": "Changed my mind"}

ListingService.cancel_listing():
    │
    ├── Get listing → verify ownership
    ├── state_machine.transition_listing("active" → "cancelled") ← validates
    ├── listing_repo.update_listing_status(id, "cancelled", cancelled_at=now)
    │
    ├── seller_repo.get_for_update(seller_id) ← lock seller row
    ├── new_count = seller.cancellation_count + 1
    ├── seller_repo.update_cancellation_count(seller_id, new_count)
    │
    ├── IF new_count >= 3:
    │   └── seller_repo.suspend_seller(seller_id, now + 30 days)
    │       └── UPDATE sellers SET suspension_until = '2026-07-13'
    │       └── Seller CANNOT publish new listings for 30 days
    │
    └── event_bus.emit_event("listing.cancelled", {...})
```

---

### How Season Detection works:

```python
Month 1-3  (Jan-Mar)  → Rabi season of PREVIOUS year
Month 4-5  (Apr-May)  → Zaid season of current year
Month 6-10 (Jun-Oct)  → Kharif season of current year
Month 11-12 (Nov-Dec) → Rabi season of current year

Example: June 2026 → "kharif_2026"
Example: February 2026 → "rabi_2025"
```

---

### How Price Staleness works:

```
When farmer opens draft with step3 data (pricing):
  1. Check step3_data.price_fetched_at timestamp
  2. If (now - fetched_at) > 30 minutes:
     → price_stale: true in response
     → Frontend should prompt farmer to refresh price
  3. This prevents publishing with outdated mandi prices
```

---

### Inter-Service Communication:

```
┌────────────────────┐     HTTP (port 8006)     ┌──────────────────┐
│  Seller Service    │ ◄──────────────────────► │  Price Service   │
│  (this service)    │     get_floor_price()     │  (separate)      │
│  port 8001         │                          │  Mandi data      │
└────────┬───────────┘                          └──────────────────┘
         │
         │  Redis pub/sub
         │  "seller-service-events"
         ▼
┌────────────────────┐     HTTP (port 8007)     ┌──────────────────┐
│  Redis 7           │                          │  Notification    │
│  Event Bus         │ ◄───────────────────────►│  Service         │
│  port 6379         │                          │  SMS/WhatsApp    │
└────────────────────┘                          └──────────────────┘
         │
         │  Events emitted:
         │  - listing.published
         │  - listing.price_edited
         │  - listing.cancelled
         │  - listing.expired
         │
         ▼
┌────────────────────┐
│  Supabase Storage  │  Photo upload
│  (cloud)           │  sellers/{id}/drafts/{id}/lot_view.jpg
└────────────────────┘
```

**Currently in mock mode** (all clients return fake data when ENABLE_*=false). When you connect real services, just set the env vars:
- `ENABLE_REAL_PRICE_DATA=true` + `PRICE_SERVICE_URL=http://...`
- `ENABLE_NOTIFICATIONS=true` + `NOTIFICATION_SERVICE_URL=http://...`
- `ENABLE_AI_GRADING=true` + `ANTHROPIC_API_KEY=sk-ant-...`
