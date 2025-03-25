from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import requests
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# ================================================
# 🔑 CONFIGURACIÓN INICIAL
# ================================================

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "MISSING_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "MISSING_ACCESS_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "MISSING_PHONE_ID")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "MISSING_APP_SECRET")

print("\n=== Variables cargadas ===")
print(f"VERIFY_TOKEN: {VERIFY_TOKEN[:3]}...")
print(f"ACCESS_TOKEN: {ACCESS_TOKEN[:3]}...")
print(f"PHONE_ID: {PHONE_ID}")
print(f"APP_SECRET: {APP_SECRET[:3]}...\n")


# Verificar variables
if not all([VERIFY_TOKEN, ACCESS_TOKEN, PHONE_ID, APP_SECRET]):
    app.logger.error("Faltan variables de entorno requeridas")
    raise RuntimeError("Configuración incompleta")

# ================================================
# 🚀 ENDPOINTS PRINCIPALES
# ================================================


@app.route('/version')
def health_check():
    return jsonify({"status": "active", 
                    "service": "WhatsApp Echo API", 
                    "version": "1.0.0", 
                    "build": "01"})




@app.route('/')
def health_check():
    """Endpoint de verificación de estado"""
    return jsonify({
        "status": "active",
        "service": "WhatsApp Echo API",
        "version": "1.0.0"
    })



@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verificación inicial del webhook"""
    app.logger.info("Solicitud GET recibida en /webhook")
    
    if not VERIFY_TOKEN:
        return "Verify token no configurado", 500
        
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == VERIFY_TOKEN:
        app.logger.info("Verificación exitosa")
        return challenge, 200
    return "Token inválido", 403



@app.route('/webhook', methods=['POST'])
def handle_message():
    """Procesamiento de mensajes entrantes"""
    app.logger.info("Solicitud POST recibida en /webhook")
    
    # Validar firma
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not _verify_signature(signature, request.data):
        app.logger.warning("Firma inválida recibida")
        return jsonify({"error": "Firma inválida"}), 403
    
    try:
        data = request.get_json()
        app.logger.debug(f"Datos recibidos: {data}")
        
        # Validar estructura del mensaje
        if not all([
            data.get('entry'),
            data['entry'][0].get('changes'),
            data['entry'][0]['changes'][0].get('value'),
            data['entry'][0]['changes'][0]['value'].get('messages')
        ]):
            app.logger.error("Estructura de mensaje inválida")
            return jsonify({"error": "Formato incorrecto"}), 400
            
        message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
        
        # Extraer datos esenciales
        phone = message_data.get('from')
        message = message_data.get('text', {}).get('body')
        
        if not all([phone, message]):
            app.logger.error("Datos esenciales faltantes")
            return jsonify({"error": "Datos incompletos"}), 400
        
        # Procesar y responder
        app.logger.info(f"Mensaje recibido de {phone}: {message}")
        _send_whatsapp_message(phone, message)
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        app.logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

# ================================================
# 🧪 ENDPOINTS DE PRUEBA
# ================================================

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Endpoint para pruebas sin WhatsApp"""
    test_data = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "text": {"body": "Mensaje de prueba"}
                    }]
                }
            }]
        }]
    }
    
    # Simular request de WhatsApp
    from flask.testing import EnvironBuilder
    builder = EnvironBuilder(
        path='/webhook',
        method='POST',
        json=test_data,
        headers={'X-Hub-Signature-256': _create_test_signature(test_data)}
    )
    env = builder.get_environ()
    
    with app.request_context(env):
        return handle_message()

# ================================================
# 🔧 FUNCIONES AUXILIARES
# ================================================

def _send_whatsapp_message(to, text):
    """Envía mensajes a través de la API de WhatsApp"""
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        app.logger.info(f"Enviando mensaje a {to}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        app.logger.debug(f"Respuesta de API: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error en API de WhatsApp: {str(e)}")
        return None

def _verify_signature(signature, payload):
    """Valida la firma HMAC"""
    secret = APP_SECRET.encode()
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return signature == f"sha256={expected}"

def _create_test_signature(data):
    """Crea firma para pruebas internas"""
    secret = APP_SECRET.encode()
    payload = jsonify(data).get_data()
    return f"sha256={hmac.new(secret, payload, hashlib.sha256).hexdigest()}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))