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
    time_check( findEchoHigh, timeout )

    def findEchoLow():
        return not gpio.input(echo)
    tDiffSoundMicros = time_check( findEchoLow, timeout ) * 1000000
    
    return micros_to_cm(tDiffSoundMicros)


def micros_to_cm(micros):
    return micros / 58.82

def micros_wait(t):
    tEnd = time.time() + t/1000000.0
    while time.time() < tEnd: pass

def time_check( return_checker, max_time ):
    tStart = time.time()
    tTimeout = tStart + max_time
    complete = return_checker()
    while not complete:
        complete = return_checker()
        if time.time() >= tTimeout: return 0
    return time.time() - tStart
    
