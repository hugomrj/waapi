from datetime import datetime
import json
import os

import requests





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






def obtener_conversaciones(archivo_path):
    # Leer el archivo y cargar las preguntas
    with open(archivo_path, 'r') as archivo:
        lineas = archivo.readlines()
    
    # Convertir las líneas en un formato de preguntas con fechas
    preguntas = []
    for i in range(0, len(lineas), 3):
        if i + 1 < len(lineas):
            fecha = lineas[i].strip().split(": ")[1]
            pregunta = lineas[i + 1].strip().split(": ")[1]
            preguntas.append((fecha, pregunta))
    
    return preguntas





def guardar_pregunta_en_archivo(phone_number, question):
    # Obtener la fecha y hora actual
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear el archivo si no existe
    archivo_path = crear_archivo_conversacion(phone_number)

    # Obtener las preguntas existentes
    preguntas = obtener_conversaciones(archivo_path)

    # Agregar la nueva pregunta al inicio de la lista
    preguntas.insert(0, (fecha_actual, question))

    # Si hay más de 5 preguntas, eliminar la más antigua
    if len(preguntas) > 5:
        preguntas.pop()

    # Reescribir el archivo con las preguntas ordenadas
    with open(archivo_path, 'w') as archivo:
        for fecha, pregunta in preguntas:
            archivo.write(f"Fecha: {fecha}\n")
            archivo.write(f"Pregunta: {pregunta}\n\n")




            



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



