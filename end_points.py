from flask import Flask, request, jsonify
from caller import numero_tem_whatsapp, enviar_whatsapp, discar_e_transferir

app = Flask(__name__)

# Endpoint 1: Check WhatsApp availability
@app.route("/whatsapp/check", methods=["POST"])
def check_whatsapp():
    data = request.json
    numero = data.get("numero")
    device_serial = data.get("device_serial")
    
    if not numero:
        return jsonify({"error": "numero is required"}), 400
    
    result = numero_tem_whatsapp(numero, device_serial)
    return jsonify({"numero": numero, "whatsapp_available": result})

# Endpoint 2: Send WhatsApp
@app.route("/whatsapp/send", methods=["POST"])
def send_whatsapp():
    data = request.json
    numero = data.get("numero")
    mensagem = data.get("mensagem")
    device_serial = data.get("device_serial")
    
    if not numero or not mensagem:
        return jsonify({"error": "numero and mensagem are required"}), 400
    
    result = enviar_whatsapp(numero, mensagem, device_serial)
    return jsonify({"numero": numero, "sent": result})

# Endpoint 3: Dial and transfer
@app.route("/call/transfer", methods=["POST"])
def call_transfer():
    data = request.json
    numero = data.get("numero")
    nome = data.get("nome")
    data_nascimento = data.get("data_nascimento")
    device_serial = data.get("device_serial")
    
    if not numero or not nome or not data_nascimento:
        return jsonify({"error": "numero, nome, and data_nascimento are required"}), 400
    
    result = discar_e_transferir(numero, nome, data_nascimento, device_serial)
    return jsonify({"numero": numero, "status": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)