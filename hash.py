# Script principal que calcula el hash-hmac de la clave diffie hellman
# y luego genera la contraseña común con HOTP

import hashlib
import random
import hmac
import sys
import os
import time
from tkinter import *
from diffieHellman import diffieHellman
# import pyfirmata

# board = pyfirmata.Arduino('/dev/ttyACM0')

def establecerConexion(grupo):
    """A partir del grupo del primo, devuelve un objeto diffieHellman
    con el que comunicar entre ambos."""
    return diffieHellman(grupo)

def imprimirPantallaGuardar():
    """Imprime por pantalla el número que se haya introducido por tkinter
    y lo guarda en una variable para usarlo en el futuro"""
    print("El grupo introducido ha sido el %s" % (n.get()))
    print("El contador del usuario es %s" % (n1.get()))
    print("El margen con el que se opera es %s" % (n2.get()))
    print("El ID del usuario es %s" % (n3.get()))
    return n.get()


def generarInput():
    """Genera una ventana por tkinter para que el usuario introduzca
    el grupo con el que operar.
    Posee botones para guardar y ejecutar el programa"""
    ventana = Tk()
    Label(ventana, text='Grupo con el que operar [15: 3072 bits, 16: 4096 bits, 17: 6144 bits, 18: 8192 bits] ').grid(row=0)
    Label(ventana, text='Contador con el que opera el usuario').grid(row=1)
    Label(ventana, text='Margen de la ventana').grid(row=2)
    Label(ventana, text='ID del usuario').grid(row=3)

    global n
    global n1
    global n2
    global n3

    n = Entry(ventana)
    n1 = Entry(ventana)
    n2 = Entry(ventana)
    n3 = Entry(ventana)

    n.grid(row=0, column=1)
    n1.grid(row=1, column=1)
    n2.grid(row=2, column=1)
    n3.grid(row=3, column=1)

    Button(ventana, text='Ejecutar Programa', command=ventana.quit).grid(row=4, column=0, sticky=W, pady=4)
    Button(ventana, text='Guardar Valor', command=imprimirPantallaGuardar).grid(row=4, column=1, sticky=W, pady=4)
    mainloop()
    return n.get()


def hmac_sha512(clave, mensaje):
    """Devuelve el hmac con sha512 a partir de:
    clave: clave de la comunicación entre DH,
    mensaje: contador de 8 Bytes generado al azar,
    devuelve el resumen hmac"""

    # Se convierten la clave y el mensaje, que eran enteros, 
    # a un conjunto de bytes con el que operar
    clave = bytes(str(clave), "UTF-8")
    mensaje = bytes(str(mensaje), "UTF-8")

    # Se devuelve el resultado del hmac
    digester = hmac.new(clave, mensaje, hashlib.sha512)

    print("Tamaño del HMAC resultante: ",digester.digest_size, " Bytes\n")
    return digester.hexdigest()

def eliminarPrefijo(stringNumero):
	"""Quita el prefijo 0b de los Bytes que se introducen"""
	prefijo = "0b"
	if stringNumero.startswith(prefijo):
		return stringNumero[len(prefijo):]

def calcularHOTP(contador, grupo, diffie):
    """Método que se encarga de calcular y devolver el HOTP"""
    # Guardamos un objeto con los parámetros a partir del grupo del primo elegido
    # ¿Ambos usuarios presentan la misma clave final?
    if not diffie.conexionCorrecta():
    # No: error y el sistema para
        print("Los valores finales de Diffie-Hellman no encajan, error en la comunicacion")
        return -1
    # Si: el sistema continua
    # Calculamos el HMAC del mensaje contador a partir de la clave en común
    resumenHmac = hmac_sha512(diffie.aFinal, contador)

    # 128 caracteres, 64 Bytes en total
    print("Resumen HMAC resultante: ", resumenHmac,"\n")

    # Coger el último Byte del grupo (por defecto 5f) para elegir un grupo al azar
    lastByte = resumenHmac[-2:]

    # Imprimir por pantalla el último byte
    print("Último Byte del HMAC: ",lastByte, "\n") #95

    # lista auxiliar donde guardar los bits del último byte
    aux = []
    for byte in lastByte:
        
        binary_representation = format(int(byte,16), '#06b')
        print("Representacion binaria de",byte,":", binary_representation, "\n")

        salida = eliminarPrefijo(binary_representation)

        aux.append(salida)

    # Unir los bits para obtener la representación binaria del último byte
    final = "".join(aux)
    print("Binario del último Byte: ",final, "\n")

    # Pasar a decimal para calcular el grupo a elegir; se divide entre dos y
    # se pasa a entero porque final puede ser la segunda parte del Byte (impar),
    # y queremos el inicio del grupo entero (par).
    final = int(final,2)
    final = int(final/2)
    print("Valor en decimal del grupo de BITS resultante:",final*2,"\n")
    
    # Si es un valor superior a 60 (61, 62 o 63), ponemos el final al máximo
    # disponible, que es 60.

    while final > 60:
        print("El grupo",final,"se encuentra fuera del rango de Bytes, que tiene como máximo del 60 al 63","\n")
        final = final - 60

    print("Se elige el grupo de Bytes",final,"\n")
    # Cogemos el grupo de Bytes calculado antes y los 3 siguientes,
    # hasta disponer de 4 Bytes
    modulo = resumenHmac[final*2:final*2+8]
    print("4 Bytes que nos salen:",modulo,"\n")

    # Se pasan los valores, que están en hexadecimal, a decimal
    # para ser un input fácil de introducir para un usuario
    modulo = int(modulo,16)
    print("Resultado decimal de los Bytes obtenidos:",modulo,"\n")
    
    # Si el resulta tiene menos de 8 números, se añaden al final tantos
    # 0's como sean necesarios hasta que haya 8.
    while len(str(modulo)) <= 8:
        modulo *= 10

    # Si el resultado tiene más de 8 números, se quitan al final tantos
    # valores como sean necesarios hasta que haya 8.
    while len(str(modulo)) > 8:
        modulo = modulo // 10

    # Se devuelve el valor de la contraseña en común entre usuario
    # y caja fuerte.
    print("Primeros 8 dígitos de la contraseña:",modulo,"\n")
    return modulo


