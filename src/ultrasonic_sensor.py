import RPi.GPIO as gpio
import time
import threading


REALLY_FAR_AWAY = 1000

class UltrasonicSensor:	
    """ 
    Constructor Parameters:
	* trigger_pin - number for the GPIO pin connected to TRIG on the sensor
	* echo_pin - number for the GPIO pin connected to ECHO on the sensor
	* offset - distance from sensor when walker hits an obstacle
		^ can be zero
	* max_dist - ignores objects farther than this (after offset applied)
    """
    

    def __init__(self, trigger_pin, echo_pin, offset, max_dist, min_blip_freq, max_blip_freq):
        self.echo = echo_pin
        self.trigger = trigger_pin
        self.distance = 0  # should be >= 0
        self.dist_offset = offset
        self.dist_max = max_dist
        self.max_freq = max_blip_freq
        self.min_freq = min_blip_freq
        self.timeout = 0.1
        gpio.setmode(gpio.BCM)
        gpio.setup(self.trigger, gpio.OUT)
        gpio.setup(self.echo, gpio.IN)

    def check_echo_started(self):
        return gpio.input(self.echo)

    def check_echo_ended(self):
        return not gpio.input(self.echo)

    def ping(self):
        gpio.output(self.trigger, gpio.LOW)
        micros_wait(10)
        gpio.output(self.trigger, gpio.HIGH)
        micros_wait(10)
        gpio.output(self.trigger, gpio.LOW)

    def find_distance(self):
        #gpio.output(self.trigger, gpio.LOW)
        #micros_wait(10)
        #gpio.output(self.trigger, gpio.HIGH)
        #micros_wait(10)
        #gpio.output(self.trigger, gpio.LOW)

        wait_time = time_check(self.check_echo_started, self.timeout)
        echo_time = time_check(self.check_echo_ended, self.timeout)
        raw_distance = seconds_to_meters( echo_time )
        self.distance = raw_distance - self.dist_offset
        print str(self.trigger)+' went high after '+str(wait_time) + \
              '; measured time '+str(echo_time) + \
              '; raw distance '+str(self.distance)
        if echo_time < 0: #timed out
            self.distance = REALLY_FAR_AWAY
        elif self.distance < 0.0: #found something but it's too close
            self.distance = 0.0  #thus self.distance >= 0 always
        return
            

    def get_distance_thread(self):
        return threading.Thread(target=UltrasonicSensor.find_distance, 
                                args=(self,))

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

def micros_wait(t):
    tEnd = time.clock() + t * 10**-6
    while time.clock() < tEnd:
        pass
    return

def time_check( return_checker, max_time ):
    tStart = time.clock()
    tTimeout = tStart + max_time
    complete = return_checker()
    while not complete:
        complete = return_checker()
        if time.clock() >= tTimeout: 
            return -1
    #print('sensor time', time.clock() - tStart)
    return time.clock() - tStart
    
