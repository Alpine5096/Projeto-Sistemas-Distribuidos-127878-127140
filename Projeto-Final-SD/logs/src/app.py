from flask import Flask, jsonify, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime

app = Flask(__name__)

logs_requests = Counter(
    "logs_requests_total",
    "Total de pedidos ao serviço de logs",
    ["service"]
)


@app.route("/logs")
def logs():
    service = request.args.get("service", "all")
    logs_requests.labels(service=service).inc()

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
