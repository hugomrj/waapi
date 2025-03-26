import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Cargar las variables del archivo .env solo si estamos en local
# load_dotenv()


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.route('/version')
def version():
    return jsonify({"version": "10.2"})



def send_whatsapp_message(phone_number, message_body):
    """Envía un mensaje a través de la API de WhatsApp Business"""


    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
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
        if request.args.get('hub.verify_token', '') == VERIFY_TOKEN:
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
                received_text = message.get('text', {}).get('body', '')

                if from_number and received_text:
                    # Llamar a la API de /pregunta_ia con el texto recibido
                    api_url = "http://3.12.160.19/chat/pregunta_ia"  # Cambiar a tu URL correcta
                    headers = {"Content-Type": "application/json"}
                    payload = {"pregunta": received_text}

                    # Realizar la solicitud POST a la API
                    response = requests.post(api_url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        # Obtener la respuesta de la API
                        respuesta = response.json().get('respuesta', 'No se pudo obtener una respuesta.')

                        # Enviar la respuesta a WhatsApp
                        send_response = send_whatsapp_message(from_number, respuesta)
                        return jsonify({"status": "message sent" if send_response else "error sending message"}), 200 if send_response else 500
                    else:
                        return jsonify({"status": "error", "message": "Error from API"}), response.status_code
            
            return jsonify({"status": "not a whatsapp message"}), 200
        
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500



# curl "/test?pregunta=¿pregunta?"
@app.route("/test", methods=["GET"])
def test_api():
    try:
        # Obtener la pregunta desde los parámetros de la URL
        pregunta = request.args.get('pregunta')
        
        if not pregunta:
            return jsonify({"error": "Falta la pregunta en la URL"}), 400
        
        # URL de la API de IA
        api_url = "http://3.12.160.19/chat/pregunta_ia"  # Cambia por la URL correcta de tu servidor
        headers = {"Content-Type": "application/json"}
        payload = {"pregunta": pregunta}
        
        # Realizar la solicitud a la API de IA
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            # Obtener la respuesta de la IA
            respuesta = response.json().get('respuesta', 'No se pudo obtener una respuesta.')
            return jsonify({"respuesta": respuesta}), 200
        else:
            return jsonify({"error": "Error al llamar a la API de IA"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


        


if __name__ == '__main__':
    app.run(debug=True)            