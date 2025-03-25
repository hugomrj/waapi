from flask import Flask, jsonify, request
app = Flask(__name__)


# Nueva ruta para obtener la versión
@app.route('/version')
def version():
    return jsonify({"version": "4.0"})


# Ruta del webhook
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        else:
            return "Error de autentificacion."
    
    
    data = request.get_json()
    mensaje = "Telefono:" + data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje += "|Mensaje:" + data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    
    # Extraer número del remitente
    remitente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']

    # Respuesta para WhatsApp (envía mensaje al usuario)
    return jsonify({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": remitente,
        "type": "text",
        "text": {
            "body": "Hola desde mi bot! 🚀"
        }
    }), 200



if __name__ == "__main__":
    app.run(debug=True)


