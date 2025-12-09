
from flask import Flask, jsonify, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
import logging, time, random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
requests_total = Counter('metricas_requests_total', 'Total requests to metrics service')
request_duration = Histogram('metricas_request_duration_seconds', 'Request duration')
active_connections = Gauge('metricas_active_connections', 'Active connections')
system_load = Gauge('metricas_system_load', 'System load average')

@app.route('/')
def home():
    return jsonify({
        "service": "metricas",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/metrics", "/health", "/stats"]
    })

@app.route('/metrics')
def metrics():
    requests_total.inc()
    active_connections.set(random.randint(10, 100))
    system_load.set(random.uniform(0.1, 2.0))
    try:
        metrics_data = generate_latest(REGISTRY)
        return Response(metrics_data, mimetype=CONTENT_TYPE_LATEST)
    except Exception as e:
        logging.error(f"Error generating metrics: {e}")
        return jsonify({"error": "Failed to generate metrics"}), 500

@app.route('/stats')
def stats():
    requests_total.inc()
    return jsonify({
        "service_metrics": {
            "total_requests": int(requests_total._value.get()),
            "active_connections": random.randint(10, 100),
            "system_load": round(random.uniform(0.1, 2.0), 2),
            "uptime": "24h"
        },
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "metricas",
        "prometheus_endpoint": "/metrics"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
