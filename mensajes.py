from datetime import datetime
import json
import os

import requests




'''
def crear_archivo_conversacion(phone_number):
    # Definir la ruta de la carpeta donde se guardarán las conversaciones
    carpeta = 'mensajes_log'
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # Nombre del archivo basado en el número de teléfono
    archivo_path = os.path.join(carpeta, f'{phone_number}.txt')

    # Verifica si el archivo no existe y lo crea (sin agregar texto al principio)
    if not os.path.exists(archivo_path):
        with open(archivo_path, 'w') as archivo:
            pass  # No agregamos texto al archivo si no existe

    return archivo_path
'''





def guardar_contexto_en_archivo(contexto):
    """
    Guarda el contexto en un archivo de log, agregándolo al inicio del archivo
    y desplazando el contenido existente hacia abajo.
    
    Args:
        contexto (str): Texto con el contexto a guardar
    
    Returns:
        bool: True si se guardó correctamente, False si hubo error
    """
    try:
        # Obtener fecha y hora actual formateada
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        separador = "=" * 50
        
        # Formatear el nuevo contenido
        nuevo_contenido = f"{separador}\n[{fecha_hora}]\n{contexto}\n{separador}\n\n"
        
        # Nombre del archivo
        archivo = "contexto_log.txt"
        
        # Leer contenido existente si el archivo existe
        contenido_existente = ""
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido_existente = f.read()
        
        # Escribir nuevo contenido + contenido existente
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido + contenido_existente)
        
        return True
    
    except Exception as e:
        print(f"Error al guardar contexto: {str(e)}")
        return False    


            



def registrar_conversacion_chat(celular, pregunta, respuesta):
    """
    Registra una conversación completa en el servidor de chat
    
    Args:
        celular (str): Número de teléfono (ej: "59112345678")
        pregunta (str): Texto de la pregunta del usuario
        respuesta (str): Texto de la respuesta del sistema
    
    Returns:
        dict: Respuesta del servidor en JSON o None si hubo error
    """
    # Configuración encapsulada
    API_URL = "http://3.148.238.163/api/conversaciones/registro"
    HEADERS = {'Content-Type': 'application/json'}
    
    # Preparar los datos
    datos = {
        "celular": celular,
        "pregunta": pregunta,
        "respuesta": respuesta
    }
    
    try:
        # Hacer la petición POST
        respuesta_servidor = requests.post(
            API_URL,
            data=json.dumps(datos),
            headers=HEADERS,
            timeout=10  # Timeout de 10 segundos
        )
        

        # Mostrar los datos en consola
        print("Datos a enviar:", json.dumps(datos, indent=4))

        # Verificar la respuesta
        if respuesta_servidor.status_code == 201:
            print("✅ Conversación registrada con éxito")
            return respuesta_servidor.json()
        else:
            print(f"❌ Error en el registro (HTTP {respuesta_servidor.status_code})")
            print("Detalles:", respuesta_servidor.text)
            return None
            
    except requests.exceptions.RequestException as error:
        print(f"⚠️ Error al conectar con el servidor: {error}")
        return None
    except Exception as error:
        print(f"⚠️ Error inesperado: {error}")
        return None



