FROM python:3.11-slim as builder

WORKDIR /build
RUN pip install poetry==1.8.3
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

FROM python:3.11-slim

WORKDIR /app
RUN adduser --disabled-password --gecos "" appuser

COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8001/health').raise_for_status()"

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
