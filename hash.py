# script principal que calcula el hash de la clave diffie hellman

import hashlib
import random
import hmac
import sys
import GUI
from tkinter import *
from diffieHellman import diffieHellman

def aplicarHash(n):
	"""funcion hash manual, TODO si se implementa al final"""
	print("Calculando el Hash de " + str(n) + "\n")
	m = hashlib.sha512()
	cadena = str(n).encode('utf-8')
	m.update(cadena)
	print("Tamanyo del bloque de salida: " + str(m.digest_size) + " Bytes, "+ str(m.digest_size*8) + " bits.\n")
	print("El hash obtenido es: " + m.hexdigest())
	return m.hexdigest()

def imprimirPantalla():
    print( 'El grupo introducido ha sido el %s' % (n.get()) )
    return n.get()

def generarInput():
    ventana = Tk()
    Label(ventana, text='Grupo con el que operar [15: 3072 bits, 16: 4096 bits, 17: 6144 bits, 18: 8192 bits] ').grid(row=0)
    global n
    n = Entry(ventana)
    n.grid(row=0, column=1)
    Button(ventana, text='Ejecutar Programa', command=ventana.quit).grid(row=3, column=0, sticky=W, pady=4)
    Button(ventana, text='Guardar Valor', command=imprimirPantalla).grid(row=3, column=1, sticky=W, pady=4)
    mainloop()
    return n.get()

	

def hmac_sha512(clave, mensaje):
    """devuelve el hmac con sha512 a partir de
    clave: clava de la comunicación entre DH
    mensaje: contador de 8 Bytes generado al azar
    se devuelve el resumen hmac"""

    # se convierten la clave y el mensaje, que eran enteros, a un conjunto de bytes
    clave = bytes(str(clave), "UTF-8")
    mensaje = bytes(str(mensaje), "UTF-8")

    #se devuelve el resultado del hmac
    digester = hmac.new(clave, mensaje, hashlib.sha512)
    print("Tamaño del HMAC resultante: ",digester.digest_size, " Bytes\n")
    return digester.hexdigest()

def eliminarPrefijo(stringNumero):
	"""quita el prefijo 0b de los Bytes que se introducen, los devuelve sin ella"""
	prefijo = "0b"
	if stringNumero.startswith(prefijo):
		return stringNumero[len(prefijo):]


def main():
	# Semilla definida en cada inicio para obtener resultados consistentes = 30
    random.seed(30)

    # contador del sistema para sincronizar, tiene 8 Bytes aleatorios, 64 bits, como define el RFC de HOTP
    contador = random.getrandbits(64)
    print("El valor del contador es: ", contador,"\n")
    # entrada del usuario, que se espera sea un entero
    # en caso de no ser, error y sale

    n = generarInput()
    
    print("\n")
    if not n.isdecimal():
    	print("Introduzca un valor numérico la próxima vez")
    	return -1

    # genera todos los parámetros de DH a partir del primo del grupo,
    # los guarda en un objeto de tipo diffieHellman con todos los demás parámetros
    diffie = diffieHellman(n)

    # ¿ambos usuarios presentan la misma clave final?
    if not diffie.presentarResultados():
    # No: error y el sistema para
    	print("Los valores finales de Diffie-Hellman no encajan, error en la comunicacion")
    	return -1
    # Si: el sistema continua
    resumenHmac = hmac_sha512(diffie.aFinal, contador)

    # 128 caracteres, 64 Bytes en total
    print("Resumen HMAC resultante: ", resumenHmac,"\n")

    # Coger el último Byte del grupo; por defecto 5f
    lastByte = resumenHmac[-2:]

    # Imprimir por pantalla el último byte
    print("Último Byte del HMAC: ",lastByte, "\n") #95

    # lista aux donde guardar los bit del último byte
    aux = []
    for byte in lastByte:
        binary_representation = bin(int(byte,16))
        print("Representacion binaria de",byte,":", binary_representation, "\n")

        salida = eliminarPrefijo(binary_representation)

        aux.append(salida)
    final = "".join(aux)
    print("Binario del último Byte: ",final, "\n")
    final = int(final,2)
    final = int(final/2)
    print("Valor en decimal del grupo de bits:",final*2,"\n")
    print("Se elige el grupo",final,"\n")
    #test correcto, comentar
    #final = 61
    if final > 60:
    	final = 60
    modulo = resumenHmac[final*2:final*2+8]
    print("4 Bytes que nos salen:",modulo,"\n")
    modulo = int(modulo,16)
    print("Resultado decimal de los Bytes obtenidos:",modulo,"\n")
    print("Últimos 8 dígitos de la contraseña:",modulo // 100,"\n")



if __name__ == "__main__":
    main()

