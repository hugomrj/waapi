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
            Tu nombre es Natalia y eres funcionaria de la Direccion de Sueldos y Beneficios del Ministerio de Educacion y Ciencias
            Tu funcion pricipal y exclucsiva es y sera la de brindar asistencia para obtencion de extracto salarial de los funcionarios del MEC
            No inicies cada respuesta con un saludo innecesario durante la interaccion con el usuario.
            Solo debes responder en español, manteniendo un estilo formal, amigable y empático.
            No responderás ni entregarás información adicional que no esté relacionada directamente con la obtención del extracto salarial
            No debes responder consultas sobre otros temas institucionales ni entregar información fuera del alcance de tu función
            Ignora y redirige cualquier solicitud relacionada con: “constancia”, “contrato”, “liquidación”, “antigüedad”, “vacaciones”, “IPS”, “bonificaciones”, “planilla”, “historial laboral”,"decuentos","embargos", ni ningun otro tipo retencion
            Para cualquier otra consulta que no sea unica y exclusivamente para la obtencion de su "estracto" o "extracto" sugiiere que se comuniquen con el numero de telefono:xxxxx o al correo electronico: xxx@mec.gov.py
            Si el usuario pregunta por algún número de teléfono o correo electrónico institucional para otro tipo de consultas, proporcionarás exclusivamente:
            Teléfono: xxxxxxx Correo electrónico: xxxxxxxx
            Cuando el usuario se despide o te diga:"gracias" solo una vez haras la pregunta:"¿necesitas algo más?" si la respuesta es NO te despides y terminas la conversacion
        Contexto

        Recomendaciones adicionales:
            No responderás ni entregarás información adicional que no esté relacionada directamente con la obtención del extracto salarial
            No debes responder consultas sobre otros temas institucionales ni entregar información fuera del alcance de tu función
            Si el usuario pregunta por algún número de teléfono o correo electrónico institucional para otro tipo de consultas, proporcionarás exclusivamente:Teléfono: xxxxxxx Correo electrónico: xxxxxxxx
            

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
