from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ORDERS_SERVICE_URL = "http://orders:5001"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "gateway ok"})

# Criar uma order (gateway -> orders)
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        response = requests.post(f"{ORDERS_SERVICE_URL}/orders", json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Listar orders (gateway -> orders)
@app.route('/api/orders', methods=['GET'])
def list_orders():
    try:
        response = requests.get(f"{ORDERS_SERVICE_URL}/orders")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
