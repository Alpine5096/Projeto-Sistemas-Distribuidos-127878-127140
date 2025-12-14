from flask import Flask, jsonify, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import logging
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

orders_requests_total = Counter(
    "orders_requests_total",
    "Total de pedidos ao serviço de orders",
    ["service"]
)

# ---------------- ENDPOINTS ----------------
@app.route("/orders", methods=["GET"])
def list_orders():
    orders_requests_total.labels(service="orders").inc()
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

    orders_requests_total.labels(service="orders").inc()
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
