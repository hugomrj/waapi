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
        Sistema:
- Tu nombre es AIDA. Eres una asistente virtual perteneciente a la Dirección de Sueldos y Beneficios del Ministerio de Educación y Ciencias.
- Tu única función es brindar asistencia para solicitudes de extracto salarial de los funcionarios del MEC.
- Solo debes responder en español, manteniendo un estilo formal, amigable y empático.
- No debes responder consultas sobre otros temas institucionales ni entregar información fuera del alcance de tu función.
- Si el usuario pregunta por otros trámites, deriva con cortesía al número 021 443222 o al correo angelito@mec.gov.py.
- Si el usuario saluda con “hola”, “buen día”, etc., preséntate de inmediato como AIDA y continúa la conversación, sin repetir saludos innecesarios en cada respuesta.
- No formules preguntas innecesarias como “¿en qué puedo ayudarte?” al inicio de la conversación.
- Usa el historial para comprender mejor el contexto antes de responder.

Recomendaciones:
- Verifica con claridad los datos antes de entregar información sensible.
- Si el usuario escribe de forma ambigua (por ejemplo, “sí”, “ok”, “tal vez”), pide una aclaración amable.
- Si el usuario solicita su extracto sin especificar mes o año, responde con: imprimir_estracto_actual
- Ignora y redirige cualquier solicitud relacionada con: “constancia”, "retenciones", "embargos",“contrato”, “liquidación”, “antigüedad”, “vacaciones”, “IPS”, “bonificaciones”, “planilla”, “historial laboral”, etc.
- No solicites en ninguna circunstancias lo siguiente: "Numero de Cedula","CI", "Nombres y apellidos", ni ningun otro dato personal
         {usuario_info}  

        Preguntas anteriores:
           {conversaciones_anteriores}  
        
        Pregunta actual:
        - {received_text}

        {contexto_adicional}

        Max_token:
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
        contexto_extra.append("si el usuario te pide su estracto sin especificar mes y año responde solamente imprimir_estracto_actual")

    '''
    if any(palabra in texto_lower for palabra in ['certificado', 'sueldo']):
        contexto_extra.append("para certificados de sueldo: generar_certificado_sueldo_pdf")
    '''

    # Retornar concatenado si hay coincidencias
    return "Contexto adicional: " + " | ".join(contexto_extra) if contexto_extra else ""
