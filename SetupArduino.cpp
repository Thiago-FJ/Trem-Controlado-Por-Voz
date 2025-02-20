#include <SoftwareSerial.h>


// Configuração dos pinos Bluetooth (RX=0, TX=1)
SoftwareSerial bluetooth(0, 1);


// Definição do pino do motor


// Definição do PWM mínimo necessário para evitar travamentos
const int PWM_MINIMO = 50;  // Ajuste esse valor conforme necessário


void setup() {
    Serial.begin(9600);    // Comunicação serial para debug
    bluetooth.begin(9600); // Bluetooth


    pinMode(11, OUTPUT);
    analogWrite(11, 0);  // Inicia com motor desligado
    pinMode(10, OUTPUT);
    analogWrite(10, 0);  // Inicia com motor desligado
}


void loop() {
    if (bluetooth.available()) {
        String volumeStr = bluetooth.readStringUntil('\n');  // Lê até quebra de linha
        int volume = volumeStr.toInt();  // Converte para inteiro
       
        if (volume < 0 || volume > 100) return;  // Ignora valores inválidos


        // Converte volume (0-100) para PWM (50-255 para evitar travamentos)
        int pwmValue = map(volume, 0, 100, PWM_MINIMO, 255);
        if (volume == 0) pwmValue = 0;  // Garante que 0 desliga o motor


        analogWrite(11, pwmValue); // Ajusta a velocidade do motor
        analogWrite(10, pwmValue); // Ajusta a velocidade do motor
    }
}
