
from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
payments_counter = Counter('payments_total', 'Total number of payments')

@app.route('/')
def home():
    return jsonify({
        "service": "payments",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/payments", "/health", "/metrics"]
    })

@app.route('/payments')
def get_payments():
    payments_counter.inc()
    return jsonify({
        "payments": [
            {"id": 1, "order_id": 1, "amount": 999.99, "status": "completed"},
            {"id": 2, "order_id": 2, "amount": 51.00, "status": "pending"}
        ],
        "total": 2
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "payments"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
