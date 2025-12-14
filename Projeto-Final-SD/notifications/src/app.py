from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime

app = Flask(__name__)

notifications_total = Counter(
    "notifications_requests_total",
    "Total de pedidos ao serviço de notificações",
    ["service"]
)


@app.route("/notifications")
def notifications():
    notifications_total.labels(service="notifications").inc()

    data = [
        {
            "id": 1,
            "message": "Order confirmed",
            "timestamp": datetime.now().isoformat()
        }
    ]

    return jsonify({
        "service": "notifications",
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
    app.run(host="0.0.0.0", port=5004)
