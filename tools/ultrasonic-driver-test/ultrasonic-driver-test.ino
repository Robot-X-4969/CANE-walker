#include "robotx-ultrasonic-driver.h"

UltrasonicSensorHCSR04 us(4,2);

void setup() {
	Serial.begin(9600);
	pinMode(4, OUTPUT);
}

void loop() {
	int dist = us.getDistance();
	delayMicroseconds(100);
	if(dist != -1) {
		Serial.println( dist );
		delay(100);
	}
}
