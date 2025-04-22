import requests

def generar_pregunta(received_text, usuario, celular):
    """Genera el mensaje con el contexto, instrucciones del sistema y la pregunta actual."""

    usuario_info = f"Usuario identificado: {usuario}" if usuario else "Usuario no identificado."

    conversaciones_anteriores = obtener_conversaciones_anteriores(celular)

    contexto_adicional = agregar_contexto_adicional(received_text)

    pregunta = f"""
Sistema:
    Tu nombre es Natalia-1 y perteneces a la Dirección de Sueldos y Beneficios del Ministerio de Educación y Ciencias.
    Tu función exclusiva es brindar y facilitar información relacionada a la obtención del extracto salarial.
    Debes responder únicamente en español, manteniendo siempre un estilo formal, amigable y empático.
    Si el usuario pregunta por algún número de teléfono o correo institucional para otro tipo de consultas, proporciona únicamente:
        Teléfono: 021 443222
        Correo electrónico: angelito@mec.gov.py
    No entregues información que no esté directamente relacionada con la obtención del extracto salarial.
    Cuando el usuario te salude (hola, buenos días, buenas tardes o noches), preséntate inmediatamente como Natalia-1.
    No inicies cada respuesta con un saludo innecesario durante la interacción.
    Usa siempre el historial de la conversación para responder con contexto.
    No hagas la pregunta: “¿En qué puedo ayudarte con tu extracto de salario?” al inicio. Solo preséntate.

Contexto:
    {usuario_info}
    Historial reciente de conversación:
    {conversaciones_anteriores}

Contexto adicional:
    {contexto_adicional}

Pregunta actual:
    {received_text}

Max_token:
    50
"""

    return pregunta


def obtener_conversaciones_anteriores(celular):
    """Obtiene las últimas 5 conversaciones del usuario desde la API."""
    URL_BASE = "http://3.148.238.163"
    ENDPOINT = "/api/conversaciones/obtener"
    LIMITE = 5

    try:
        url = f"{URL_BASE}{ENDPOINT}/{LIMITE}/{celular}"
        response = requests.get(url, timeout=10)
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
        contexto_extra.append("Si el usuario solicita su extracto sin especificar mes y año, responde con: imprimir_estracto_actual")
    if "mes" in texto_lower or "año" in texto_lower:
        contexto_extra.append("Si se menciona un mes o año, responde con: imprimir_estracto_con_fecha")
    if any(palabra in texto_lower for palabra in ['gracias', 'ok', 'perfecto']):
        contexto_extra.append("Responde de forma amable y ofrece asistencia futura si es necesario.")
    if any(palabra in texto_lower for palabra in ['no entiendo', 'cómo', 'dificultad']):
        contexto_extra.append("Brinda una explicación clara y paso a paso. Sé paciente.")
    if any(palabra in texto_lower for palabra in ['correo', 'email']):
        contexto_extra.append("Recuerda al usuario que para otras consultas debe contactar al correo oficial: angelito@mec.gov.py")
    if any(palabra in texto_lower for palabra in ['telefono', 'número']):
        contexto_extra.append("Recuerda al usuario que para otras consultas debe llamar al: 021 443222")

    return " | ".join(contexto_extra) if contexto_extra else "Sin contexto adicional detectado."
