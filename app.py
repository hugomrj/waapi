import os
import logging
import json
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, request
import requests

from contexto import generar_pregunta
from mensajes import  guardar_contexto_en_archivo, registrar_conversacion_chat
from usuario import buscar_usuario

app = Flask(__name__)

# Establecer el nivel de log de Flask a DEBUG
app.logger.setLevel(logging.DEBUG)


# Cargar las variables del archivo .env solo si estamos en local
# load_dotenv()


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.route('/version')
def version():
    return jsonify({"version": "10.38"})






# Añade esta nueva función para documentos
def send_whatsapp_document(phone_number, document_url, filename, caption=None):
    """Envía un documento PDF a través de la API de WhatsApp Business"""
    
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    document_data = {
        "link": document_url,
        "filename": filename
    }
    
    if caption:
        document_data["caption"] = caption

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": "document",
        "document": document_data
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error enviando documento: {e}")
        return None





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
                    # 1. Configuración inicial
                    api_url = "http://3.12.160.19/chat/pregunta_ia"
                    headers = {"Content-Type": "application/json"}
                    
                    # 2. Obtener información del usuario
                    usuario = buscar_usuario(from_number)
                    usuario_info = f"El usuario se llama {usuario}" if usuario else ""
                    app.logger.debug(f"Usuario: {usuario_info}")

                    # 3. Generar y guardar contexto
                    pregunta = generar_pregunta(received_text, usuario_info, from_number)
                    guardar_contexto_en_archivo(pregunta)
                    app.logger.debug(f"Consulta recibida de {from_number}")

                    # 4. Consultar a la IA
                    try:
                        response = requests.post(api_url, json={"pregunta": pregunta}, headers=headers, timeout=10)
                        response.raise_for_status()  # Lanza excepción para códigos 4XX/5XX
                        
                        respuesta = response.json().get('respuesta', '').strip().lower()
                        
                        # 5. Registrar en base de datos
                        registrar_conversacion_chat(from_number, received_text, respuesta)
                        
                        # 6. Manejo de comando especial para extracto PDF
                        if respuesta == "imprimir_estracto_actual_pdf":
                            pdf_url = f"http://3.148.238.163/api/reporte/celular/{from_number}"
                            
                            # Verificar disponibilidad del PDF
                            pdf_check = requests.head(pdf_url, timeout=5)
                            if pdf_check.status_code == 200:
                                if send_whatsapp_document(
                                    phone_number=from_number,
                                    document_url=pdf_url,
                                    filename="extracto.pdf",
                                    caption="Aquí tienes tu extracto oficial"
                                ):
                                    return jsonify({"status": "document sent"}), 200
                            
                            # Si falla cualquiera de los pasos anteriores
                            error_msg = "Lo siento, no pude generar tu extracto en este momento. Por favor intenta más tarde."
                            send_whatsapp_message(from_number, error_msg)
                            return jsonify({"status": "pdf generation failed"}), 200
                        
                        # 7. Respuesta normal de texto
                        send_whatsapp_message(from_number, respuesta)
                        return jsonify({"status": "message sent"}), 200

                    except requests.exceptions.RequestException as e:
                        app.logger.error(f"Error en la API: {str(e)}")
                        error_msg = "Disculpa, estoy teniendo problemas técnicos. Por favor intenta nuevamente más tarde."
                        send_whatsapp_message(from_number, error_msg)
                        return jsonify({"status": "service unavailable", "error": str(e)}), 200

            return jsonify({"status": "not a whatsapp message"}), 200
        
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500





@app.route('/ver_contexto', methods=['GET'])
def ver_contexto():
    """
    Endpoint para visualizar el contenido del archivo contexto_log.txt
    Devuelve el contenido formateado como texto plano con separadores claros
    """
    archivo_path = 'contexto_log.txt'
    
    if not os.path.exists(archivo_path):
        return Response("No hay registros de contexto disponibles", mimetype='text/plain')
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Formatear para mejor visualización
        respuesta = (
            "=== REGISTRO DE CONTEXTO ===\n\n"
            f"{contenido}\n"
            "=== FIN DEL REGISTRO ==="
        )
        
        return Response(respuesta, mimetype='text/plain')
    
    except Exception as e:
        error_msg = f"Error al leer el archivo: {str(e)}"
        return Response(error_msg, status=500, mimetype='text/plain')



        


if __name__ == '__main__':
    app.run(debug=True)            