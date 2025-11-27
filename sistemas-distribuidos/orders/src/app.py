from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage
orders = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "orders ok"})

@app.route('/orders', methods=['GET'])
def list_orders():
    return jsonify(orders)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    order = {
        "id": len(orders) + 1,
        "item": data.get("produto"),   # novo campo
        "price": data.get("preco"),    # novo campo
        "status": "created"
    }
    orders.append(order)
    return jsonify(order), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, use_reloader=False)
