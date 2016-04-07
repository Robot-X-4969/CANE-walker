import RPi.GPIO as gpio
import time

trigger = 22
echo = 18
timeout = 0.05

def setup():
    gpio.setmode(gpio.BCM)
    gpio.setup(trigger, gpio.OUT)
    gpio.setup(echo, gpio.IN)


def find_dist():
    gpio.output(trigger, gpio.LOW)
    micros_wait(10)
    gpio.output(trigger, gpio.HIGH)
    micros_wait(10)
    gpio.output(trigger, gpio.LOW)

    def findEchoHigh():
        return gpio.input(echo)
    time_check( findEchoHigh )

    def findEchoLow():
        return not gpio.input(echo)
    tDiffSoundMicros = time_check( findEchoLow ) * 1000000
    
    return microsToCm(tDiffSoundMicros)


def micros_to_cm(micros):
    return micros / 58.82

def micros_wait(t):
    tEnd = time.time() + t/1000000.0
    while time.time() < tEnd: pass

def time_check( return_checker ):
    tStart = time.time()
    tTimeout = tStart + timeout
    complete = return_checker()
    while not complete:
        complete = return_checker()
        if time.time() >= tTimeout: return
    return time.time() - tStart
    
