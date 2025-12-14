from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payments-service")

payments_requests_total = Counter(
    "payments_requests_total",
    "Total de pedidos ao serviço de pagamentos",
    ["service"]
)


@app.route("/payments")
def payments():
    payments_requests_total.labels(service="payments").inc()

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
