import requests

def generar_pregunta(received_text, usuario, celular):
    """Genera el mensaje con el contexto y la pregunta actual, con el nombre de usuario si se encuentra."""
    
    # Si no hay usuario, se deja vacío el campo correspondiente en la pregunta
    usuario_info = f"\n{usuario}" if usuario else ""


    # Obtener conversaciones anteriores
    conversaciones_anteriores = obtener_conversaciones_anteriores(celular)


    # Obtener contexto adicional si existe    
    contexto_adicional = agregar_contexto_adicional(received_text)



    pregunta = f"""
        Sistema
– Eres Aida de la Dirección de Sueldos y Beneficios del Ministerio de Educación y Ciencias del Paraguay.
– Identificas al usuario automáticamente por el número de WhatsApp; ese número está mapeado en la tabla “usuarios” de SIGMEC.
– Si no existe un registro para ese número, respondes:
  "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
- Cuando al hacer la consulta a la base de datos el numero no esta registrado ni asociado a un funcionario responde:
  "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
- Si no puedes Generar el Extracto responde lo siguiente: "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto."
– No saludas en cada mensaje; saluda solo al inicio de la conversación según la hora del día:
  "Buenos días" (antes de 12:00), "Buenas tardes" (12:00–18:00) o "Buenas noches" (después de 18:00).
– Espera a que el usuario solicite su extracto de salario ("extracto", "mi extracto", "extracto de salario", etc.) antes de generar el documento.
– Una vez recibida la solicitud, extrae los datos de la base de datos de sueldos y llama a la función interna `generateSalaryExtract(user_id)`, que devuelve un PDF. - Si no hay datos de salario para ese usuario, responde:
  "Lo siento, no encontré tus datos. Por favor actualiza tu información en SIGMEC para poder generar tu extracto." Envía el PDF de vuelta por WhatsApp. 
– Si el usuario pide otro documento distinto al extracto salarial, respondes:
  "Para trámites consultas o solicitudes relacionada con: "descuentos", "retenciones", "embargos", "demandas" “constancia”, “contrato”, “liquidación”, “antigüedad”, “vacaciones”, “IPS”, “bonificaciones”, “planilla”, “historial laboral” , comunícate al xxx."
– Mantén siempre un tono formal, amigable y empático, usando lenguaje humanizado y explicaciones breves.
– Guarda en memoria las últimas 10 interacciones para referencia contextual y registro de logs.
- Evita utilizar lenguaje negativo como: "lamento", "lamentablemente", etc
- La conversacion debe ser mas Humanizada

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

    return pregunta


def obtener_conversaciones_anteriores(celular):
    """
    Obtiene las últimas 5 conversaciones de un celular desde la API
    y retorna el resultado como texto formateado.
    
    Args:
        celular (str): Número de celular a consultar (ej: '595971100267')
    
    Returns:
        str: Texto formateado con las conversaciones o mensaje de error
    """
    # Configuración fija
    URL_BASE = "http://3.148.238.163"
    ENDPOINT = "/api/conversaciones/obtener"
    LIMITE = 5  # Valor fijo como solicitaste
    
    try:
        # Construir URL completa
        url = f"{URL_BASE}{ENDPOINT}/{LIMITE}/{celular}"
        
        # Hacer la petición GET
        response = requests.get(url, timeout=10)
        
        # Verificar respuesta exitosa
        if response.status_code == 200:
            return response.text
        else:
            return f"Error al obtener conversaciones. Código: {response.status_code}\n{response.text}"
    
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"
    

def agregar_contexto_adicional(received_text):
    contexto_extra = []
    texto_lower = received_text.lower()
    
    
    if any(palabra in texto_lower for palabra in ['extracto', 'estracto']):
        contexto_extra.append("si el usuario te pide su estracto o extracto sin especificar mes y año responde con: imprimir_estracto_actual")
    
    '''
    if any(palabra in texto_lower for palabra in ['certificado', 'sueldo']):
        contexto_extra.append("para certificados de sueldo: generar_certificado_sueldo_pdf")
    '''

    # Retornar concatenado si hay coincidencias
    return "Contexto adicional: " + " | ".join(contexto_extra) if contexto_extra else ""
