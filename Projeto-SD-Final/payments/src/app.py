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

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------- DATABASE ----------------

DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/sysd"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

Base.metadata.create_all(bind=engine)

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

@app.route("/payments", methods=["GET"])
def list_payments():
    db = SessionLocal()
    payments = db.query(Payment).all()
    db.close()

    return jsonify({
        "service": "payments",
        "count": len(payments),
        "data": [
            {
                "id": p.id,
                "order_id": p.order_id,
                "amount": p.amount,
                "status": p.status,
                "timestamp": p.timestamp.isoformat()
            } for p in payments
        ]
    })

@app.route("/payments", methods=["POST"])
def create_payment():
    payload = request.json or {}

    db = SessionLocal()

    payment = Payment(
        order_id=payload.get("order_id"),
        amount=payload.get("amount", 0),
        status=payload.get("status", "CREATED"),
        timestamp=datetime.now()
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.close()

    logger.info(f"Payment created: {payment.id} for order {payment.order_id}")

    return jsonify({
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status,
        "timestamp": payment.timestamp.isoformat()
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
    app.run(host="0.0.0.0", port=5002)
