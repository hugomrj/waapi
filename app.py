import os
import logging
import json
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request, send_from_directory, url_for
import requests

from contexto import generar_pregunta
from mensajes import crear_archivo_conversacion, guardar_pregunta_en_archivo, registrar_conversacion_chat
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
    return jsonify({"version": "10.29"})



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


                '''
                # Manejar solicitud de liquidación
                if received_text.lower() == "pdf":
                    # URL del servicio web que devuelve el PDF
                    pdf_url = f"http://3.148.238.163/api/reporte/celular/{from_number}"
                    

                    send_response = send_whatsapp_document(
                        phone_number=from_number,
                        document_url=pdf_url,  # Usamos directamente la URL del servicio
                        filename="liquidacion.pdf",
                        caption="Aquí tienes tu liquidación oficial"
                    )
                    
                    return jsonify({
                        "status": "document sent" if send_response else "error sending document"
                    }), 200 if send_response else 500
                '''




                if from_number and received_text:
                    # Llamar a la API de /pregunta_ia con el texto recibido
                    api_url = "http://3.12.160.19/chat/pregunta_ia"  # Cambiar a tu URL correcta
                    headers = {"Content-Type": "application/json"}
                    

                    usuario = buscar_usuario(from_number)
                    if usuario:
                        usuario = f"El usuario se llama {usuario}"                        
                    app.logger.debug(f"usuario  : {usuario}")


                    # Definir el mensaje con los contextos y la pregunta actual
                    pregunta = generar_pregunta(received_text, usuario)


                    # Mostrar el número en el log                    
                    # app.logger.debug(f"pregunta : \n{pregunta}")

                    # Guardar la conversación en el archivo
                    crear_archivo_conversacion(from_number)                               
                    guardar_pregunta_en_archivo(from_number, received_text)         

                    # Mostrar el número en el log                    
                    app.logger.debug(f"Se recibió el número: {from_number}")


                    # Realizar la solicitud POST a la API
                    response = requests.post(api_url, json={"pregunta": pregunta}, headers=headers)                    

                    app.logger.debug(f"response.status_code: {response.status_code}")

                    if response.status_code == 200:
                        # Obtener la respuesta de la API
                        respuesta = response.json().get('respuesta', 'No se pudo obtener una respuesta.')


                        # llamada api para guardar conversacion a base de datos

                        # Datos de prueba
                        resultado = registrar_conversacion_chat(
                            celular=from_number,
                            pregunta=pregunta,
                            respuesta=respuesta
                        )
                        
                        if resultado:
                            print("Respuesta del servidor:")
                            print(json.dumps(resultado, indent=2))




                        # Enviar la respuesta a WhatsApp
                        send_response = send_whatsapp_message(from_number, respuesta)
                        return jsonify({"status": "message sent" if send_response else "error sending message"}), 200 if send_response else 500
                    else:
                        return jsonify({"status": "error", "message": "Error from API"}), response.status_code
            
            return jsonify({"status": "not a whatsapp message"}), 200
        
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500





@app.route('/ver_conversacion/<phone_number>', methods=['GET'])
def ver_conversacion(phone_number):
    # Definir la ruta del archivo basado en el número de teléfono
    carpeta = 'mensajes_log'
    archivo_path = os.path.join(carpeta, f'{phone_number}.txt')

    # Verifica si el archivo existe
    if os.path.exists(archivo_path):
        # Abrir el archivo y leer su contenido
        with open(archivo_path, 'r') as archivo:
            contenido = archivo.read()
        return contenido  # Devolver el contenido del archivo en el navegador
    else:
        abort(404)  # Si el archivo no existe, devolver un error 404



        


if __name__ == '__main__':
    app.run(debug=True)            