from flask import Flask, jsonify
import time

app = Flask(__name__)

metrics = {
    "orders_count": 0,
    "payments_count": 0,
    "notifications_count": 0,
    "logs_received": 0,
    "start_time": time.time()
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "metrics ok"})

@app.route('/metrics', methods=['GET'])
def get_metrics():
    uptime = time.time() - metrics["start_time"]
    return jsonify({**metrics, "uptime": uptime})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, use_reloader=False)