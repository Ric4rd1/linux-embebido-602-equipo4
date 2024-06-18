#include <Servo.h>
#include <DHT.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <EasyBuzzer.h>

Servo door;
DHT dht(2,DHT11);
const int light1Pin = 8;
const int light2Pin = 7;
const int light3Pin = 6; 
const int buttonPin = 11;
LiquidCrystal_I2C lcd(0x27,16,2);  //


/*######### PIN CONFIGURATION #########*/
/*ServoMotor on PIN 9                  */
/*DHT Temperature sensor PIN 2         */
/*LED on PIN 8,7,6                     */
/*LCD display SDA A4, SCL A5           */
/*Buzzer on PIN5                       */
/*Push Button on PIN 11                */

void setup() {
  Serial.begin(115200);

  // Servo Motor
  door.attach(9); // Assign Pin 9
  door.write(0); // Starting position 0

  // DHT Sensor
  dht.begin();

  // LEDs
  pinMode(light1Pin , OUTPUT);
  pinMode(light2Pin , OUTPUT);
  pinMode(light3Pin , OUTPUT);

  // LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("       TV       ");
  lcd.setCursor(0, 1);
  lcd.print("       OFF         ");

  //Buzzer
  EasyBuzzer.setPin(5);
  EasyBuzzer.update();

  // Button
  pinMode(buttonPin, INPUT_PULLUP);

  while(!Serial.available());
  //Serial.println("Initializing...");

}

byte calculateCRC(String data) {
  byte crc = 0x00;
  for (int i = 0; i < data.length(); i++) {
    crc ^= data[i];
    for (int j = 0; j < 8; j++) {
      if (crc & 0x01) {
        crc = (crc >> 1) ^ 0x8C; // Polynomial 0x8C for CRC-8
      } else {
        crc >>= 1;
      }
    }
  }
  return crc;
}

String serialTemperature(char unit, float temperature){
  if (unit == 'F') {
    // Convert Celsius to Fahrenheit if requested
    temperature = temperature * 9.0;
    temperature /= 5.0;
    temperature += 32;
    }

    String formattedTemperature = String(temperature,2);
    // Calculate CRC for the response
    String response = "RT" + formattedTemperature + unit;
    byte crc = calculateCRC(response);
    // Send the response with CRC
    response += String(crc, HEX);
    return response;
}
void openDoor(){
  door.write(90);
}

void closeDoor(){
  door.write(0);
}

void lightsOn(){
  digitalWrite(light1Pin , HIGH);
  digitalWrite(light2Pin , HIGH);
  digitalWrite(light3Pin , HIGH);
}

void lightsOff(){
  digitalWrite(light1Pin , LOW);
  digitalWrite(light2Pin , LOW);
  digitalWrite(light3Pin , LOW);
}

void tvOn(){
  lcd.clear();
  lcd.print("       TV       ");
  lcd.setCursor(0, 1);
  lcd.print("       ON         ");
}

void tvOff(){
  lcd.clear();
  lcd.print("       TV       ");
  lcd.setCursor(0, 1);
  lcd.print("       OFF         ");
}

void alarm(){
  EasyBuzzer.beep(
  400,		// Frequency in hertz(HZ).
  100, 		// On Duration in milliseconds(ms).
  100, 		// Off Duration in milliseconds(ms).
  4, 		// The number of beeps per cycle.
  50, 	// Pause duration.
  1 		// The number of cycles
  );
  String response = "RB";
  Serial.println(response);
}

String received=""; // String buffer
char instruction = '0'; // Instruction code

void loop() {
  float celsius_degrees = dht.readTemperature();
  EasyBuzzer.update();
  int buttonState = digitalRead(buttonPin);

  if (buttonState == LOW) {
    while (digitalRead(buttonPin) == LOW); // Wait unpress
    alarm();  // Call the function when the button is pressed
  }

  // Send data when data is recieved
  while(Serial.available()>0){
    // Read incoming byte
    char c = Serial.read();
    received+=c;
    delay(5);
  }
  
  if (received!=""){
    instruction = received[0];
    if(received.length() >= 2 && 
        (instruction == 'T'||
        instruction == 'S'||
        instruction == 'B'||
        instruction == 'L'||
        instruction == 'D')){

      // Print received data for debugging
      // Serial.print("Received: ");
      // Serial.println(received);
      
      // Select instruction to execute
      // Serial.print("Instruction: ");
      // Serial.println(instruction);

        if (instruction == 'T'){  // Temperature
          char unit = received[1]; // 'C' or 'F'

          String response = serialTemperature(unit, celsius_degrees);
          Serial.println(response);

        }else if (instruction == 'S'){ // Servomotor (Door)
          char state = received[1]; // '1' open, '2' close

          if (state == '1'){
            openDoor();
          } else if(state == '0'){
            closeDoor();
          }
          String response = "RS"+String(state);
          Serial.println(response);
        }else if(instruction == 'L'){  // LED (Lights)
          char state = received[1]; // '1' ON, '2' OFF

          if (state == '1'){
            lightsOn();
          } else if(state == '0'){
            lightsOff();
          }
          String response = "RL"+String(state);
          Serial.println(response);
        }else if(instruction == 'D'){  // LCD Display (TV)
          char state = received[1]; // '1' ON, '2' OFF

          if (state == '1'){
            tvOn();
          } else if(state == '0'){
            tvOff();
          }
          String response = "RD"+String(state);
          Serial.println(response);
        }else if (instruction == 'B'){
          alarm();
        }
      

    } else {
      // Handle incorrect commands
      String response = "E-1";
      byte crc = calculateCRC(response);
      response += String(crc, HEX);
      Serial.println(response);
    }
    received = "";
  }
  delay(50);
}
