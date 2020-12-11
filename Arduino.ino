#include <Crypto.h>
#include <Curve25519.h>
#include <RNG.h>
#include <string.h>
#include <SimpleHOTP.h>
#include <stdlib.h>


static uint8_t alice_k[32];
unsigned long startTime;
uint32_t code[5];
uint8_t contador[8];

//Funcion de ejemplo sacada de los ejemplos de la propia biblioteca SimpleHOTP que se usa
void testDH()
{
    static uint8_t alice_f[32];
    static uint8_t bob_k[32];
    static uint8_t bob_f[32];

    Serial.println("Diffie-Hellman key exchange:");
    Serial.print("Generate random k/f for Alice ... ");
    Serial.flush();
    unsigned long start = micros();
    Curve25519::dh1(alice_k, alice_f);
    unsigned long elapsed = micros() - start;
    Serial.print("elapsed ");
    Serial.print(elapsed);
    Serial.println(" us");

    Serial.print("Generate random k/f for Bob ... ");
    Serial.flush();
    start = micros();
    Curve25519::dh1(bob_k, bob_f);
    elapsed = micros() - start;
    Serial.print("elapsed ");
    Serial.print(elapsed);
    Serial.println(" us");

    Serial.print("Generate shared secret for Alice ... ");
    Serial.flush();
    start = micros();
    Curve25519::dh2(bob_k, alice_f);
    elapsed = micros() - start;
    Serial.print("elapsed ");
    Serial.print(elapsed);
    Serial.println(" us");

    Serial.print("Generate shared secret for Bob ... ");
    Serial.flush();
    start = micros();
    Curve25519::dh2(alice_k, bob_f);
    elapsed = micros() - start;
    Serial.print("elapsed ");
    Serial.print(elapsed);
    Serial.println(" us");

    Serial.print("Check that the shared secrets match ... ");
    if (memcmp(alice_k, bob_k, 32) == 0)
        Serial.println("ok");
    else
        Serial.println("failed");
}



void setup() {
  Serial.begin(9600);
  // Dejar el led del puerto 13 para iluminar
  pinMode(13, OUTPUT);
  // Ejecutar el DH de arriba
  testDH();
  // Generar un número aleatorio de 8 Bytes y guardarlo en "contador"
  RNG.rand(contador, sizeof(contador));
  // Fragmento para pasar de String a char []
  char salidaContador[8];
  String textoMensaje = "";
  for (int i = 0; i < sizeof(contador); i++){
    textoMensaje += String(contador[i]);
  }
  textoMensaje.toCharArray(salidaContador,sizeof(salidaContador));
  // Fragmento para pasar de String a char []
  char salidaAlice[32];
  String textoAlice = "";
  for (int i = 0; i < sizeof(alice_k); i++){
    textoAlice += String(alice_k[i]);
  }
  textoAlice.toCharArray(salidaAlice,sizeof(salidaAlice));

  // Presentar por la consola de DEBUG los valores de DH y del contador
  Serial.print("Valor obtenido en la curva (256 bits; 32 Bytes): ");Serial.println(salidaAlice);
  Serial.print("Valor del Contador (64 bits; 8 Bytes): ");Serial.println(salidaContador);
  // Hacer que la clave sea el valor de DH presentado anteriormente
  Key key(salidaAlice, sizeof(salidaAlice)-1);
  // Generar HMAC. Clave es la de la línea anterior, mensaje es el contador de 8 Bytes
  SimpleHMAC::generateHMAC(key, salidaContador, (sizeof(salidaContador)-1)*8, code);
  // Presentar por consola de DEBUG los valores del HMAC en HEX
  Serial.print("HMAC resultante(160 bits; 20 Bytes): ");
  for (int i = 0; i < 5; i++) {
    Serial.print(code[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
  // Guardar el último grupo, para acceder a los 4 últimos bits de manera sencilla
  String lastGroup;
  lastGroup = String(code[4], HEX);
  // Acceder a la longitud del último grupo, en caso de que sean menos de 4 Bytes
  int len;
  len = lastGroup.length();
  
  char valorInicio = lastGroup[len-1];
  // Unir los 5 grupos del HMAC total
  String total = "";
  total += String(code[0], HEX);
  total += String(code[1], HEX);
  total += String(code[2], HEX);
  total += String(code[3], HEX);
  total += String(code[4], HEX);
  // Necesario presentar el codigo desde la posicion valorInicio hasta 3 mas adelante.
  Serial.print("Valor de los últimos 4 bits del último Byte: ");Serial.println(valorInicio);
  // Código para pasar el número a un entero
  int numero = String(valorInicio).toInt();
  switch (valorInicio){
    case 'a':
      numero=10;
      break;
    case 'b':
      numero=11;
      break;
    case 'c':
      numero=12;
      break;
    case 'd':
      numero=13;
      break;
    case 'e':
      numero=14;
      break;
    case 'f':
      numero=15;
      break;
  }
  // Agrupar los Bytes que toca coger para la combinación desde el grupo que dicen los últimos
  // 4 bits. Va desde 0 (valor HEX 0) a 15 (valor HEX f). 
  String combinacion;
  combinacion += total[numero*2];
  combinacion += total[numero*2+1];
  combinacion += total[numero*2+2];
  combinacion += total[numero*2+3];
  combinacion += total[numero*2+4];
  combinacion += total[numero*2+5];
  combinacion += total[numero*2+6];
  combinacion += total[numero*2+7];
  char salidaCombinacion[7];
  combinacion.toCharArray(salidaCombinacion,sizeof(salidaCombinacion));
  long respuestaFinal = strtol(salidaCombinacion, NULL, 16);
  Serial.print("Valor de la combinación en hexadecimal: ");Serial.println(salidaCombinacion);
  Serial.print("Valor previo a conversión: ");Serial.println(respuestaFinal);

  
  int numero_digitos = floor(log10(respuestaFinal)) + 1;
  while (numero_digitos < 8){
    respuestaFinal *= 10;
    numero_digitos = floor(log10(respuestaFinal)) + 1;
  }
   Serial.print("Valor válido para introducir como combinación: ");Serial.println(respuestaFinal);
   // Encender el LED
   digitalWrite(13, HIGH);
   delay(10000);
   digitalWrite(13, LOW);
   delay(10000);
}

void loop() {
  
}