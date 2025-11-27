from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

logs = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "logs ok"})

@app.route('/log', methods=['POST'])
def receive_log():
    data = request.json
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "service": data.get("service"),
        "message": data.get("message")
    }
    logs.append(log_entry)
    return jsonify({"saved": True}), 201

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, use_reloader=False)