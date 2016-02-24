#include "robotx-ultrasonic-driver.h"

UltrasonicSensorHCSR04 us (30,22);

void setup() {
  Serial.begin(9600);
}

void loop() {
	Serial.println("something");
    int dist;
    do { dist = us.getDistance(); } while( dist == -1);
    Serial.println(dist);
    delay(500);
}
