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
import requests

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------- DATABASE ----------------

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/sysd"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

# ---------------- SERVICE URLS ----------------

PAYMENTS_SERVICE_URL = "http://payments:5002/payments"
NOTIFICATIONS_SERVICE_URL = "http://notifications:5004/notifications"

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
    db = SessionLocal()
    orders = db.query(Order).all()
    db.close()

    return jsonify({
        "service": "orders",
        "count": len(orders),
        "data": [
            {
                "id": o.id,
                "product": o.product,
                "price": o.price,
                "timestamp": o.timestamp.isoformat()
            } for o in orders
        ]
    })

@app.route("/orders", methods=["POST"])
def create_order():
    payload = request.json or {}

    db = SessionLocal()

    order = Order(
        product=payload.get("product", "Unknown"),
        price=payload.get("price", 0),
        timestamp=datetime.now()
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()

    logger.info(f"Order created: {order.id}")

    # -------- CREATE PAYMENT --------
    payment_payload = {
        "order_id": order.id,
        "amount": order.price,
        "status": "CREATED",
        "timestamp": datetime.now().isoformat()
    }

    try:
        requests.post(PAYMENTS_SERVICE_URL, json=payment_payload, timeout=3)
    except Exception as e:
        logger.error(f"Failed to create payment for order {order.id}: {e}")

    # -------- CREATE NOTIFICATION --------
    notification_payload = {
        "order_id": order.id,
        "message": f"Order {order.id} created successfully",
        "timestamp": datetime.now().isoformat()
    }

    try:
        requests.post(NOTIFICATIONS_SERVICE_URL, json=notification_payload, timeout=3)
    except Exception as e:
        logger.error(f"Failed to create notification for order {order.id}: {e}")

    return jsonify({
        "id": order.id,
        "product": order.product,
        "price": order.price,
        "timestamp": order.timestamp.isoformat()
    }), 201

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
