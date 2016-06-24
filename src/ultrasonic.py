import RPi.GPIO as gpio
from time import clock
from threading import Thread


REALLY_FAR_AWAY = 1000

class UltrasonicSensor:
    """ 
    Constructor Parameters:
	* trigger_pin - number for the GPIO pin connected to TRIG on the sensor
	* echo_pin - number for the GPIO pin connected to ECHO on the sensor
	* offset - distance from sensor when walker hits an obstacle
		^ can be zero
	* max_dist - ignores objects farther than this (after offset applied)
      * min_blip_freq - beep tempo at farthest distance
      * max_blip_freq - beep tempo at nearest distance
    """
    

    def __init__(self, trigger_pin, echo_pin, offset, max_dist, min_blip_freq, max_blip_freq):
        self.echo = echo_pin
        self.trigger = trigger_pin
        self.distance = 0  # should be >= 0
        self.dist_offset = offset
        self.dist_max = max_dist
        self.max_freq = max_blip_freq
        self.min_freq = min_blip_freq
        self.timeout = meters_to_seconds(6.0)
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
        time_check(self.check_echo_started, self.timeout)
        tmp_time = time_check(self.check_echo_ended, self.timeout)
        raw_distance = seconds_to_meters( tmp_time )
        self.distance = raw_distance - self.dist_offset
        #print("""'went high after', wait_time, """'measured time', tmp_time)
        print('raw distance', self.distance)
        if raw_distance < 0: #timed out
            self.distance = REALLY_FAR_AWAY
        elif self.distance < 0.0: #found something but it's too close
            self.distance = 0.0  #thus self.distance >= 0 always
        return
            

    def get_distance_thread(self):
        return Thread(target=UltrasonicSensor.find_distance, args=(self,))

    def blips_freq(self):
        if self.distance < self.dist_max:
            return self.max_freq - (self.max_freq - self.min_freq) / self.dist_max * self.distance
        else:
            return 0.001



# def micros_to_cm(micros):
    # return micros / 58.82
def seconds_to_meters(seconds):
	return seconds * 170.145
def meters_to_seconds(meters):
	return meters / 170.145

def micros_wait(t):
    tEnd = clock() + t * 10**-6
    while clock() < tEnd:
        pass
    return

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
    
