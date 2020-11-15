def añadirUsuario(user):
    """Función capaz de añadir un usuario al archivo de usuarios.
    Si el usuario ya existe, no hace nada y devuelve un -1.
    Si no existe, escribe el usuario y devuelve un 1"""
    if type(user) != int:
        print("Introduzca un valor entero la próxima vez")
        return -1
    archivo = open('usuarios.txt', 'r')
    lineas = archivo.readlines()
    for linea in lineas:
        # El usuario ya existe en el archivo
        if user == int(linea):
            print("Usuario",user,"ya existente en el sistema")
            return -1
    f=open("usuarios.txt", "a+")
    f.write(str(user))
    f.write("\n")
    f.close()
    print("Usuario",user,"introducido de manera correcta en el sistema")
    return 1

def borrarUsuario(user):
    """Función capaz de buscar un usuario en el sistema y borrarlo.
    Si lo encuentra, lo borra y devuelve 1.
    Si no lo encuentra, no hace nada y devuelve un -1"""
    if type(user) != int:
        print("Introduzca un valor entero la próxima vez")
        return -1
    aux = False;
    with open("usuarios.txt", "r") as f:
        lineas = f.readlines()
    with open("usuarios.txt", "w") as f:
        for linea in lineas:
            if linea.strip("\n") != str(user):
                f.write(linea)
            else:
                aux = True;
    if aux:
        print("Usuario encontrado en el sistema. Borrando")
        return 1
    print("Usuario no encontrado")
    return -1


def borrarMensajes():
    """Función capaz de limpiar por completo el fichero de mensajes"""
    open('mensajes.txt', 'w').close()

def borrarClaves():
    """Función capaz de limpiar por completo el fichero de claves"""
    open('claves.txt', 'w').close()

def borrarUsuarios():
    """Función capaz de limpiar por completo el fichero de usuarios"""
    open('usuarios.txt', 'w').close()


if __name__ == "__main__":
    borrarUsuarios()
