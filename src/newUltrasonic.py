import RPi.GPIO as GPIO
import time
import threading

class UltrasonicThread (threading.Thread):
    stateMachines = None # List of state machines to loop through.  Cannot be initialized here, so is set to None.
    soundThreads = None
    #dropoffFile

    def __init__(self, triggerPins, echoPins, distanceOptions, soundThreads):
        threading.Thread.__init__(self)
        self.stateMachines = [] # Initialize stateMachines as a list.
        for trigger, echo, distOptions in zip(triggerPins, echoPins, distanceOptions):
            machine = UltrasonicStateMachine(trigger, echo)
            machine.distanceOptions = distOptions
            self.stateMachines.append(machine)
        dropoffFile = open("dropoffEnabled.txt", "w")
        self.soundThreads = soundThreads
        for thread in soundThreads:
            thread.start()

    def run(self):
        while True:
            for machine, soundThread in zip(self.stateMachines, self.soundThreads):
                machine.findDistance()
                soundThread.set_frequency(machine.blipsFrequency)
                if machine.distanceOptions.frontSensor and machine.rawDistance > 1.5:
                    dropoffFile.write("True")
                elif machine.distanceOptions.frontSensor:
                    dropoffFile.write("False")
                time.sleep(0.001)

class DistanceOptions:
    minDistance = 0 #Distance when the walker hits an obstacle, in meters.
    maxDistance = 0 #Distance after which objects are ignored, in meters.
    inverseConstant = 1 # k, where y=k/x . x is distance, and y is frequency.
    frontSensor = False #Set True if it's a front sensor.  Used to disable dropoff detection if there is an obstacle.

    def __init__(self):
        self.inverseConstant = 1
        self.frontSensor = False

class UltrasonicStateMachine:
    # All methods in the state machine should be non-blocking.
    timedOut = False

    triggerPin = None # Pin which the Pi pulse to tell the sensor to ping.
    echoPin = None # Pin on which the Pi receives a ping back from the sensor.

    distanceOptions = None # Distance options object, used to hold values for processing.

    rawTime = 0 # Raw time for sound to bounce against object and back, seconds.
    rawDistance = 0
    blipsFrequency = 0.0

    consecutiveTimeouts = 0

    def __init__(self, triggerPin, echoPin):
        self.triggerPin = triggerPin
        self.echoPin = echoPin

        self.blipsFrequency = 0.001 # Default frequency when starting out.

        self.setUpGPIO()

    def setUpGPIO(self):
        GPIO.setmode(GPIO.BCM)
        if self.triggerPin is not None:
           GPIO.setup(self.triggerPin, GPIO.OUT)
        GPIO.setup(self.echoPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def findDistance(self):
        self.timedOut = False

        self.startTriggerPing()
        self.waitForTriggerEnd()
        self.endTriggerPing()
        self.waitForEchoStart()
        self.waitForEchoEnd()
        if self.timedOut == False:
            self.calculateValues()
            self.consecutiveTimeouts = 0
        else:
            self.consecutiveTimeouts += 1
            if self.consecutiveTimeouts > 50:
                self.blipsFrequency = 0.001
            print("Pin: " + str(self.echoPin) + " timed out!")
    
    def startTriggerPing(self):
        GPIO.output(self.triggerPin, GPIO.HIGH)
    
    def waitForTriggerEnd(self):
        time.sleep(0.00001)

    def endTriggerPing(self):
        GPIO.output(self.triggerPin, GPIO.LOW)

    echoStartTime = 0
    waitForEchoStartTime = 0
    def waitForEchoStart(self):
        self.waitForEchoStartTime = time.time()
        while True:
            if GPIO.input(self.echoPin) == GPIO.HIGH:
                self.echoStartTime = time.time()
                break
            elif time.time() > self.waitForEchoStartTime + 0.01: # Timeout if it missed the echo.
                self.timedOut = True
                break

    echoEndTime = 0
    def waitForEchoEnd(self):
        while True:
            if GPIO.input(self.echoPin) == GPIO.LOW:
                self.echoEndTime = time.time()
                break
            elif time.time() > self.waitForEchoStartTime + 0.02: # Timeout if it missed the echo.
                self.timedOut = True
                break

    def calculateValues(self):
        self.calculateRawTime()
        self.calculateRawDistance()
        self.calculateBlipFrequency()
        print("Pin: " + str(self.echoPin) + " Distance (m): " + str(self.rawDistance))

    def calculateRawTime(self):
        self.rawTime = self.echoEndTime - self.echoStartTime

    def calculateRawDistance(self):
        speedOfSound = 343.2 # meters / second
        self.rawDistance = (self.rawTime / 2.0) * speedOfSound

    def calculateBlipFrequency(self):
        if self.rawDistance > self.distanceOptions.maxDistance:
            self.blipsFrequency = 0.001
        elif self.rawDistance <= self.distanceOptions.minDistance:
            self.blipsFrequency = 20
        else:
            # Do a linear conversion between the two scales.
            #w = (self.rawDistance - self.distanceOptions.minDistance) / (self.distanceOptions.maxDistance / self.distanceOptions.minDistance)
            #self.blipsFrequency = self.distanceOptions.maxBlipFrequency - (w * (self.distanceOptions.maxBlipFrequency - self.distanceOptions.minBlipFrequency))

            # Do an inverse proportional relationship between distance and frequency.
            self.blipsFrequency = self.distanceOptions.inverseConstant / (self.rawDistance - self.distanceOptions.minDistance)

