# KisanSetu Seller Service — Developer Guide

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Local Setup from Scratch](#2-local-setup-from-scratch)
3. [Running the Service](#3-running-the-service)
4. [Database Setup & Migrations](#4-database-setup--migrations)
5. [Running Tests](#5-running-tests)
6. [Exploring the API (Swagger UI)](#6-exploring-the-api-swagger-ui)
7. [How to Showcase the Project](#7-how-to-showcase-the-project)
8. [Project Architecture Explained](#8-project-architecture-explained)
9. [Adding New Functionality](#9-adding-new-functionality)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview

KisanSetu Seller Service is a **Python FastAPI microservice** that handles:

| Module | What It Does |
|--------|-------------|
| Module 3 | Listing Draft — 5-step wizard for farmers to create crop listings |
| Module 4 | AI Grading — Claude (primary) → Gemini (fallback) grades crop photos A/B/C |
| Module 5 | Listing Publish & Management — publish, pause, cancel, edit price |
| Module 6 | Season Summary & Analytics — earnings, mandi comparison, dashboard |

**Tech Stack:** Python 3.11 · FastAPI · SQLAlchemy 2.0 async · PostgreSQL 16 · Redis 7 · Pydantic v2

---

## 2. Local Setup from Scratch

### Prerequisites

Install these before starting:

- [Python 3.11+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Postgres + Redis)
- [Git](https://git-scm.com/)

### Step 1 — Clone the repository

```bash
git clone https://github.com/mahes9/KisanSetu.git
cd KisanSetu/seller-service
```

### Step 2 — Create a virtual environment

```bash
python -m venv .venv

# On Mac/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -e ".[dev]"
```

### Step 4 — Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and update these values (minimum needed for local testing):

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/kisangpt_seller
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=my-local-dev-secret-key-change-in-production
ENABLE_AI_GRADING=false       # keep false until you add real API keys
ENABLE_NOTIFICATIONS=false
ENABLE_REAL_PRICE_DATA=false
```

> For real AI grading, set `ANTHROPIC_API_KEY` and `ENABLE_AI_GRADING=true`

### Step 5 — Start Postgres and Redis with Docker

```bash
docker-compose up postgres redis -d
```

Verify they are running:
```bash
docker ps
# You should see: postgres:16-alpine and redis:7-alpine
```

---

## 3. Running the Service

### Option A — Run directly (for development)

```bash
uvicorn main:app --reload --port 8001
```

You will see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Option B — Run with Docker Compose (full stack)

```bash
docker-compose up --build
```

This starts Postgres + Redis + the seller-service together.

### Verify the service is running

Open your browser or run:
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "seller-service",
  "version": "1.0.0"
}
```

---

## 4. Database Setup & Migrations

### Create the database tables

After starting the service (or separately), run Alembic to create all 9 tables:

```bash
# Generate migration from your models
alembic revision --autogenerate -m "initial schema"

# Apply migration to database
alembic upgrade head
```

You should see output like:
```
Running upgrade  -> abc123, initial schema
```

### Verify tables were created

Connect to Postgres and check:
```bash
docker exec -it kisansetu-postgres-1 psql -U postgres -d kisangpt_seller -c "\dt"
```

Expected tables:
```
 sellers
 farms
 listing_drafts
 draft_save_log
 listing_photos
 ai_grading_log
 listings
 price_snapshots_cache
 season_summaries
```

### Seed test data (optional)

```bash
python -c "import asyncio; from app.db.seed import seed_db; asyncio.run(seed_db())"
```

This creates 3 test sellers:
- `9000000001` — KYC verified (use this for testing)
- `9000000002` — KYC pending
- `9000000003` — Suspended seller

---

## 5. Running Tests

### Run all tests

```bash
pytest
```

Expected output:
```
169 passed in X.XXs
```

### Run only unit tests (fast, no mocks needed)

```bash
pytest tests/unit/ -v
```

### Run only integration tests

```bash
pytest tests/integration/ -v
```

### Run a specific test file

```bash
pytest tests/integration/test_publish_flow.py -v
```

### Run a specific test by name

```bash
pytest tests/unit/test_validators.py::TestFloorPrice::test_1240_gives_1054 -v
```

### Run with coverage report

```bash
pytest --cov=app --cov-report=term-missing
```

### What each test folder tests

| Folder | Tests | What It Covers |
|--------|-------|---------------|
| `tests/unit/test_validators.py` | 30 tests | Crop validation, floor price, quantity limits |
| `tests/unit/test_payout_calc.py` | 8 tests | Commission tiers (3%, 5%, 8%) |
| `tests/unit/test_completeness.py` | 19 tests | Draft completeness scoring (0-100) |
| `tests/unit/test_state_machine.py` | 18 tests | Listing status transitions |
| `tests/unit/test_security.py` | 12 tests | JWT, bcrypt, Aadhaar hashing |
| `tests/unit/test_constants.py` | 22 tests | All config constants verified |
| `tests/integration/test_draft_flow.py` | 11 tests | Create/save/clone/delete draft |
| `tests/integration/test_ai_grading.py` | 7 tests | Claude→Gemini→Manual fallback |
| `tests/integration/test_publish_flow.py` | 11 tests | Publish, price edit, cancel |
| `tests/integration/test_listing_flow.py` | 4 tests | Public view, pagination, events |

---

## 6. Exploring the API (Swagger UI)

Once the service is running, open:

```
http://localhost:8001/docs
```

This shows the **interactive Swagger UI** with all 30+ API endpoints.

### How to test an API endpoint in Swagger:

1. Click on any endpoint (e.g. `POST /api/v1/drafts`)
2. Click **"Try it out"**
3. Fill in the JSON body
4. Click **"Execute"**
5. See the response below

### For authenticated endpoints:

Most endpoints require a JWT token. To get one:

1. First call `POST /api/v1/auth/send-otp` with a phone number
2. Then `POST /api/v1/auth/verify-otp` — this returns a `token`
3. Click **"Authorize"** button (top right of Swagger)
4. Enter: `Bearer <your-token>`
5. Now all authenticated endpoints work

> **Quick hack for testing:** Since auth is a stub (Module 1-2 not built yet), you can temporarily bypass JWT by editing `app/api/deps.py` and returning a fixed seller_id.

### Key API endpoints to demo:

```
POST   /api/v1/drafts                      Create a new draft
POST   /api/v1/drafts/{id}/step/{n}        Save a step (1-5)
POST   /api/v1/drafts/{id}/photos          Upload 3 photos
POST   /api/v1/drafts/{id}/grade           Trigger AI grading
GET    /api/v1/drafts/{id}/grade           Get grading status
POST   /api/v1/drafts/{id}/publish         Publish listing
GET    /api/v1/listings                    List my listings
GET    /api/v1/listings/{id}/public        Public view (no PII)
PATCH  /api/v1/listings/{id}/price         Edit price
POST   /api/v1/listings/{id}/pause         Pause listing
POST   /api/v1/listings/{id}/cancel        Cancel listing
GET    /api/v1/analytics/dashboard         Full dashboard
GET    /api/v1/analytics/season-summary    Season earnings
GET    /api/v1/analytics/mandi-comparison  vs Mandi prices
```

---

## 7. How to Showcase the Project

### Demo Flow (end-to-end in 10 minutes)

Follow these steps in order to show the complete farmer journey:

#### Step 1 — Create a Draft

```bash
curl -X POST http://localhost:8001/api/v1/drafts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "crop": "tomato",
    "quantity_kg": 800,
    "harvest_status": "harvested_today"
  }'
```

**Show:** Draft created with `completeness_score: 25`

---

#### Step 2 — Save Step 3 (Pricing)

```bash
curl -X POST http://localhost:8001/api/v1/drafts/{draft_id}/step/3 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "ask_price_per_q": 1200
  }'
```

**Show:** Completeness increases. Price staleness detection after 30 mins.

---

#### Step 3 — Trigger AI Grading

```bash
curl -X POST http://localhost:8001/api/v1/drafts/{draft_id}/grade \
  -H "Authorization: Bearer <token>"
```

**Show:** With `ENABLE_AI_GRADING=false` it uses mock data. With real API key it calls Claude.

**Talking point:** Claude primary → Gemini fallback → Manual fallback chain.

---

#### Step 4 — Publish the Listing

```bash
curl -X POST http://localhost:8001/api/v1/drafts/{draft_id}/publish \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"ask_price_per_q": 1200}'
```

**Show:**
- Returns `listing_number` like `KGP-20260610-4821`
- Shows `floor_price_at_publish` (85% of mandi modal)
- Shows `payout_preview` with commission deducted

---

#### Step 5 — Show Public Listing (No PII)

```bash
curl http://localhost:8001/api/v1/listings/{listing_id}/public
```

**Show:** Response has NO `seller_id`, NO phone, NO name — privacy protected.

---

#### Step 6 — Show Analytics Dashboard

```bash
curl http://localhost:8001/api/v1/analytics/dashboard \
  -H "Authorization: Bearer <token>"
```

**Show:** Season summary, total earnings, mandi comparison verdict.

---

### What to highlight when showcasing

| Feature | What to Say |
|---------|------------|
| AI Grading | "Claude grades A/B/C from 3 photos. If Claude fails, Gemini takes over automatically. No manual intervention needed." |
| Floor Price | "Farmer can never sell below 85% of mandi price. Protects farmers from distress selling." |
| Bilingual Errors | "Every error has English + Telugu translation built in. Ready for rural farmers." |
| Commission Tiers | "3% for small farmers (≤500kg), 5% mid (≤2000kg), 8% large (>2000kg)." |
| State Machine | "Listings follow strict rules — can't resume an expired listing, can't unsell a sold one." |
| Public View | "Buyer-facing API strips all PII. Farmer's identity is protected." |
| 169 Tests | "Every business rule has a test. Show the test run with `pytest`." |

---

## 8. Project Architecture Explained

### Layered Architecture (Request Flow)

```
HTTP Request
    ↓
Router (app/api/v1/*.py)
    → Validates HTTP, extracts JWT, calls Controller
    ↓
Controller (app/controllers/*.py)
    → Thin layer, just calls Service
    ↓
Service (app/services/*.py)
    → ALL business logic lives here
    → Calls Repository for DB, Clients for external APIs
    ↓
Repository (app/repositories/*.py)
    → All SQLAlchemy queries
    → Returns ORM models
    ↓
Database (PostgreSQL via asyncpg)
```

### Why this structure?

- **Router** — only knows about HTTP (status codes, auth headers)
- **Controller** — only knows about request/response shapes
- **Service** — knows about business rules, has no HTTP knowledge
- **Repository** — only knows about SQL, no business logic
- **Model** — only knows about DB columns

This means: **to change a business rule, you only touch the Service. To change a DB schema, you only touch the Model + Repository.**

### Key files to know

| File | Purpose |
|------|---------|
| `app/core/exceptions.py` | All 30 custom errors with EN + Telugu |
| `app/core/validators.py` | Floor price, crop validation, commission calc |
| `app/core/state_machine.py` | Listing status transition rules |
| `app/core/constants.py` | All business constants (crops, tiers, limits) |
| `app/services/listing_service.py` | Most complex — atomic publish flow |
| `app/services/ai_service/ai_router.py` | Claude→Gemini→Manual fallback chain |
| `app/services/draft_service.py` | 5-step wizard logic |

---

## 9. Adding New Functionality

### Example A — Add a new API endpoint

**Goal:** Add `GET /api/v1/listings/{id}/payout-preview`

**Step 1 — Add the schema** (`app/schemas/listing_schema.py`):
```python
class PayoutPreviewResponse(BaseModel):
    gross_amount: float
    commission_percent: float
    commission_amount: float
    net_payout: float
    effective_price_per_kg: float
```

**Step 2 — Add the service method** (`app/services/listing_service.py`):
```python
async def get_payout_preview(self, listing_id: UUID, seller_id: UUID) -> dict:
    listing = await self.listing_repo.get_listing_by_id(listing_id)
    if listing.seller_id != seller_id:
        raise ListingNotFoundError()
    return calculate_payout_preview(listing.quantity_kg, listing.ask_price_per_q)
```

**Step 3 — Add the controller method** (`app/controllers/listing_controller.py`):
```python
@staticmethod
async def get_payout_preview(listing_id: UUID, seller_id: UUID, session) -> dict:
    svc = ListingService(session)
    return await svc.get_payout_preview(listing_id, seller_id)
```

**Step 4 — Add the route** (`app/api/v1/listing_router.py`):
```python
@router.get("/{listing_id}/payout-preview", response_model=PayoutPreviewResponse)
async def get_payout_preview(
    listing_id: UUID,
    seller=Depends(get_current_seller),
    session=Depends(get_db),
):
    return await ListingController.get_payout_preview(listing_id, seller.id, session)
```

**Step 5 — Add a test** (`tests/unit/test_payout_calc.py` or new integration test).

**Step 6 — Run tests** to make sure nothing broke:
```bash
pytest
```

---

### Example B — Add a new DB column

**Goal:** Add `featured: bool` column to `listings` table

**Step 1 — Update the model** (`app/models/listing.py`):
```python
featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

**Step 2 — Generate a migration**:
```bash
alembic revision --autogenerate -m "add featured column to listings"
```

**Step 3 — Apply it**:
```bash
alembic upgrade head
```

**Step 4 — Update the schema** if you want it in API responses (`app/schemas/listing_schema.py`):
```python
class ListingResponse(BaseModel):
    # ... existing fields ...
    featured: bool
```

**Step 5 — Update the repository** if you need to query by it (`app/repositories/listing_repo.py`):
```python
async def get_featured_listings(self) -> list[Listing]:
    result = await self.session.execute(
        select(Listing).where(Listing.featured == True, Listing.status == "active")
    )
    return result.scalars().all()
```

---

### Example C — Add a new exception

**Goal:** Add `ListingAlreadyFeaturedError`

In `app/core/exceptions.py`:
```python
class ListingAlreadyFeaturedError(KisanGPTException):
    def __init__(self):
        super().__init__(
            error_code="E031",
            message_en="This listing is already featured",
            message_te="ఈ లిస్టింగ్ ఇప్పటికే ఫీచర్ చేయబడింది",
            http_status=400,
        )
```

---

### Example D — Add a new background job

**Goal:** Send reminders for drafts inactive for 5 days

**Step 1 — Create the job** (`app/jobs/draft_reminder_job.py`):
```python
async def run_draft_reminders():
    async with SessionLocal() as session:
        repo = DraftRepository(session)
        stale = await repo.get_stale_drafts(days=5)
        for draft in stale:
            # send notification
            pass
```

**Step 2 — Register in scheduler** (`app/jobs/scheduler.py`):
```python
from app.jobs.draft_reminder_job import run_draft_reminders

scheduler.add_job(
    run_draft_reminders,
    CronTrigger(hour=10, minute=0, timezone="Asia/Kolkata"),
    id="draft_reminders",
)
```

---

### Example E — Add a new crop (Phase 2)

In `app/core/constants.py`:
```python
PHASE1_CROPS: set[str] = {
    "tomato",
    "chilli_dry",
    "chilli_green",
    "groundnut",
    "onion",        # ← add here
}
```

In `app/services/ai_service/prompts.py`, add a grading prompt for the new crop:
```python
ONION_GRADING_PROMPT = """
You are an expert agricultural grader specializing in onion quality assessment...
"""
```

---

## 10. Troubleshooting

### Service won't start — "Database connection refused"

```bash
# Make sure Docker is running
docker ps

# Start just the databases
docker-compose up postgres redis -d

# Wait 5 seconds then try again
```

### Tests fail — "ModuleNotFoundError: No module named 'app'"

```bash
# Make sure you installed the package in editable mode
pip install -e ".[dev]"

# Run from the seller-service directory
cd seller-service
pytest
```

### Alembic error — "Can't locate revision"

```bash
# Reset and regenerate
alembic downgrade base
alembic revision --autogenerate -m "fresh schema"
alembic upgrade head
```

### JWT token expired during testing

Tokens expire after 7 days by default. Generate a new one via `/api/v1/auth/verify-otp` or increase `JWT_EXPIRY_DAYS` in `.env`.

### AI grading returns mock data

This is expected when `ENABLE_AI_GRADING=false`. To use real AI:
1. Add your `ANTHROPIC_API_KEY` to `.env`
2. Set `ENABLE_AI_GRADING=true`
3. Restart the service

### Port 8001 already in use

```bash
# Find what's using it
lsof -i :8001

# Kill it
kill -9 <PID>

# Or run on a different port
uvicorn main:app --reload --port 8002
```

---

## Quick Reference Card

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Start infrastructure
docker-compose up postgres redis -d

# Run migrations
alembic revision --autogenerate -m "init"
alembic upgrade head

# Seed test data
python -c "import asyncio; from app.db.seed import seed_db; asyncio.run(seed_db())"

# Start service
uvicorn main:app --reload --port 8001

# Open API docs
open http://localhost:8001/docs

# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Check health
curl http://localhost:8001/health
```
