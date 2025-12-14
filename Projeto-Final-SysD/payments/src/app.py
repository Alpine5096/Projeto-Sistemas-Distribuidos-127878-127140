from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from datetime import datetime
import logging
import time

# ---------------- APP ----------------

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payments-service")

# ---------------- PROMETHEUS METRICS ----------------

PAYMENTS_REQUESTS_TOTAL = Counter(
    "payments_requests_total",
    "Total de requests ao serviço Payments",
    ["method", "endpoint", "status"]
)

PAYMENTS_REQUEST_LATENCY = Histogram(
    "payments_request_duration_seconds",
    "Latência dos requests do serviço Payments",
    ["method", "endpoint"]
)

# ---------------- MIDDLEWARE ----------------

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def record_metrics(response):
    duration = time.perf_counter() - request.start_time

    PAYMENTS_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    PAYMENTS_REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    return response

# ---------------- ENDPOINTS ----------------

@app.route("/payments")
def payments():
    data = [
        {
            "id": 1,
            "order_id": 1,
            "amount": 999.99,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": 2,
            "order_id": 2,
            "amount": 25.50,
            "timestamp": datetime.now().isoformat()
        }
    ]

    logger.info("Payments list requested")

    return jsonify({
        "service": "payments",
        "count": len(data),
        "data": data
    })

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
    app.run(host="0.0.0.0", port=5002)
