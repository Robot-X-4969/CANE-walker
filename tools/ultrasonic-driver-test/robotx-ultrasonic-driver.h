#include "Arduino.h"

const long PING_TIMEOUT = 50000;

long microsToCm(long t);

class UltrasonicSensorHCSR04 {
    public:
        UltrasonicSensorHCSR04(int trigger, int pin);
        ~UltrasonicSensorHCSR04();
        int getDistance();
		bool refresh();
    private:
		enum ListenMode { INIT, WAIT_FOR_START, WAIT_FOR_END };
		ListenMode currentMode;
		int trigger, echo, distance;
		long tStart;
        void ping();
};


UltrasonicSensorHCSR04::UltrasonicSensorHCSR04(int pinTrig, int pinEcho) {
    trigger = pinTrig;
    echo = pinEcho;
    tStart = distance = 0;
	currentMode = INIT;
}
UltrasonicSensorHCSR04::~UltrasonicSensorHCSR04() { }

int UltrasonicSensorHCSR04::getDistance() {
	return distance;
}

bool UltrasonicSensorHCSR04::refresh() {
	bool isDone = false;
	switch (currentMode) {
		case INIT:
			ping();
			currentMode = WAIT_FOR_START;
			break;
		case WAIT_FOR_START:
			if(digitalRead(echo) == HIGH) {
				tStart = micros();
                currentMode = WAIT_FOR_END;
            }
            break;
		case WAIT_FOR_END:
			long elapsed = micros()-tStart;
            if(digitalRead(echo) == LOW) {
				distance = (int) microsToCm( elapsed );
                currentMode = INIT;
				isDone = true;
            } else if(elapsed > PING_TIMEOUT) {
                currentMode = INIT;
				isDone = true;
            }
	}
	return isDone;
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
