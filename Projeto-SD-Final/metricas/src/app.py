from flask import Flask, jsonify, request, Response
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
import time
import logging

# ---------------- APP ----------------

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metricas-service")

# ---------------- PROMETHEUS METRICS ----------------

METRICAS_REQUESTS_TOTAL = Counter(
    "metricas_requests_total",
    "Total de requests ao serviço Metricas",
    ["method", "endpoint", "status"]
)

METRICAS_REQUEST_LATENCY = Histogram(
    "metricas_request_duration_seconds",
    "Latência dos requests do serviço Metricas",
    ["method", "endpoint"]
)

# ---------------- MIDDLEWARE ----------------

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def record_metrics(response):
    duration = time.perf_counter() - request.start_time

    METRICAS_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    METRICAS_REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    return response

# ---------------- ENDPOINTS ----------------

@app.route("/summary")
def summary():
    logger.info("Metricas summary requested")

    return jsonify({
        "status": "ok",
        "message": "Metricas service is running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
