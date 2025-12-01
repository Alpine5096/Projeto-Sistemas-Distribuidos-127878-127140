
from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
orders_counter = Counter('orders_total', 'Total number of orders')

@app.route('/')
def home():
    return jsonify({
        "service": "orders",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/orders", "/health", "/metrics"]
    })

@app.route('/orders')
def get_orders():
    orders_counter.inc()
    return jsonify({
        "orders": [
            {"id": 1, "product": "Laptop", "quantity": 1, "price": 999.99},
            {"id": 2, "product": "Mouse", "quantity": 2, "price": 25.50}
        ],
        "total": 2
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "orders"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
