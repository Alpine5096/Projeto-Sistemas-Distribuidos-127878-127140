from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
import logging
import time
from datetime import datetime

# ---------------- DATA (IN-MEMORY) ----------------

ORDERS = [
    {
        "id": 1,
        "product": "Laptop",
        "price": 999.99,
        "timestamp": datetime.now().isoformat()
    },
    {
        "id": 2,
        "product": "Mouse",
        "price": 25.50,
        "timestamp": datetime.now().isoformat()
    }
]

next_id = 3

# ---------------- APP ----------------

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orders-service")

# ---------------- PROMETHEUS METRICS ----------------

ORDERS_REQUESTS_TOTAL = Counter(
    "orders_requests_total",
    "Total de requests ao serviço Orders",
    ["method", "endpoint", "status"]
)

ORDERS_REQUEST_LATENCY = Histogram(
    "orders_request_duration_seconds",
    "Latência dos requests do serviço Orders",
    ["method", "endpoint"]
)

# ---------------- MIDDLEWARE ----------------

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def record_metrics(response):
    duration = time.perf_counter() - request.start_time

    ORDERS_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    ORDERS_REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    return response

# ---------------- ENDPOINTS ----------------

@app.route("/orders", methods=["GET"])
def list_orders():
    logger.info("Orders list requested")
    return jsonify({
        "service": "orders",
        "count": len(ORDERS),
        "data": ORDERS
    })

@app.route("/orders", methods=["POST"])
def create_order():
    global next_id

    payload = request.json or {}

    order = {
        "id": next_id,
        "product": payload.get("product", "Unknown"),
        "price": payload.get("price", 0),
        "timestamp": datetime.now().isoformat()
    }

    ORDERS.append(order)
    next_id += 1

    logger.info(f"Order created: {order}")
    return jsonify(order), 201

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
