from flask import Flask, jsonify, request
import requests


app = Flask(__name__)

@app.route('/version')
def version():
    return jsonify({"version": "9.0"})

def send_whatsapp_message(phone_number, message_body):
    """Envía un mensaje a través de la API de WhatsApp Business"""

    
    url = "https://graph.facebook.com/v22.0/635224343007012/messages"
    

    headers = {
        "Authorization": "Bearer EAAjChKYE1goBOzPhaHDUlyiTuVRUa8kmKyZCb2ZApnTocC6gCHj2SbTP2muycx6PsYirtXl8vrqn2ZASxSA5mRSV9mikVfz3KZADpVEbvdkAFAtZAqiY6i5QK7YKuwCnZB6IttEaRmkdfCBEFKhAmDapaS1NjCwaso64aCXrxFlbE5ZBioAtg3i5B2pGCfNK0eDAqwFsRIOOlofCDBwlq3i6bKk",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "text",
        "text": {"body": message_body}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error enviando mensaje: {e}")
        return None





@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token', '') == "HolaNovato":
            return request.args.get('hub.challenge', ''), 200
        return "Error de autenticación.", 403
    
    if request.method == "POST":
        try:
            body = request.get_json()
            if not body:
                return jsonify({"status": "error", "message": "Empty request body"}), 400
            
            if body.get('object') == 'whatsapp_business_account':
                entry = body.get('entry', [])
                if not entry:
                    return jsonify({"status": "error", "message": "No entry found"}), 400
                
                changes = entry[0].get('changes', [])
                if not changes:
                    return jsonify({"status": "error", "message": "No changes found"}), 400
                
                message = changes[0].get('value', {}).get('messages', [{}])[0]
                from_number = message.get('from')

                if from_number:
                    response = send_whatsapp_message(from_number, "Hola, soy un bot de prueba")
                    return jsonify({"status": "message sent" if response else "error sending message"}), 200 if response else 500
            
            return jsonify({"status": "not a whatsapp message"}), 200
        
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
