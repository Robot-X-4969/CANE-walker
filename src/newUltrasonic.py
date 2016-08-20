import RPi.GPIO as GPIO
import time
import threading

class UltrasonicThread (threading.Thread):
    stateMachines = None # List of state machines to loop through.  Cannot be initialized here, so is set to None.
    distanceOptions = None # Distance options object, used to hold values for processing.

    def __init__(self, triggerPins, echoPins):
        self.stateMachines = [] # Initialize stateMachines as a list.
        for trigger, echo in zip(triggerPins, echoPins):
            self.stateMachines.append(UltrasonicStateMachine(trigger, echo))
        self.distanceOptions = DistanceOptions()
        threading.Thread.__init__(self)

    def run(self):
        while True:
            for machine in self.stateMachines:
                machine.update()
            time.sleep(0.00001) # TODO Adjust this value.

class DistanceOptions:
    # Content
    def __init__(self):
        pass

class UltrasonicStateMachine:
    # All methods in the state machine should be non-blocking.
    state = 0 # Keeps track of state and runs proper methods.
    triggerPin = None # Trigger pin.  Can be None.
    echoPin = None
    rawTime = 0 # Raw time for sound to bounce against object and back, seconds.

    def __init__(self, triggerPin, echoPin):
        self.triggerPin = triggerPin
        self.echoPin = echoPin

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
            self.calculateRawTime()
    
    def startTriggerPing(self):
        if self.triggerPin is not None:
            GPIO.output(self.triggerPin, GPIO.HIGH)
        self.state += 1
    
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

    echoEndTime = 0
    def waitForEchoEnd(self):
        if GPIO.input(self.echoPin) == GPIO.LOW:
            self.echoEndTime = time.clock()
            self.state += 1

    def calculateRawTime(self):
        self.rawTime = self.echoEndTime - self.echoStartTime
        print("Pin: " + str(self.echoPin) + " Time: " + str(self.rawTime))
        self.state = 0


