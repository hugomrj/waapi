import os

def crear_archivo_conversacion(phone_number):
    # Definir la ruta de la carpeta donde se guardarán las conversaciones
    carpeta = 'mensajes_log'
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # Nombre del archivo basado en el número de teléfono
    archivo_path = os.path.join(carpeta, f'{phone_number}.txt')

    # Verifica si el archivo no existe y lo crea sin agregar ningún texto
    if not os.path.exists(archivo_path):
        with open(archivo_path, 'w') as archivo:
            pass  # No agregamos texto al archivo, solo lo creamos
