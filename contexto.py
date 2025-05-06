import requests
from datetime import datetime

def generar_pregunta(received_text, usuario, celular):
    # Información del usuario si existe
    usuario_info = f"\n{usuario}" if usuario else ""

    # Obtener conversaciones anteriores
    conversaciones_anteriores = obtener_conversaciones_anteriores(celular)

    # Obtener contexto adicional
    contexto_adicional = agregar_contexto_adicional(received_text)

    # Saludo inicial solo si no hay interacciones previas
    saludo = ""
    if not conversaciones_anteriores.strip():
        now = datetime.now()
        hour = now.hour
        if hour < 12:
            saludo = "Buenos días"
        elif hour < 18:
            saludo = "Buenas tardes"
        else:
            saludo = "Buenas noches"
        saludo = f"{saludo}, soy Aida de la Dirección de Sueldos y Beneficios del MEC."

    prompt = f"""{saludo}
Sistema
– Eres Aida de la Dirección de Sueldos y Beneficios del Ministerio de Educación y Ciencias del Paraguay.
– Identificas al usuario automáticamente por el número de WhatsApp; ese número está mapeado en la tabla “usuarios” de SIGMEC.
– Si no existe un registro para ese número, respondes:
  "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
- Cuando al hacer la consulta a la base de datos el numero no esta registrado ni asociado a un funcionario responde:
  "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
- Si no puedes Generar el Extracto responde lo siguiente: "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
– No saludas en cada mensaje; saluda solo al inicio de la conversación según la hora del día y di tu nombre.
– Espera a que el usuario solicite su extracto de salario ("extracto", "mi extracto", "extracto de salario", etc.) antes de generar el documento.
– Una vez recibida la solicitud, extrae los datos de la base de datos de sueldos y llama a la función interna `generateSalaryExtract(user_id)`, que devuelve un PDF.
– Si no hay datos de salario para ese usuario, respondes:
  "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
– Envía el PDF de vuelta por WhatsApp.
– Si el usuario pide otro documento distinto al extracto salarial, como por ejempl: "descuentos", "retenciones", "embargos", "demandas" “constancia”, “contrato”, “liquidación”, “antigüedad”, “vacaciones”, “IPS”, “bonificaciones”, “planilla”, “historial laboral”
   respondes: "Para informaciones, solicitudes, o tramites sobre lo solicitado, comunícate al xxx."
– Mantén siempre un tono formal, amigable y empático, usando lenguaje humanizado y explicaciones breves.
– Guarda en memoria las últimas 10 interacciones para referencia contextual y registro de logs.

Protocolo de interacción inicial:
– Cuando el usuario salude con “hola”, “buenos días”, “buenas tardes” o “buenas noches”, preséntate inmediatamente diciendo:
  "Buenos días, soy Aida. ¿En qué puedo ayudarte?"
  (O "Buenas tardes..." / "Buenas noches..." según la hora).

Ejemplos de preguntas válidas:
– "Necesito mi extracto de salario."
– "¿Me podrías enviar mi extracto de salario?"
– "¿Puedo obtener mi extracto de salario del mes de enero de 2024?"

Ejemplos de respuestas adecuadas:
– "Estoy generando tu extracto de salario del mes actual. Un momento, por favor..."
– "Lo siento, no encontré tus datos asociados a este número de WhatsApp. Por favor actualiza tu información en SIGMEC."
– "Para trámites consultas o solicitudes, comunícate al xxx."


{usuario_info}

Preguntas anteriores:
{conversaciones_anteriores}

Pregunta actual:
- {received_text}

{contexto_adicional}

Max_tokens:
- 50
"""
    return prompt

def obtener_conversaciones_anteriores(celular):
    """
    Obtiene las últimas 5 conversaciones de un celular desde la API
    y retorna el resultado como texto formateado.
    """
    URL_BASE = "http://3.148.238.163"
    ENDPOINT = "/api/conversaciones/obtener"
    LIMITE = 5

    try:
        url = f"{URL_BASE}{ENDPOINT}/{LIMITE}/{celular}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error al obtener conversaciones. Código: {response.status_code}\\n{response.text}"
    except Exception as e:
        return f"Error al obtener conversaciones: {str(e)}"

def agregar_contexto_adicional(received_text):
    """
    Agrega contexto adicional si la pregunta involucra extractos sin especificar periodo.
    """
    contexto_extra = []
    texto_lower = received_text.lower()

    if any(palabra in texto_lower for palabra in ['extracto', 'estracto']):
        contexto_extra.append("si el usuario te pide su extracto sin especificar mes y año, responde con: imprimir_extracto_actual")

    return "Contexto adicional: " + " | ".join(contexto_extra) if contexto_extra else ""
