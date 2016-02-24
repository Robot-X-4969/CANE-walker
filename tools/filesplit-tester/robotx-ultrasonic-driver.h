#include "Arduino.h" 

const int PING_TIMEOUT = 5000;
int microsToCm(int t);
class UltrasonicSensorHCSR04 {
    int trigger, echo, state;
	long tStart;
    public:
        UltrasonicSensorHCSR04(int trigger, int pin);
        ~UltrasonicSensorHCSR04();
        int getDistance();
    private:
        void ping();
};


UltrasonicSensorHCSR04::UltrasonicSensorHCSR04(int pinTrig, int pinEcho) {
    trigger = pinTrig;
    echo = pinEcho;
    tStart = state = 0;
}
UltrasonicSensorHCSR04::~UltrasonicSensorHCSR04() { }

int UltrasonicSensorHCSR04::getDistance() {
    switch(state) {
		case 0: //send signal
			ping();
			state++;
        case 1: //wait for high signal to start
            if(digitalRead(echo) == HIGH) {
                state++;
                tStart = micros();
            }
            return -1;
		case 2: //wait for pulse to complete
            int elapsed = (int)(micros()-tStart);
            if(digitalRead(echo) == LOW) {
                state = 0;
				return microsToCm( elapsed ); 
            } else if(elapsed > PING_TIMEOUT) {
                state = 0;
                return 0;
            } else {
                return -1;
            }
    }
}

void UltrasonicSensorHCSR04::ping() {
    digitalWrite(trigger, LOW);
    delayMicroseconds(5);
    digitalWrite(trigger, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigger, LOW);
}

int microsToCm(int t) {
    return t / 38;
}
