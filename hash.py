# Script principal que calcula el hash-hmac de la clave diffie hellman
# y luego genera la contraseña común con HOTP

import hashlib
import random
import hmac
import sys
from tkinter import *
from diffieHellman import diffieHellman



def imprimirPantallaGuardar():
    """Imprime por pantalla el número que se haya introducido por tkinter
    y lo guarda en una variable para usarlo en el futuro"""
    print( 'El grupo introducido ha sido el %s' % (n.get()) )
    return n.get()

def generarInput():
    """Genera una ventana por tkinter para que el usuario introduzca
    el grupo con el que operar.
    Posee botones para guardar y ejecutar el programa"""
    ventana = Tk()
    Label(ventana, text='Grupo con el que operar [15: 3072 bits, 16: 4096 bits, 17: 6144 bits, 18: 8192 bits] ').grid(row=0)
    global n
    n = Entry(ventana)
    n.grid(row=0, column=1)
    Button(ventana, text='Ejecutar Programa', command=ventana.quit).grid(row=3, column=0, sticky=W, pady=4)
    Button(ventana, text='Guardar Valor', command=imprimirPantallaGuardar).grid(row=3, column=1, sticky=W, pady=4)
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

def calcularHOTP(contador, grupo):
    """Método que se encarga de calcular y devolver el HOTP"""
    # Guardamos un objeto con los parámetros a partir del grupo del primo elegido
    diffie = diffieHellman(grupo)

    # ¿Ambos usuarios presentan la misma clave final?
    if not diffie.presentarResultados():
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
        
        binary_representation = bin(int(byte,16))
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
        final = final % 60

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
    print("Últimos 8 dígitos de la contraseña:",modulo,"\n")
    return modulo


def main():
	# Semilla definida en cada inicio para obtener resultados consistentes = 30
    random.seed(30)

    # Contador del sistema para sincronizar, tiene 8 Bytes aleatorios,
    # como define el RFC de HOTP
    # sirve como mensaje del que calcular el HMAC a partir de la clave común
    contador = random.getrandbits(64)
    print("El valor del contador es: ", contador,"\n")
    
    # entrada del usuario, que se espera sea un entero
    # en caso de no ser, error y sale
    # genera la pantalla para elegir grupo, guarda en n el valor introducido
    n = generarInput()
    print("\n")
    
    # El valor no es numérico y devuelve un error
    if not n.isdecimal():
    	print("Introduzca un valor numérico la próxima vez")
    	return -1

    # Genera todos los parámetros de DH a partir del primo del grupo,
    # los guarda en un objeto de tipo diffieHellman con todos los demás parámetros
    valorHOTP = calcularHOTP(contador, n)
    print(valorHOTP)

    # TODO: ventana de resincronizacion, usuario desincroniazado,
    # calcular valor HOTP de ambos, etc

if __name__ == "__main__":
    main()
