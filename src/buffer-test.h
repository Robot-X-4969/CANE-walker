#include "buffered-array.h"

BufferedArray buff(10);
int n;

void printBufferDebugLine(BufferedArray b);

void setup() {
	Serial.begin(9600);
	n = 15;
}

void loop() {
	n--;
	buff.push(n);
	
	Serial.print("BufferedArray: ");
	printBufferDebugLine(buff);
	
	Serial.print("mean: ");
	Serial.println(buff.mean());
	
	Serial.print("median: ");
	Serial.println(buff.median());
	
	Serial.print("sorted: ");
	printBufferDebugLine(buff.getSortedBuffer());
	
	Serial.print("trimming 3: ");
	printBufferDebugLine(buff.getTrimmedBuffer(3));
	
	Serial.println();
	delay(500);
}

void printBufferDebugLine(BufferedArray b) {
	for(int i = 0; i < b.getSize(); i++) {
		Serial.print((int)b.get(i));
		Serial.print(", ");
	}
	Serial.println();
}
