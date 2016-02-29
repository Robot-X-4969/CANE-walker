#ifndef Arduino_h
	#include "Arduino.h"
#endif
#include "robotx-ultrasonic-driver.h"

// ************** DEFINES ************** //
#define TRIGGER 30

#define USPIN_LEFT_SIDE 22
#define USPIN_LEFT_MID 23
#define USPIN_LEFT_FRONT 24
#define USPIN_RIGHT_FRONT 25
#define USPIN_RIGHT_MID 26
#define USPIN_RIGHT_SIDE 27

#define FOREACH_US for(int i = 0; i < nUltrasonicSensors; i++)


// ************* GLOBAL VARS *********** //
UltrasonicSensorHCSR04 us[] = {
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_LEFT_SIDE),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_LEFT_MID),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_LEFT_FRONT),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_RIGHT_FRONT),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_RIGHT_MID),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_RIGHT_SIDE)
};

const int nUltrasonicSensors = sizeof(us) / sizeof(us[0]);
bool scanCompleted[nUltrasonicSensors];


// ************* HELPER FUNCTIONS ********** //

bool noneFalse(bool arr[]) {
	bool out = true;
	for(int i = 0; i < sizeof(arr)/sizeof(arr[0]); i++) {
		out = out && arr[i];
	}
	return out;
}



// ************** MAIN PROGRAM ************** //

void setup() {
	Serial.begin(9600);
	FOREACH_US { us[i].initSensor(); }
}

void loop() {

	FOREACH_US {
		scanCompleted[i] = us[i].refresh();
	}
	
	if(noneFalse(scanCompleted)) {
		FOREACH_US {
			Serial.print(us[i].getDistance());
			Serial.print("\t");
		}
		Serial.println();
	}

	delayMicroseconds(100);
}
