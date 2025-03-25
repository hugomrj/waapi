from flask import Flask, jsonify, request

app = Flask(__name__)

# Nueva ruta para obtener la versión
@app.route('/version')
def version():
    return jsonify({"version": "7.0"})

# Ruta del webhook
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token', '').strip() == "HolaNovato":
            return request.args.get('hub.challenge', '')
        return "Error de autenticación.", 403

    try:
        data = request.get_json()

        # Verificar estructura antes de acceder
        if not data or 'entry' not in data:
            return jsonify({"error": "JSON inválido"}), 400

        mensaje_data = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0]

        remitente = mensaje_data.get('from', 'desconocido')
        mensaje = mensaje_data.get('text', {}).get('body', 'Sin mensaje')

        print(f"Mensaje recibido de {remitente}: {mensaje}")  # Para depuración

        # Respuesta a WhatsApp
        return jsonify({
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": remitente,
            "type": "text",
            "text": {
                "body": "Hola desde mi bot! 🚀"
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