def main():
	# Semilla/Seed definida en cada inicio para obtener resultados consistentes = 30
    random.seed(30)

    if not os.path.exists('mensajes.txt'):
            os.mknod('mensajes.txt')
    # Contador del sistema para sincronizar, tiene 8 Bytes aleatorios,
    # como define el RFC de HOTP.
    # Sirve como mensaje del que calcular el HMAC a partir de la clave común
    contador = random.getrandbits(64)
    archivo = open('mensajes.txt', 'r') 
    lineas = archivo.readlines() 

    # Ya funciona, repasar diffie hellman
    for linea in lineas:
        if contador == int(linea):
            contador = random.getrandbits(64)

    f=open("mensajes.txt", "a+")
    f.write(str(contador))
    f.write("\n")
    f.close()
    print("El valor del contador es: ", contador,"\n")
    
    # entrada del usuario, que se espera sea un entero
    # en caso de no ser, error y sale
    # genera la pantalla para elegir grupo, guarda en n el valor introducido
    n = generarInput()
    print("\n")
    
    # Abrir el archivo con los ID's de los usuarios

    archivo_usuario = open('usuarios.txt', 'r') 
    lineas = archivo_usuario.readlines() 
    aux = False
    # Comparar el id del usuario para ver que el usuario tiene los permisos necesarios.
    # Se compara contra cada línea del archivo
    for linea in lineas:
        if int(n3.get()) == int(linea):
        	aux = True
    # Si no los tiene, error y return -1

    if not aux:
    	print("ERROR; El usuario no tiene permisos")
    	return -1
    # Continúa de manera normal de lo contrario

    # El valor no es numérico y devuelve un error
    if not n.isdecimal():
    	print("Introduzca un valor numérico la próxima vez")
    	return -1
    # Establecer conexion inicial a partir de un objeto diffieHellman
    # se usa el grupo anterior
    conexion = establecerConexion(n)
    conexion.presentarResultados()

    # Genera todos los parámetros de DH a partir del primo del grupo,
    # los guarda en un objeto de tipo diffieHellman con todos los demás parámetros
    contador_usuario = int(n1.get())
    ventana = int(n2.get())
    # Contadores desincronizados, el usuario puede estar adelantado
    valorHOTPcaja = calcularHOTP(contador, n, conexion)

    # Atencion, el usuario actual puede estar por detrás en sus aleatorios que el usuario anterior
    if contador_usuario != contador:
        # Dejamos el valor del usuario parado, la caja es la que va cambiando
        valorHOTPusuario = calcularHOTP(contador_usuario, n, conexion)
        print("EL CONTADOR DEL USUARIO NO ENCAJA. EL VALOR HOTP DEL USUARIO ES",valorHOTPusuario)
        # Leer el archivo de mensajes aleatorios a partir de la seed de antes
        f = open("mensajes.txt", "r")
        # Leer todas las lineas menos la ultima porque no nos interesa el nuevo valor
        lines = f.readlines()
        f.close()
        lines = lines[:-1]
        f = open("mensajes.txt", "w")
        for linea in lines:
        	f.write(linea)
        f.close()
        # Coger los últimos VENTANA valores del archivo, sin contar el generado para esta ejecución
        for aleatorio in lines[-ventana:]:
        	# Print del valor con el que se operra
            print("Calculando HOTP para valor del contador",aleatorio)
            # Re-calcular el valor HOTP de la caja con el aleatorio
            valorHOTPcaja = calcularHOTP(int(aleatorio), n, conexion)
            # Si coinciden, se hace print de toda la info y se termina
            if valorHOTPcaja == valorHOTPusuario:
                print("EL SISTEMA ENCUENTRA EL MISMO VALOR HOTP PARA EL CONTADOR GENERADO ANTES EN LA CAJA", aleatorio)
                print("VALOR DEL USUARIO:",valorHOTPusuario)
                print("VALOR DE LA CAJA FUERTE:",valorHOTPcaja)
                # board.digital[13].write(1)
                # time.sleep(10)
                # board.digital[13].write(0)
                return 0
        print("NO SE CONSIGUE GENERAR LA CONTRASEÑA")
        return -1
    # Los contadores son iguales, no hay problema
    else:
        print("Los contadores de ambos son iguales, calculando HOTP para ambos\n")
        valorHOTPusuario = calcularHOTP(contador_usuario, n, conexion)
        if valorHOTPcaja == valorHOTPusuario:
            print("Los valores coinciden, se da acceso")
            # board.digital[13].write(1)
            # time.sleep(10)
            # board.digital[13].write(0)
        return 0

    
    

if __name__ == "__main__":
    main()
