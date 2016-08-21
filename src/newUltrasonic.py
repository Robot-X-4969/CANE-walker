import RPi.GPIO as GPIO
import time
import threading

class UltrasonicThread (threading.Thread):
    stateMachines = None # List of state machines to loop through.  Cannot be initialized here, so is set to None.
    soundThreads = None

    def __init__(self, triggerPins, echoPins, distanceOptions, soundThreads):
        threading.Thread.__init__(self)
        self.stateMachines = [] # Initialize stateMachines as a list.
        for trigger, echo, distOptions in zip(triggerPins, echoPins, distanceOptions):
            machine = UltrasonicStateMachine(trigger, echo)
            machine.distanceOptions = distOptions
            self.stateMachines.append(machine)
        self.soundThreads = soundThreads
        for thread in soundThreads:
            thread.start()

    def run(self):
        while True:
            for machine, soundThread in zip(self.stateMachines, self.soundThreads):
                machine.update()
                while machine.state != 0:
                    #print("Pin: " + str(machine.echoPin) + " State: " + str(machine.state))
                    machine.update()
                    soundThread.set_frequency(machine.blipsFrequency)
                #time.sleep(0.00001) # TODO Adjust this value.

class DistanceOptions:
    minDistance = 0 #Distance when the walker hits an obstacle, in meters.
    maxDistance = 0 #Distance after which objects are ignored, in meters.
    minBlipFrequency = 0 #Minimum frequency for sound blips, in blips / second.
    maxBlipFrequency = 0 #Maximum frequency for sound blips, in blips / second.
    def __init__(self):
        pass

class UltrasonicStateMachine:
    # All methods in the state machine should be non-blocking.
    state = 0 # Keeps track of state and runs proper methods.

    triggerPin = None # Pin which the Pi pulse to tell the sensor to ping.  Can be None.
    echoPin = None # Pin on which the Pi receives a ping back from the sensor.

    distanceOptions = None # Distance options object, used to hold values for processing.

    rawTime = 0 # Raw time for sound to bounce against object and back, seconds.
    rawDistance = 0
    blipsFrequency = 0.0

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

    def update(self):
        if self.state == 0:
            self.startTriggerPing()
        elif self.state == 1:
            self.waitForTriggerEnd()
        elif self.state == 2:
            self.waitForEchoStart()
        elif self.state == 3:
            self.waitForEchoEnd()
        elif self.state == 4:
            self.calculateValues()
        elif self.state == 5:
            self.waitingPeriod()
        else:
            self.state = 0
    
    def startTriggerPing(self):
        if self.triggerPin is not None:
            GPIO.output(self.triggerPin, GPIO.HIGH)
            self.state += 1
        else:
            self.triggerEndTime = time.clock()
            self.state += 2
    
    triggerEndTime = 0
    waitingForTrigger = False
    def waitForTriggerEnd(self):
        if self.triggerPin is None:
            self.state += 1
        else:
            if self.waitingForTrigger == False:
                self.waitingForTrigger = True
                self.triggerEndTime = time.clock() + (10 * 10**-6) # Stop in 10 microseconds.
            elif self.triggerEndTime < time.clock():
                if self.triggerPin is not None:
                    GPIO.output(self.triggerPin, GPIO.LOW)
                self.waitingForTrigger = False
                self.state += 1
    
    echoStartTime = 0
    def waitForEchoStart(self):
        if GPIO.input(self.echoPin) == GPIO.HIGH:
            self.echoStartTime = time.clock()
            self.state += 1
        elif time.clock() > self.triggerEndTime + 0.2: # Timeout if it missed the echo.
            self.state = 0

    echoEndTime = 0
    def waitForEchoEnd(self):
        if GPIO.input(self.echoPin) == GPIO.LOW:
            self.echoEndTime = time.clock()
            self.state += 1
        elif time.clock() > self.echoStartTime + 0.2: # Timeout if it missed the echo.
            self.state = 0

    def calculateValues(self):
        self.calculateRawTime()
        self.calculateRawDistance()
        self.calculateBlipFrequency()
        print("Pin: " + str(self.echoPin) + " Distance (m): " + str(self.rawDistance))
        self.state += 1

    def calculateRawTime(self):
        self.rawTime = self.echoEndTime - self.echoStartTime

    def calculateRawDistance(self):
        speedOfSound = 343.2 # meters / second
        self.rawDistance = (self.rawTime / 2.0) * speedOfSound

    def calculateBlipFrequency(self):
        if self.rawDistance > self.distanceOptions.maxDistance:
            self.blipsFrequency = 0.001
        elif self.rawDistance < self.distanceOptions.minDistance:
            self.blipsFrequency = self.distanceOptions.maxBlipFrequency
        else:
            # Do a linear conversion between the two scales.
            w = (self.rawDistance - self.distanceOptions.minDistance) / (self.distanceOptions.maxDistance / self.distanceOptions.minDistance)
            self.blipsFrequency = self.distanceOptions.maxBlipFrequency - (w * (self.distanceOptions.maxBlipFrequency - self.distanceOptions.minBlipFrequency))

    waitEndTime = 0
    waiting = False
    def waitingPeriod(self):
       if self.waiting == False:
           self.waiting = True
           self.waitEndTime = time.clock() + 0.05 
       elif self.waitEndTime < time.clock():
           self.waiting = False
           self.state += 1
        

