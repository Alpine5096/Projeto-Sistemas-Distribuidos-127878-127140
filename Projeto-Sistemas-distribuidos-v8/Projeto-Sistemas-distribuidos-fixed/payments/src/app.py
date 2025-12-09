
from flask import Flask, jsonify, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import logging
#start
import uuid # Usado para gerar IDs únicos para pagamentos
#end

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
payments_counter = Counter('payments_total', 'Total number of payments')
#start
payments_completed_counter = Counter('payments_completed_total', 'Total number of completed payments')

# Lista global para simular armazenamento em memória
# Num cenário real, isto seria um banco de dados
payments_db = [
    {"id": str(uuid.uuid4()), "order_id": 1, "amount": 999.99, "status": "completed"},
    {"id": str(uuid.uuid4()), "order_id": 2, "amount": 51.00, "status": "pending"}
]
#end

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

#start
@app.route('/create_payment', methods=['POST'])
def create_payment():
    """
    Endpoint para simular a criação e processamento de um pagamento.
    Espera um JSON com 'order_id' e 'amount'.
    """
    data = request.get_json()
    if not data or 'order_id' not in data or 'amount' not in data:
        return jsonify({"error": "Dados inválidos. Requer 'order_id' e 'amount'."}), 400

    order_id = data['order_id']
    amount = data['amount']
    
    # Simulação do processamento de pagamento
    # Na vida real, a lógica de validação e comunicação com
    # um gateway de pagamento ocorreria aqui.
    
    # Decidimos que pagamentos abaixo de 100 terão status 'completed' imediatamente
    # e o restante 'pending'
    status = "completed" if amount < 100 else "pending"
    
    new_payment = {
        "id": str(uuid.uuid4()),
        "order_id": order_id,
        "amount": amount,
        "status": status
    }

    # Adiciona à "base de dados" e incrementa métricas
    payments_db.append(new_payment)
    payments_counter.inc()

    if status == "completed":
        payments_completed_counter.inc()

    logging.info(f"Pagamento criado: {new_payment}")
    
    # Retorna o novo pagamento e um status de sucesso
    return jsonify(new_payment), 201 # 201 Created
#end

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "payments"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)