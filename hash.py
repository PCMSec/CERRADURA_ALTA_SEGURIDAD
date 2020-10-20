# script principal que calcula el hash de la clave diffie hellman

import hashlib
import random
import sys
from diffieHellman import diffieHellman

def aplicarHash(n):
	m = hashlib.sha512()
	cadena = str(n).encode('utf-8')
	m.update(cadena)
	print(m.hexdigest())
	print(m.digest_size)


def main():
    random.seed(30)
    n = int(input("Introduzca el grupo con el que operar: "))
    test = diffieHellman(n)
    if test.presentarResultados():
        #Se devuelve la clave para hacer hash; el tamanyo es el mismo que el del primo usado
        print(sys.getsizeof(test.aFinal))
        #return test.aFinal
    aplicarHash(test.aFinal)

if __name__ == "__main__":
    main()