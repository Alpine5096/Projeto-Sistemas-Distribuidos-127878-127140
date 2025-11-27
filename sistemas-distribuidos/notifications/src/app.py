from flask import Flask, request, jsonify

app = Flask(__name__)

notifications = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "notifications ok"})

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.json
    notification = {
        "id": len(notifications) + 1,
        "type": data.get("type", "info"),
        "message": data.get("message"),
        "target": data.get("target")
    }
    notifications.append(notification)
    return jsonify(notification), 201

@app.route('/notifications', methods=['GET'])
def list_notifications():
    return jsonify(notifications)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, use_reloader=False)
