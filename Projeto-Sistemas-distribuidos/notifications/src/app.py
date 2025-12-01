
from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
notifications_counter = Counter('notifications_total', 'Total number of notifications')

@app.route('/')
def home():
    return jsonify({
        "service": "notifications",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/", "/notifications", "/health", "/metrics"]
    })

@app.route('/notifications')
def get_notifications():
    notifications_counter.inc()
    return jsonify({
        "notifications": [
            {
                "id": 1,
                "type": "email",
                "recipient": "user@example.com",
                "subject": "Order Confirmation",
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": 2,
                "type": "sms",
                "recipient": "+1234567890",
                "message": "Payment received",
                "status": "delivered",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "total": 2
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "notifications"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
