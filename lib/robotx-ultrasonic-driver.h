#ifndef Arduino_h
	#include "Arduino.h"
#endif

#define PING_TIMEOUT 50000

#define MODE_WAIT_FOR_START 1
#define MODE_WAIT_FOR_END 	2
#define MODE_DONE 			3

long microsToCm(long t);

class UltrasonicSensorHCSR04 {
    public:
        UltrasonicSensorHCSR04(int trigger, int pin);
        ~UltrasonicSensorHCSR04();
		void initSensor();
		void resetDistance();
        int getDistance();
		bool refresh();
		void ping();
    private:
		int trigger, echo, distance, currentMode;
		long tStart;
		long elapsedTime();
};


UltrasonicSensorHCSR04::UltrasonicSensorHCSR04(int pinTrig, int pinEcho) {
    trigger = pinTrig;
    echo = pinEcho;
    tStart = distance = 0;
}
UltrasonicSensorHCSR04::~UltrasonicSensorHCSR04() { }

void UltrasonicSensorHCSR04::initSensor() {
	pinMode(trigger, OUTPUT);
	pinMode(echo, INPUT);
	resetDistance();
}

void UltrasonicSensorHCSR04::resetDistance() {
	distance = 0;
	currentMode = MODE_WAIT_FOR_START;
}

long UltrasonicSensorHCSR04::elapsedTime() {
	return micros()-tStart;
}

int UltrasonicSensorHCSR04::getDistance() {
	return distance;
}

bool UltrasonicSensorHCSR04::refresh() {
	long elapsed = 0;
	switch (currentMode) {
		case MODE_WAIT_FOR_START:
			if(digitalRead(echo) == HIGH) {
				tStart = micros();
                currentMode = MODE_WAIT_FOR_END;
            }
            break;
		case MODE_WAIT_FOR_END:
            if(digitalRead(echo) == LOW) {
				distance = (int) microsToCm( elapsedTime() );
				currentMode = MODE_DONE;
            } else if(elapsedTime() > PING_TIMEOUT) {
				distance = 0;
                currentMode = MODE_DONE;
            }
			break;
		case MODE_DONE:
			//nothing needed
			break;
	}
	return currentMode == MODE_DONE;
}

void UltrasonicSensorHCSR04::ping() {
    digitalWrite(trigger, LOW);
    delayMicroseconds(5);
    digitalWrite(trigger, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigger, LOW);
}

long microsToCm(long t) {
    return (long)( (double)t / 38.0 );
}
