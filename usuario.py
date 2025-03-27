

def buscar_usuario(numero):
    """Busca un usuario en datos/usuario.txt por su número de teléfono."""
    try:
        with open("datos/usuario.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                num, usuario = linea.strip().split(",", 1)
                if num == numero:
                    return usuario
    except FileNotFoundError:
        # Si el archivo no existe, lo indicamos claramente
        print("El archivo datos/usuario.txt no fue encontrado.")
        return ""  # Retorna una cadena vacía si no encuentra el archivo
    return ""  # Si no se encuentra el número, también retorna una cadena vacía
