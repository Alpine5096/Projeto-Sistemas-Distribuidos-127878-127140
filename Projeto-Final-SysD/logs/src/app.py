from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from datetime import datetime
import time
import logging

# ---------------- APP ----------------

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logs-service")

# ---------------- PROMETHEUS METRICS ----------------

LOGS_REQUESTS_TOTAL = Counter(
    "logs_requests_total",
    "Total de requests ao serviço Logs",
    ["method", "endpoint", "status"]
)

LOGS_REQUEST_LATENCY = Histogram(
    "logs_request_duration_seconds",
    "Latência dos requests do serviço Logs",
    ["method", "endpoint"]
)

# ---------------- MIDDLEWARE ----------------

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def record_metrics(response):
    duration = time.perf_counter() - request.start_time

    LOGS_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    LOGS_REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    return response

# ---------------- ENDPOINTS ----------------

@app.route("/logs")
def logs():
    service = request.args.get("service", "all")

    logger.info(f"Logs requested for service={service}")

    return jsonify({
        "service": service,
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "msg": "Order created"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "msg": "Payment processed"
            }
        ]
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
    app.run(host="0.0.0.0", port=5003)
