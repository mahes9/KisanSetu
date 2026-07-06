FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install poetry==1.8.5 && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt || \
    echo "No lock file, skipping export"

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir \
    fastapi[standard] uvicorn sqlalchemy[asyncio] asyncpg \
    pydantic pydantic-settings python-jose[cryptography] \
    passlib[bcrypt] httpx redis alembic

COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
