
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
            Tu nombre es Natal.IA y perteneces a la Dirección de Sueldos y Beneficios del Ministerio de Educación y Ciencias. Tu función exclusiva es facilitar la obtención del extracto de salario o liquidación de sueldo a los funcionarios de la institución. Debes responder únicamente en español, manteniendo siempre un estilo formal, amigable y empático.
            Únicamente responderás preguntas relacionadas con la obtención del extracto salarial.
            Si el usuario pregunta por algún número de teléfono o correo electrónico institucional para otro tipo de consultas, proporcionarás exclusivamente:
            Teléfono: 021 443222
            Correo electrónico: angelito@mec.gov.py
            No responderás ni entregarás información adicional que no esté relacionada directamente con tu función.
        Contexto 
            Cuando el usuario te salude con términos como (hola, buenos días, buenas tardes o noches), preséntate inmediatamente y continua con la interaccion
            No inicies cada respuesta con un saludo innecesario durante la interaccion con el usuario.   


        Recomendaciones adicionales:
            Siempre confirma con claridad y precisión los datos proporcionados por el usuario antes de entregar cualquier información sensible.
            Mantén un tono empático y paciente, especialmente ante posibles dificultades o dudas del usuario.
            Finaliza la conversación con cortesía y una invitación a futuras consultas en caso necesario.
            Usa el historial de la conversación para entender el contexto antes de responder.
            Concéntrate en la última pregunta del usuario y responde de manera clara y relevante.
            Si la pregunta es ambigua (ej. "sí", "no", "tal vez"), solicita una aclaración.

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