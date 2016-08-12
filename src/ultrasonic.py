import RPi.GPIO as gpio
from time import clock
from threading import Thread
from src import util

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
        self.timeout = meters_to_seconds(10.0) #upper range 1m-4.5m, depending
        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger, gpio.OUT)
        gpio.setup(self.echo, gpio.IN, pull_up_down=gpio.PUD_DOWN)

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
        echo_time = self.measure_echo_pulse()
        
        self.distance = self.convert_time_to_distance(echo_time)
        """util.log(str(self.echo)+' went high after '+str(wait_time)
            + ' with loop count '+str(wait_count)
            + '; measured time '+str(echo_time)+' with loop count '
            + str(echo_count)+'; raw distance '+str(self.distance)
        )"""
    
    # Measure the length of the echo pulse and return it, in seconds.
    def measure_echo_pulse(self):
        echo_time = 0.0 # Length of time, in seconds.

        # wait until the echo pin goes high
        # Multiply by 1000 to convert seconds to milliseconds.
        # TODO determine timeout outside of wait_for_edge
        error = gpio.wait_for_edge(self.echo, gpio.RISING, 
                                   timeout=int(self.timeout*1000))
        
        startTime = clock()

        # wait until the echo pin goes low, storing the elapsed time
        error = gpio.wait_for_edge(self.echo, gpio.FALLING, 
                                   timeout=int(self.timeout*1000))
        if error is None:
            echo_time = REALLY_FAR_AWAY
            util.log(str(self.echo)+' never went low')
        
        endTime = clock()

        # Calculate elapsed time.
        echo_time = endTime - startTime

        return echo_time

    # Convert the provided time (in seconds) to an output distance (in meters).
    def convert_time_to_distance(self, input_time):
        distance = 0.0 # Distance in meters

        # convert time to meters and adjust for offset
        distance = seconds_to_meters(input_time) - self.dist_offset
        if distance < 0.0: 
            # found something but it's less than the minimum distance
            distance = 0.0

        return distance

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
    complete = False
    while not complete:
        complete = return_checker()
        if clock() >= tTimeout: 
            return -1
    #print('sensor time', time() - tStart)
    return clock() - tStart
    
