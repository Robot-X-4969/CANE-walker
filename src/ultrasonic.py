import RPi.GPIO as gpio
from time import clock
from threading import Thread

# distance (in meters, technically) to use when no object is seen. This 
# should be outside the range in which the walker reacts in any way
REALLY_FAR_AWAY = 49.69

class UltrasonicSensor: 
    #Constructor Parameters:
    # * trigger_pin - number for the GPIO pin connected to TRIG on the sensor
    # * echo_pin - number for the GPIO pin connected to ECHO on the sensor
    # * offset - distance from sensor when walker hits an obstacle
    # 	^ can be zero
    # * max_dist - ignores objects farther than this (after offset applied)
    #  * min_blip_freq - beep tempo at farthest distance
    # * max_blip_freq - beep tempo at nearest distance
    #Other ariables stored:
    # * distance - most recent measurement (in meters)
    # * timeout - time after which CANE should stop listening for US echo
    
    def __init__(self, trigger_pin, echo_pin, offset, max_dist, 
                 min_blip_freq, max_blip_freq):
        self.echo = echo_pin
        self.trigger = trigger_pin
        self.distance = 0  # should be >= 0
        self.dist_offset = offset
        self.dist_max = max_dist
        self.max_freq = max_blip_freq
        self.min_freq = min_blip_freq
        self.timeout = meters_to_seconds(6.0) #upper range 1m-4.5m, depending
        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger, gpio.OUT)
        gpio.setup(self.echo, gpio.IN)

    def check_echo_started(self):
        return gpio.input(self.echo)

    def check_echo_ended(self):
        return not gpio.input(self.echo)
        
    # send pulse to sensor's TRIG pin, starting the measurement process
    def ping(self):
        gpio.output(self.trigger, gpio.LOW)
        micros_wait(10)
        gpio.output(self.trigger, gpio.HIGH)
        micros_wait(10)
        gpio.output(self.trigger, gpio.LOW)
    
    # update the sensor's distance variable (see resources directory for 
    # technical info)
    def find_distance(self):
        # wait until the echo pin goes high, ignoring how long it takes
        time_check(self.check_echo_started, self.timeout)
        # wait until the echo pin goes low, storing the elapsed time
        echo_time = time_check(self.check_echo_ended, self.timeout)
        if echo_time < 0: #timed out; there is nothing in view
            self.distance = REALLY_FAR_AWAY
        else:
            #convert to meters and adjust for offset
            self.distance = seconds_to_meters(echo_time) - self.dist_offset
            if self.distance < 0.0: 
                #found something but it's less than the minimum distance
                self.distance = 0.0
            
    # return a new thread which runs find_distance()
    def get_distance_thread(self):
        return Thread(target=UltrasonicSensor.find_distance, args=(self,))
    
    # get the freqency at which the UI beeps should occur for this sensor
    def blips_freq(self):
        if self.distance < self.dist_max:
            return (self.max_freq - (self.max_freq - self.min_freq) 
                    / self.dist_max * self.distance)
        else:
            return 0.001



# def micros_to_cm(micros):
    # return micros / 58.82
def seconds_to_meters(seconds):
	return seconds * 170.145
def meters_to_seconds(meters):
	return meters / 170.145

# time.sleep() only works with input > 1 ms. This is inelegnt, but works with
# the full accuracy of the operating system. Only use when time.sleep()
# would be insufficient
def micros_wait(t):
    tEnd = clock() + t * 10**-6
    while clock() < tEnd:
        pass
    return

# run a function repeatedly until it returns true, then return the time
# it took to reach that state. If max_time (in seconds) is 
def time_check( return_checker, max_time ):
    tStart = clock()
    tTimeout = tStart + max_time
    complete = return_checker()
    while not complete:
        complete = return_checker()
        if clock() >= tTimeout: 
            return -1
    #print('sensor time', time() - tStart)
    return clock() - tStart
    
