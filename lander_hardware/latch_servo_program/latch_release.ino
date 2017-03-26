#include <Servo.h>
Servo servo;

void setup() {

  servo.attach(7);

}

void loop() {

  servo.write(150);
  delay(200);

  servo.write(100);
  delay(9999);

}
