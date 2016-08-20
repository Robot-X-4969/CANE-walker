import RPi.GPIO
import time
import threading

class UltrasonicThread (threading.Thread):
    stateMachines = None # List of state machines to loop through.  Cannot be initialized here, so is set to None.
    distanceOptions = None # Distance options object, used to hold values for processing.

    def __init__(self, triggerPins, echoPins):
        for trigger, echo in zip(triggerPins, echoPins):
            self.stateMachiens.add(UltrasonicStateMachine(trigger, echo))
        self.distanceOptions = DistanceOptions()

    def run(self):
        for machine in self.stateMachines:
            machine.update()
        time.sleep(0.00001) # TODO Adjust this value.

class DistanceOptions:
    # Content

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
        GPIO.setmode(gpio.BCM)
        if triggerPin is not None:
           GPIO.setup(self.triggerPin, GPIO.OUT)
        GPIO.setup(self.echoPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def update(self):
        if self.state == 0:
            self.startTriggerPing()
        elif self.state == 1:
            self.waitForTriggerEnd()
        elif self.state == 2:
            self.waitForEchoStart()
        elif self.state == 3;
            self.waitForEchoEnd()
        elif self.state == 4;
            self.calculateRawTime()
    
    def startTriggerPing(self):
        GPIO.output(self.triggerPin, GPIO.HIGH)
        state += 1
    
    triggerEndTime = 0
    waitingForTrigger = False
    def waitForTriggerEnd(self):
        if self.waitingForTrigger == False:
            self.waitingForTrigger = True
            self.triggerEndTime = time.clock() + (10 * 10**-6) # Stop in 10 microseconds.
        elif self.triggerEndTime < time.clock():
            self.waitingForTrigger = False
            self.state += 1
    
    echoStartTime = 0
    def waitForEchoStart(self):
        if GPIO.input(echoPin) == GPIO.HIGH:
            self.echoStartTime = time.clock()
            self.state += 1

    echoEndTime = 0
    def waitForEchoEnd(self):
        if GPIO.input(echoPin) == GPIO.LOW:
            self.echoEndTime = time.clock()
            self.state += 1

    def calculateRawTime(self):
        self.rawTime = self.echoEndTime - self.echoStartTime
        print(self.rawTime)


