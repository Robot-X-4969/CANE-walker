import RPi.GPIO
import time

class UltrasonicThread:
    # Content

class UltrasonicStateMachine:
    # All methods in the state machine should be non-blocking.
    state = 0 # Keeps track of state and runs proper methods.
    triggerPin = None # Trigger pin.  Can be None.
    echoPin = None
    distance = 0 # Most recently found distance, in meters.

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
            self.calculateDistance()
    
    def startTriggerPing(self):
        GPIO.output(self.triggerPin, GPIO.HIGH)
        state += 1
    
    triggerEndTime = 0
    waitingForTrigger = False
    def waitForTriggerEnd(self):
        if waitingForTrigger == False:
            waitingForTrigger = True
            triggerEndTime = time.clock() + (10 * 10**-6) # Stop in 10 microseconds.
        elif triggerEndTime < time.clock():
            waitingForTrigger = False
            state += 1

    def waitForEchoStart(self):

    def waitForEchoEnd(self):

    def calculateDistance(self):


