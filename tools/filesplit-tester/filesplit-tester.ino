#include "C:\Users\Evan\Documents\RobotX\ENADD\lib\robotx-ultrasonic-driver.h"

UltrasonicSensorHCSR04 us(4,2);

void setup() {
	Serial.begin(9600);
	pinMode(4, OUTPUT);
}

void loop() {
    int dist = us.getDistance();
	if(dist >= 0) Serial.println( dist );
}
