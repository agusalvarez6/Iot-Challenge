#include <HCSR04.h>

UltraSonicDistanceSensor distanceSensor1(26, 33);  // Primer par de pines.
UltraSonicDistanceSensor distanceSensor2(25, 32);  // Segundo par de pines.

bool sensor1Active = false;


const int sensorPin = 25;            // Pin del sensor
const int sensorPin2 = 26;  
const unsigned long minInterval = 100; // Intervalo mínimo entre eventos en ms
unsigned long lastEventTime = 0;     // Último tiempo en el que se detectó un evento
bool lastSensorState = HIGH;         // Estado anterior del sensor

char command;
bool est=false;
void setup() {
    Serial.begin(115200);  // Inicializamos la conexión serial para poder imprimir los valores del sensor.
    
    // Probar los dos pares de pines y seleccionar el par activo
    float distance1 = distanceSensor1.measureDistanceCm();
    if (distance1 > 0) {
        sensor1Active = true;
        command = 'A' ;
        est=true;
    } else {
        float distance2 = distanceSensor2.measureDistanceCm();
        if (distance2 > 0) {
            sensor1Active = false;
            command = 'A' ;
            est=true;
        } else {
            //Serial.println("Error: No se puede detectar el sensor en ninguno de los pares de pines.");
            //while (true);  // Detener el programa si no se puede detectar el sensor.
            pinMode(sensorPin, INPUT);
            pinMode(sensorPin2, INPUT);
            command = 'P' ;
        }
    }
}
float conversionFactor = 0.000625; 
void loop() {
  if (Serial.available()) {
    char aux=Serial.read();
    if(aux == 'A' || aux == 'P'|| aux == 'H')
        command = aux;
    
  }
  
        //Serial.print("Comando recibido: ");
        //Serial.println(command);
        if (command == 'A') {
          if(est=false){
            esp_restart();  
          }
              float distance;
        
            if (sensor1Active) {
                distance = distanceSensor1.measureDistanceCm();
            } else {
                distance = distanceSensor2.measureDistanceCm();
            }
            
            // Verifica si la lectura es válida
            if (distance > 0) {
                Serial.println(distance);  // Imprime la distancia en centímetros.
            } else {
                Serial.println("Error");  // Imprime "Error" si la lectura no es válida.
                est=false;
                esp_restart();  
            }
        }else if (command == 'P') {
             bool currentSensorState = digitalRead(sensorPin) ||digitalRead(sensorPin2);
              unsigned long currentTime = millis();

              // Detectar un cambio en el estado del sensor
              if (lastSensorState == HIGH && currentSensorState == LOW) {
                // Si ha pasado el intervalo mínimo desde el último evento
                if (currentTime - lastEventTime >= minInterval) {
                  Serial.println("1"); // Imprime '1' cuando el péndulo pasa rápidamente
                  lastEventTime = currentTime; // Actualiza el tiempo del último evento
                }
              }

              // Actualiza el estado del sensor
              lastSensorState = currentSensorState;
        }else if (command == 'H') {
          int analogValue = analogRead(34);
          float magneticField_Tesla = analogValue * conversionFactor;

            // Convertir el valor de Tesla a miliTesla
            float magneticField_mT = magneticField_Tesla * 1000;
            Serial.println(magneticField_mT);
        }
    
    delay(30);  // Ajusta este valor si es necesario para tu aplicación.
}


