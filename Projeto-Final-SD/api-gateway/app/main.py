from fastapi import FastAPI
import httpx
import asyncio
import time

app = FastAPI(title="API Gateway")

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
        return {"service": url, "status": "offline", "error": str(e)}

@app.get("/api/health")
async def health():
    return {"services": await asyncio.gather(*[check_service(s) for s in SERVICES])}

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
        r = await client.get(f"{LOGS_URL}/logs", params={"service": service})
        r.raise_for_status()
        return r.json()

# ---------------- METRICS ----------------
@app.get("/api/metrics/summary")
async def metrics_summary():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{METRICAS_URL}/summary")
        r.raise_for_status()
        return r.json()
