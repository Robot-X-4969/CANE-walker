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
#define N_US_SENSORS 6

#define FOREACH_US for(int i = 0; i < N_US_SENSORS; i++)


// ************* GLOBAL VARS *********** //
UltrasonicSensorHCSR04 us[] = {
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_LEFT_SIDE),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_LEFT_MID),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_LEFT_FRONT),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_RIGHT_FRONT),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_RIGHT_MID),
	UltrasonicSensorHCSR04 (TRIGGER, USPIN_RIGHT_SIDE)
};

bool scanCompleted[N_US_SENSORS];


// ************* HELPER FUNCTIONS ********** //

bool allDistancesFound() {
	bool out = true;
	//Serial.print("dist found: ");
	for(int i = 0; i < N_US_SENSORS; i++) {
		out = out && scanCompleted[i];
		//Serial.print( scanCompleted[i] );
		//Serial.print(", ");
	}
	//Serial.print(" -> ");
	//Serial.println(out);
	return out;
}




// ************** MAIN PROGRAM ************** //

void setup() {
	Serial.begin(9600);
	FOREACH_US { us[i].initSensor(); }
	//Serial.println("setup complete, start pinging");
	us[0].ping();
}

void loop() {
	
	FOREACH_US {
		scanCompleted[i] = us[i].refresh();
	}
	
	delayMicroseconds(50);

	if(allDistancesFound()) {
	//if(scanCompleted[i]) {
		FOREACH_US {
			Serial.print(us[i].getDistance());
			Serial.print(", ");
			us[i].resetDistance();
		}
		Serial.println();
		delay(500); //wait for echoes to clear
		us[0].ping();
	}


}

/*UltrasonicSensorHCSR04 ustest (4, 2);

void setup() {
	Serial.begin(9600);
	ustest.initSensor();
	ustest.ping();
}

void loop() {
//	if(ustest.refresh()) {
//		Serial.println( ustest.getDistance() );
//		delay(100);
//		ustest.resetDistance();
//		ustest.ping();
//	}
//	delayMicroseconds(50);
	Serial.println(ustest.refresh());
	delay(10);
}*/
