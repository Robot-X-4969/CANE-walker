#define HCSR04SenseTask 

#ifndef Arduino_h
	#include "Arduino.h"
#endif
#ifndef AsynchronousTask
	#include "asynchronous-task.h"
#endif

long microsToCm(long t);

class HCSR04SenseTask: public AsynchronousTask {
    public:
        HCSR04SenseTask(int pinTrig, int pinEcho);
		void initSensor();
		void resetDistance();
        int getDistance();
		bool refresh();
		void ping();
    private:
		const long PING_TIMEOUT_MICROS = 50000;
		int trigger, echo, distance, currentMode;
		long tStart;
		long elapsedTime();
};


UltrasonicSensorHCSR04::UltrasonicSensorHCSR04(int pinTrig, int pinEcho) {
    trigger = pinTrig;
    echo = pinEcho;
    tStart = distance = 0;
    resetDistance();
}
UltrasonicSensorHCSR04::~UltrasonicSensorHCSR04() { }

void UltrasonicSensorHCSR04::initSensor() {
	pinMode(trigger, OUTPUT);
	pinMode(echo, INPUT);
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
            } else if(elapsedTime() > PING_TIMEOUT_MICROS) {
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
