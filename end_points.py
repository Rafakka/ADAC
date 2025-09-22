from flask import Flask, request, jsonify
from caller import numero_tem_whatsapp, enviar_whatsapp, discar_e_transferir
from csv_manager import XLSXManager  # Your XLSX manager class
import threading

app = Flask(__name__)

# Initialize XLSX manager
xlsx_manager = XLSXManager()

# ---------------- XLSX Endpoints ----------------

@app.route("/contacts/check", methods=["GET"])
def get_contacts():
    """Return list of pending contacts"""
    contatos = xlsx_manager.ler_contatos()
    return jsonify({"contatos": contatos})

@app.route("/contacts/mark", methods=["POST"])
def mark_contact():
    """Mark a contact as processed"""
    data = request.json
    numero = data.get("numero")
    status = data.get("status")
    nome = data.get("nome", "")
    data_nascimento = data.get("data_nascimento", "")

    if not numero or not status:
        return jsonify({"error": "numero and status are required"}), 400

    success = xlsx_manager.marcar_como_processado(numero, status, nome, data_nascimento)
    return jsonify({"numero": numero, "success": success})

@app.route("/contacts/xlsx_path", methods=["GET"])
def get_xlsx_path():
    """Return current XLSX file path"""
    return jsonify({"xlsx_path": xlsx_manager.get_xlsx_path()})

# ---------------- WhatsApp Endpoints ----------------

@app.route("/whatsapp/check", methods=["POST"])
def check_whatsapp():
    data = request.json
    numero = data.get("numero")
    device_serial = data.get("device_serial")
    if not numero:
        return jsonify({"error": "numero is required"}), 400
    result = numero_tem_whatsapp(numero, device_serial)
    return jsonify({"numero": numero, "whatsapp_available": result})

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

# ---------------- Call/Transfer Endpoint ----------------

def async_discar_e_transferir(numero, nome, data_nascimento, device_serial):
    """Run the call transfer process in a separate thread"""
    status = discar_e_transferir(numero, nome, data_nascimento, device_serial, csv_manager=xlsx_manager)
    # You could also implement a callback or save status somewhere if needed
    return status

@app.route("/call/transfer", methods=["POST"])
def call_transfer():
    data = request.json
    numero = data.get("numero")
    nome = data.get("nome")
    data_nascimento = data.get("data_nascimento")
    device_serial = data.get("device_serial")

    if not numero or not nome or not data_nascimento:
        return jsonify({"error": "numero, nome, and data_nascimento are required"}), 400

    # Start call in a background thread
    thread = threading.Thread(target=async_discar_e_transferir, args=(numero, nome, data_nascimento, device_serial))
    thread.start()

    return jsonify({"numero": numero, "status": "IN_PROGRESS"})

# ---------------- Run App ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)