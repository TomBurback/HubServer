#include <string.h>

void setup() {
  //Open serial port with 9600 baud
  Serial.begin(9600);
  //set all digital pins to output
  for(int i = 0; i <= 13; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  Serial.println("Setup completed!\n");
}

void loop() {
  int serial_in = 0;
  while(Serial.available()) {
    serial_in = Serial.read();
  }
  switch(serial_in) {
    case '0':
      digitalWrite(8, LOW);
      break;
    case '1':
      digitalWrite(8, HIGH);
      break;
  }
}
