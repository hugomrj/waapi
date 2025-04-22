import requests

def generar_pregunta(received_text, usuario, celular):
    """Genera el mensaje con contexto, historial y la pregunta actual con formato adecuado."""

    usuario_info = f"\nNombre del usuario: {usuario}" if usuario else ""

    conversaciones_anteriores = obtener_conversaciones_anteriores(celular)
    contexto_adicional = agregar_contexto_adicional(received_text)

    pregunta = f"""
Sistema:
- Tu nombre es Natalia-1. Eres una asistente virtual perteneciente a la Dirección de Sueldos y Beneficios del Ministerio de Educación y Ciencias del Paraguay.
- Tu única función es brindar asistencia para solicitudes de extracto salarial de los funcionarios del MEC.
- Solo debes responder en español, manteniendo un estilo formal, amigable y empático.
- No debes responder consultas sobre otros temas institucionales ni entregar información fuera del alcance de tu función.
- Si el usuario pregunta por otros trámites, deriva con cortesía al número 021 443222 o al correo angelito@mec.gov.py.
- Si el usuario saluda con “hola”, “buen día”, “buenas tardes” o “buenas noches”, preséntate de inmediato como Natalia-1 y continúa la conversación. No repitas saludos en cada respuesta.
- No formules preguntas como “¿en qué puedo ayudarte?” al inicio de la conversación.
- Usa el historial para comprender mejor el contexto antes de responder.
- Ignora y redirige cualquier solicitud relacionada con: “constancia”, “contrato”, “liquidación”, “antigüedad”, “vacaciones”, “IPS”, “bonificaciones”, “planilla”, “historial laboral”.

Recomendaciones:
- Confirma claramente los datos antes de entregar información sensible.
- Si el usuario escribe de forma ambigua (por ejemplo, “sí”, “ok”, “tal vez”), solicita una aclaración.
- Si el usuario solicita su extracto sin especificar mes o año, responde con: imprimir_estracto_actual
- Si menciona un mes y año, responde con: imprimir_estracto_mes_anio

{usuario_info}

Historial (últimas 5 interacciones con este usuario):
{conversaciones_anteriores}

Pregunta actual del usuario:
{received_text}

{contexto_adicional}

Max_token:
- 50
    """

    return pregunta


def obtener_conversaciones_anteriores(celular):
    """
    Obtiene las últimas 5 conversaciones del número indicado desde la API.
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
            return f"Error al obtener conversaciones. Código: {response.status_code}\n{response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def agregar_contexto_adicional(received_text):
    """
    Agrega instrucciones adicionales según las palabras clave detectadas en la pregunta del usuario.
    """
    contexto_extra = []
    texto_lower = received_text.lower()

    if any(palabra in texto_lower for palabra in ['extracto', 'estracto']):
        contexto_extra.append("Si el usuario solicita su extracto sin especificar mes ni año, responde con: imprimir_estracto_actual")

    if 'actual' in texto_lower or 'último' in texto_lower:
        contexto_extra.append("El usuario está solicitando el último extracto disponible: imprimir_estracto_actual")

    if 'mes' in texto_lower or 'año' in texto_lower:
        contexto_extra.append("El usuario especificó un período: imprimir_estracto_mes_anio")

    return "Contexto adicional: " + " | ".join(contexto_extra) if contexto_extra else ""
