from flask import Flask, jsonify, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = Flask(__name__)

requests_total = Counter(
    "metricas_requests_total",
    "Total de pedidos ao serviço de métricas"
)

request_duration = Histogram(
    "metricas_request_duration_seconds",
    "Duração dos pedidos ao serviço de métricas"
)


@app.route("/summary")
def summary():
    start = time.perf_counter()

    requests_total.inc()

    response = {
        "orders_total": random.randint(50, 150),
        "payments_total": random.randint(30, 120),
        "notifications_total": random.randint(60, 200)
    }

    request_duration.observe(time.perf_counter() - start)

    return jsonify(response)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
