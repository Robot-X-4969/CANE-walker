
//pins
const int trigger = 30;
const int usEcho[] = {22, 23, 24, 25, 26, 27}; //left side across front to right side
const int vibs[] = {2, 3, 4, 5}; 
const int sounds[] = {40, 41, 42, 43}; //1,2,3,4 on sound card; corresponds with bl,fl,fr,br sounds
const int dropoffSound[] = {44, 45}; //5 and 6 on sound card
const int irReturn[] = {A0, A2};
const int irTogglePinOut = 50, irTogglePinIn = 53;

//presets
const int offset[] = {5, 20, 25, 25, 20, 5};
const int maxDist[] = {100, 125, 300, 300, 125, 100};
const float blipsBaseline = 0.25;
const float blipsUrgent = 5.0;
const int soundSendMicros = 6500;
const long vibTimeMillis = 70;
const float irSpikeLimit = 0.4; //TODO find this value, should be around 0.1?
const int irSpikeConsecutiveLimit = 10;

//global variable declarations
int dist[6][3];
float irData[2][8];
float irDist[2][10]; //if 8 of 10 are above limit, signal dropoff
float irDistBaseline[2];
long resetTime[4];
float freqRaw[6], freqCombined[4];
long lastIrCalibrationTime;
//float bigIrDist[2][100];
//int nextIrHistoryIndex[2];
boolean irToggleState;


void setup() {
  Serial.begin(9600);
  analogReference(INTERNAL1V1);
  //analogReference(DEFAULT);
  
  delay(2000); // wait for 2F*5.5V to transfer
  
  pinMode(trigger, OUTPUT);
  //for(int i = 0; i < 6; i++){
  //  pinMode(usEcho[i], INPUT);
  //}
  for(int i = 0; i < 4; i++){
    pinMode(vibs[i], OUTPUT);
  }for(int i = 0; i < 4; i++){
    pinMode(sounds[i], OUTPUT);
  }
  pinMode(dropoffSound[0], OUTPUT);
  pinMode(dropoffSound[1], OUTPUT);
  
  irToggleState = getIRToggleState();
  Serial.print("IR Toggle State = "); Serial.println( irToggleState );
  
  if(irToggleState) {
    //set baseline IR value
    recalibrate();
  }
  /*float total0 = 0.0, total1 = 0.0;
  for(int i = 0; i < 50; i++) {
    delayMicroseconds( 40000 ); //40 ms
    total0 += float( irToCm( analogRead(irReturn[0]) ) ); 
    total1 += float( irToCm( analogRead(irReturn[1]) ) );
  }
  irDistBaseline[0] = total0 / 50.0;
  irDistBaseline[1] = total1 / 50.0;
  Serial.print(irDistBaseline[0]); Serial.print("  "); Serial.println(irDistBaseline[1]);
  lastIrCalibrationTime = millis();
  nextIrHistoryIndex[0] = nextIrHistoryIndex[1] = 0;*/
  
  //initialize other values
  for(int i = 0; i < 4; i++) {
    resetTime[i] = millis();
  } for(int i = 0; i < 6; i++) {
    addDistEntry(i, getDistance(usEcho[i], trigger));
    freqRaw[i] = blipsFreq( (float)getClosestDistToAvg(i), offset[i], maxDist[i], blipsBaseline, blipsUrgent);
    getIRData(0);
    getIRData(1);
  }
  updateCombinedFrequencies();
  
}

void loop() {
  //long start, time;
  //start = millis();
  for(int i = 0; i < 6; i++){
    addDistEntry( i, getDistance(usEcho[i], trigger) );
    freqRaw[i] = blipsFreq( (float)getClosestDistToAvg(i), offset[i], maxDist[i], blipsBaseline, blipsUrgent);
    updateCombinedFrequencies();
    if(irToggleState) {
      getIRData(0);
      getIRData(1);
      addIRDistEntry(0, irToCm( correctedIRRawVal(0) ));
      addIRDistEntry(1, irToCm( correctedIRRawVal(1) ));
      
      if( millis()-lastIrCalibrationTime > 30000 ) {
        if( (dist[2][2] > 100 || dist[2][2] == 0) && (dist[3][2] > 100 || dist[3][2] == 0) ){
          recalibrate();
        } else {
          Serial.println("Calibration blocked by obstacle");
          lastIrCalibrationTime += 10000;
        }
      }
    }
    
    runUI();
    
    if(irToggleState != getIRToggleState()) {
      irToggleState = !irToggleState;
      Serial.print("switching ir toggle to "); Serial.println(irToggleState);
    }
  }
  //time = millis() - start;
  
  for(int i = 0; i < 6; i++){
    //Serial.print( dist[i][2] ); Serial.print("\t");
    //Serial.print( freqRaw[i] ); Serial.print("\t");
  }
  if(irToggleState) {
    Serial.print(irDist[0][9]);
    Serial.print("\t");
    Serial.print(irDist[1][9]);
    Serial.println();
  }
}



