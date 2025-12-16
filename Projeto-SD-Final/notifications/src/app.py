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

# ---------------- DATA (IN-MEMORY) ----------------

NOTIFICATIONS = [
    {
        "id": 1,
        "order_id": 1,
        "message": "Order confirmed",
        "timestamp": datetime.now().isoformat()
    }
]

next_id = 2

# ---------------- APP ----------------

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notifications-service")

# ---------------- PROMETHEUS METRICS ----------------

NOTIFICATIONS_REQUESTS_TOTAL = Counter(
    "notifications_requests_total",
    "Total de requests ao serviço Notifications",
    ["method", "endpoint", "status"]
)

NOTIFICATIONS_REQUEST_LATENCY = Histogram(
    "notifications_request_duration_seconds",
    "Latência dos requests do serviço Notifications",
    ["method", "endpoint"]
)

# ---------------- MIDDLEWARE ----------------

@app.before_request
def start_timer():
    request.start_time = time.perf_counter()

@app.after_request
def record_metrics(response):
    duration = time.perf_counter() - request.start_time

    NOTIFICATIONS_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()

    NOTIFICATIONS_REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)

    return response

# ---------------- ENDPOINTS ----------------

@app.route("/notifications", methods=["GET"])
def list_notifications():
    logger.info("Notifications list requested")
    return jsonify({
        "service": "notifications",
        "count": len(NOTIFICATIONS),
        "data": NOTIFICATIONS
    })

@app.route("/notifications", methods=["POST"])
def create_notification():
    global next_id

    payload = request.json or {}

    notification = {
        "id": next_id,
        "order_id": payload.get("order_id"),
        "message": payload.get("message", "Notification created"),
        "timestamp": payload.get("timestamp", datetime.now().isoformat())
    }

    NOTIFICATIONS.append(notification)
    next_id += 1

    logger.info(f"Notification created: {notification}")

    return jsonify(notification), 201

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
    app.run(host="0.0.0.0", port=5004)
