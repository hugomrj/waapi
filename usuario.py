

def buscar_usuario(numero):
    """Busca un usuario en datos/usuario.txt por su número de teléfono."""
    try:
        with open("datos/usuario.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                num, usuario = linea.strip().split(",", 1)
                if num == numero:
                    return usuario
    except FileNotFoundError:
        pass  # No hacer nada si el archivo no existe
    return None