void runUI()
{
  long elapsed; float target; boolean anyActive = false;
  if(irToggleState) {
    int dropoffCount0 = 0, dropoffCount1 = 0;
    for(int i = 0; i < 10; i++) {
      if( irDist[0][i] > irDistBaseline[0] + irSpikeLimit )
        dropoffCount0++;
      if( irDist[1][i] > irDistBaseline[1] + irSpikeLimit )
        dropoffCount1++;
    }
    if( dropoffCount0 >= irSpikeConsecutiveLimit ) {
      Serial.println("DROPOFF LEFT");
      digitalWrite(dropoffSound[0], HIGH);
    }
    if( dropoffCount1 >= irSpikeConsecutiveLimit ) {
      Serial.println("DROPOFF RIGHT");
      //digitalWrite(dropoffSound[0], HIGH);
      digitalWrite(dropoffSound[1], HIGH);
    }
    if( dropoffCount0 >= irSpikeConsecutiveLimit || 
        dropoffCount1 >= irSpikeConsecutiveLimit ) {
      delayMicroseconds(soundSendMicros);
      digitalWrite(dropoffSound[0], LOW);
      digitalWrite(dropoffSound[1], LOW);
      delay(4000);
      for(int i = 0; i < 10; i++) irDist[0][i] = irDist[1][i] = 0.0;
    }
  }
  for(int i = 0; i < 4; i++) {
    elapsed = millis() - resetTime[i];
    target = 1000.0 / freqCombined[i];
    if(elapsed > target) {
      anyActive = true;
      //analogWrite(vibs[i], 255);
      //Serial.println("beep");
      digitalWrite(sounds[i], HIGH);
      //the WAV trigger only samples its triggers every few milliseconds
      delayMicroseconds(soundSendMicros); 
      digitalWrite(sounds[i], LOW);
      resetTime[i] = millis(); //reset this tone's "timer"
    }
  }
  //if(anyActive) delay( vibTimeMillis );
  for(int i = 0; i < 4; i++)
    analogWrite( vibs[i], 0 );
}




void ping(int t) {
  digitalWrite(trigger, LOW);
  delayMicroseconds(5);
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigger, LOW);
}
int getDistance(int pin, int trig) {
  ping(trig); //sends out distance signal
  long time = pulseIn(pin, HIGH, 28000); //26100 microsecs for 450cm (claimed range)
  delayMicroseconds(1500); //wait for sound to clear
  return (int)(microsToCm(time));
}

long microsToCm(long t)
{
  return t / 58;
}

float blipsFreq(float distance, float minCm, float maxCm, float minFreq, float maxFreq) {
  if(distance >= minCm && distance <= maxCm){
    //return maxFreq - (maxFreq-minFreq)/((float)(maxCm-minCm))*((float)(distance-minFreq));
    //Serial.print(distance); Serial.print(" "); Serial.print(minCm); Serial.print(" "); Serial.print(maxCm); Serial.print(" ");
    //Serial.print(minFreq); Serial.print(" "); Serial.println(maxFreq);
    float fact1 = maxFreq-minFreq;
    //Serial.print("fact1: "); Serial.println(fact1);
    float posDiff = abs(distance-maxCm);
    float fact2 = pow(posDiff, 2.4);
    //Serial.print("fact2: "); Serial.println(fact2);
    float divisor = pow(maxCm-minCm, 2.4);
    //Serial.print("divisor: "); Serial.println(divisor);
    float result = (fact1*fact2) / divisor + minFreq;
    //Serial.print("result: "); Serial.println(result);
    return result;
  }else if(distance < minCm && distance != 0){
    return maxFreq;
  }else{
    return 0.01;
  }
}

void updateCombinedFrequencies(){
  freqCombined[0] = freqRaw[0] + 0.5*freqRaw[1];
  freqCombined[1] = freqRaw[2] + 0.5*freqRaw[1];
  freqCombined[2] = freqRaw[3] + 0.5*freqRaw[4];
  freqCombined[3] = freqRaw[5] + 0.5*freqRaw[4];
}

