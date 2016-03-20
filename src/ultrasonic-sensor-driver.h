#define UltrasonicDriver_h

#ifndef Arduino_h
	#include "Arduino.h"
#endif
#ifndef AsynchronousTask_h
	#include "asynchronous-task.h"
#endif
#ifndef BufferedArray_h
	#include "buffered-array.h"
#endif


#define MICROS_PER_CM 58.82

class UltrasonicSensor;
class UltrasonicSenseTask;

int microsToCm(long t);
long cmToMicros(int cm);


class UltrasonicSensor
{
	public:
		int pinTrigger, pinEcho, distance;
		UltrasonicSensor(int trig, int echo, int maxDistCm);
		void init();
		void ping();
		UltrasonicSenseTask& senseTask;
	private:
		BufferedArray distBuffer = new BufferedArray(3);
};

UltrasonicSensor::UltrasonicSensor(int trig, int echo, int maxDistCm) {
	pinTrigger = trig;
	pinEcho = echo;
	distance = 0;
	UltrasonicSenseTask temp(maxDistCm);
	senseTask = temp;
}

void UltrasonicSensor::init() {
	pinMode(pinTrigger, OUTPUT);
	pinMode(pinEcho, INPUT);
}

void UltrasonicSensor::ping() {
	digitalWrite(pinTrigger, LOW);
	delayMicroseconds(5);
	digitalWrite(pinTrigger, HIGH);
	delayMicroseconds(10);
	digitalWrite(pinTrigger, LOW);
}




class UltrasonicSenseTask: public AsynchronousTask, private UltrasonicSensor
{
	public:
		UltrasonicSenseTask(int maxDistCm);
	private:
		long tStart, pingTimeout;
		long elapsedTime();
	protected:
		bool initialize();
		bool workToCompletion();
};

UltrasonicSenseTask::UltrasonicSenseTask(int maxDistCm) {
	tStart = micros();
	pingTimeout = cmToMicros( maxDistCm+5 );
}

long UltrasonicSenseTask::elapsedTime() {
	return micros()-tStart;
}

bool UltrasonicSenseTask::initialize() {
	bool out = (digitalRead(pinEcho) == HIGH);
	if(out) {
		tStart = micros();
	}
	return out;
}

bool UltrasonicSenseTask::workToCompletion() {
	if(digitalRead(sensor->pinEcho) == LOW) {
		sensor->distance = microsToCm( elapsedTime() );
		return true;
	} else if(elapsedTime() > pingTimeout) {
		sensor->distance = 0;
		return true;
	} else {
		return false;
	}
}




double microsToCm(long t) {
    return ( (double)t / MICROS_PER_CM );
}

long cmToMicros(double cm) {
	return (long)(cm * MICROS_PER_CM);
}
