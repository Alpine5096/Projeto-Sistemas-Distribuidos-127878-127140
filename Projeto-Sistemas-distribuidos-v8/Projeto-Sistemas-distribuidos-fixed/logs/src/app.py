
from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logs_counter = Counter('logs_requests_total', 'Total number of log requests')

@app.route('/')
def home():
    return jsonify({
        "service": "logs",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/logs", "/health", "/metrics"]
    })

@app.route('/logs')
def get_logs():
    logs_counter.inc()
    return jsonify({
        "logs": [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "service": "orders",
                "message": "Order created successfully"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "service": "payments",
                "message": "Payment processed"
            }
        ],
        "total": 2
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "logs"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