void addDistEntry(int s, int val){
  dist[s][0] = dist[s][1];
  dist[s][1] = dist[s][2];
  dist[s][2] = val;
}
void addIRDistEntry(int s, float val) {
  irDist[s][0] = irDist[s][1];
  irDist[s][1] = irDist[s][2];
  irDist[s][2] = irDist[s][3];
  irDist[s][3] = irDist[s][4];
  irDist[s][4] = irDist[s][5];
  irDist[s][5] = irDist[s][6];
  irDist[s][6] = irDist[s][7];
  irDist[s][7] = irDist[s][8];
  irDist[s][8] = irDist[s][9];
  irDist[s][9] = val;
  
  //bigIrDist[s][nextIrHistoryIndex[s]] = val;
  //nextIrHistoryIndex[s]++;
  //if(nextIrHistoryIndex[s] >= 100) nextIrHistoryIndex[s] = 0;
}

int getClosestDistToAvg(int s) {
  int avg = (dist[s][0] + dist[s][1] + dist[s][2]) / 3;
  int closest = 0;
  for(int i = 0; i < 3; i++) //the resetTime 3 sensed values
    if( abs(dist[s][i]-avg) < abs(dist[s][closest]-avg) )
      closest = i;
  return dist[s][closest];
}

boolean boolArrayContainsTrue(boolean arr[]) {
  for(int i = 0; i < (sizeof(arr)/sizeof(arr[0])); i++) {
    if(arr[i]) return true;
  }
  return false;
}

void getIRData(int s) {
  for(int i = 0; i <= 6; i++) {
    irData[s][i] = irData[s][i+1];
  }
  irData[s][7] = float(analogRead( irReturn[s] ));
}

float correctedIRRawVal(int s) {
  float total = 0.0;
  float irDataSort[8];
  for(int i = 0; i < 8; i++) {
    total += irData[s][i];
    irDataSort[i] = irData[s][i];
  }
  float avg1 = total / 8.0;
  
  for(int a = 0; a < 7; a++) { //selection sort; index 0 is the closest
    int closest = 0;
    for(int i = a; i < 8; i++) {
      float thisDiff = abs( irDataSort[i] - avg1 );
      float bestDiff = abs( irDataSort[closest] - avg1 );
      if( thisDiff < bestDiff ) {
        closest = i;
      }
    }
    float temp = irDataSort[closest];
    irDataSort[closest] = irDataSort[a];
    irDataSort[a] = temp;
    //Serial.print(irDataSort[a]); Serial.print("  ");
  } //should now be sorted
  //Serial.println();
  
  total = 0.0;
  for(int i = 0; i < 5; i++) total += irData[s][i];
  float avg2 = total / 5.0;
  return avg2;
}

float irToCm(float raw) {
  return 549.0/raw;
  //return 400.0 / raw;
}

void recalibrate() {
  Serial.print("RECALIBRATING IRs  ");
  
  float total0 = 0.0, total1 = 0.0;
  for(int i = 0; i < 50; i++) {
    delayMicroseconds( 80000 ); 
    total0 += float( irToCm( analogRead(irReturn[0]) ) ); 
    total1 += float( irToCm( analogRead(irReturn[1]) ) );
  }
  irDistBaseline[0] = total0 / 50.0;
  irDistBaseline[1] = total1 / 50.0;
  Serial.print(irDistBaseline[0]); Serial.print("  "); Serial.println(irDistBaseline[1]);
  lastIrCalibrationTime = millis();
  //nextIrHistoryIndex[0] = nextIrHistoryIndex[1] = 0;
  
  /*float total0 = 0; float total1 = 0;
  for(int i = 0; i < 100; i++) {
    total0 += //bigIrDist[0][i];
    total1 += //bigIrDist[1][i];
  }
  float avg0 = total0 / 100.0;
  float avg1 = total1 / 100.0;
  irDistBaseline[0] = avg0;
  irDistBaseline[1] = avg1;
  lastIrCalibrationTime = millis();
  Serial.print(irDistBaseline[0]); Serial.print(", "); Serial.println(irDistBaseline[1]);*/
}

boolean getIRToggleState() {
  digitalWrite(irTogglePinOut, HIGH);
  int thru = digitalRead(irTogglePinIn);
  digitalWrite(irTogglePinOut, LOW);
  if(thru == 1) return false;
  else return true;
}
