int trigger = 30;

void setup() {
  pinMode(trigger, OUTPUT);
  Serial.begin(9600);
}

void loop() {
    for(int echo = 22; echo <= 27; echo++) {
      int data = microsToCm( ping( echo ));
      Serial.print( data ); Serial.print("\t");
    }
    Serial.println();
    delay(500); 
}


long ping(int echo) {
  //digitalWrite(trigger, LOW);
  //delayMicroseconds(5);
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  //digitalWrite(trigger, LOW);
  long time = pulseIn(echo, HIGH, 50000);
  return time;
}

long microsToInches(long t){
  return t / 73.5 / 2;
}
long microsToCm(long t){
  return t / 29 / 2;
}

