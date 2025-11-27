from flask import Flask, request, jsonify

app = Flask(__name__)

payments = []

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "payments ok"})

@app.route('/payments', methods=['POST'])
def process_payment():
    data = request.json
    payment = {
        "id": len(payments) + 1,
        "order_id": data.get("order_id"),
        "amount": data.get("amount"),
        "status": "paid"
    }
    payments.append(payment)
    return jsonify(payment), 201

@app.route('/payments', methods=['GET'])
def list_payments():
    return jsonify(payments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, use_reloader=False)