from fastapi import FastAPI
import os, httpx, asyncio, time, json

app = FastAPI(title="API Gateway")

SERVICES = os.getenv("SERVICES_LIST", "").split(",")

# --- health check existing (assume presente) ---
async def check_service(url: str):
    import httpx, time
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            t0 = time.perf_counter()
            r = await client.get(f"{url}/health")
            latency = int((time.perf_counter() - t0) * 1000)
            if r.status_code == 200:
                data = r.json() if "application/json" in r.headers.get("content-type","") else {}
                return {"name": url, "status": "online", "latency_ms": latency, "details": data}
            else:
                return {"name": url, "status": "degraded", "latency_ms": latency}
    except Exception as e:
        return {"name": url, "status": "offline", "latency_ms": None, "details": {"error": str(e)}}

@app.get("/api/health")
async def aggregate_health():
    tasks = [check_service(s) for s in SERVICES if s]
    results = await asyncio.gather(*tasks)
    return {"services": results}

@app.get("/api/dashboard")
async def dashboard():
    aggregated = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for s in SERVICES:
            if not s: continue
            try:
                r = await client.get(f"{s}/dashboard")
                aggregated[s] = r.json()
            except Exception:
                aggregated[s] = {"error": "unreachable"}
    return aggregated

@app.post("/api/events/publish")
async def publish_event(payload: dict):
    import aio_pika
    RURL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    connection = await aio_pika.connect_robust(RURL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange("micro.events", aio_pika.ExchangeType.FANOUT)
        await exchange.publish(
            aio_pika.Message(body=json.dumps(payload).encode()),
            routing_key=""
        )
    return {"published": True}

# --- NEW endpoint: verifica RabbitMQ (conexão AMQP) ---
@app.get("/api/rabbit")
async def check_rabbit():
    import aio_pika, asyncio
    RURL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    try:
        # tenta abrir e fechar uma ligação rápida
        connection = await aio_pika.connect_robust(RURL, timeout=3)
        await connection.close()
        return {"ok": True, "details": "AMQP reachable"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
