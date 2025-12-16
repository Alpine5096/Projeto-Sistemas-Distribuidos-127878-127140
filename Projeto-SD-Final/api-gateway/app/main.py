from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx
import asyncio
import time

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

app = FastAPI(title="API Gateway")

# ---------------- PROMETHEUS METRICS ----------------

REQUESTS_TOTAL = Counter(
    "api_gateway_requests_total",
    "Total de requests recebidas no API Gateway",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "api_gateway_request_duration_seconds",
    "Latência dos requests no API Gateway",
    ["method", "path"]
)

# ---------------- SERVICES ----------------

ORDERS_URL = "http://orders:5001"
PAYMENTS_URL = "http://payments:5002"
LOGS_URL = "http://logs:5003"
NOTIFICATIONS_URL = "http://notifications:5004"
METRICAS_URL = "http://metricas:5005"

SERVICES = [
    ORDERS_URL,
    PAYMENTS_URL,
    LOGS_URL,
    NOTIFICATIONS_URL,
    METRICAS_URL,
]

# ---------------- MIDDLEWARE ----------------

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    REQUESTS_TOTAL.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)

    return response

# ---------------- HEALTH ----------------

async def check_service(url: str):
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            start = time.perf_counter()
            r = await client.get(f"{url}/health")
            latency = int((time.perf_counter() - start) * 1000)
            return {
                "service": url,
                "status": "online" if r.status_code == 200 else "degraded",
                "latency_ms": latency,
            }
    except Exception as e:
        return {
            "service": url,
            "status": "offline",
            "error": str(e)
        }

@app.get("/api/health")
async def health():
    return {
        "services": await asyncio.gather(
            *[check_service(s) for s in SERVICES]
        )
    }

# ---------------- ORDERS ----------------

@app.get("/api/orders/list")
async def list_orders():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{ORDERS_URL}/orders")
        r.raise_for_status()
        return r.json()

@app.post("/api/orders/create")
async def create_order(payload: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ORDERS_URL}/orders", json=payload)
        r.raise_for_status()
        return r.json()

# Alias para simplificar testes e demonstração
@app.post("/api/orders")
async def create_order_alias(payload: dict):
    return await create_order(payload)

# ---------------- PAYMENTS ----------------

@app.get("/api/payments/list")
async def list_payments():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{PAYMENTS_URL}/payments")
        r.raise_for_status()
        return r.json()

# ---------------- NOTIFICATIONS ----------------

@app.get("/api/notifications/list")
async def list_notifications():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{NOTIFICATIONS_URL}/notifications")
        r.raise_for_status()
        return r.json()

# ---------------- LOGS ----------------

@app.get("/api/logs")
async def get_logs(service: str = "all"):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{LOGS_URL}/logs",
            params={"service": service}
        )
        r.raise_for_status()
        return r.json()

# ---------------- METRICAS ----------------

@app.get("/api/metrics/summary")
async def metrics_summary():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{METRICAS_URL}/summary")
        r.raise_for_status()
        return r.json()

# ---------------- PROMETHEUS ENDPOINT ----------------

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
