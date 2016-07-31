from threading import Thread
from os import system
from time import clock, sleep

class SoxSoundThread (Thread):
    # A class extending threading.Thread which plays a single sound file a
    # modifiable number of times per second.
    # t_last: the time at which the last sound started (system time, 
    #             not UTC-synchronized)
    # delay: the waiting period between plays, calculated from the frequency
    # is_robotting: True to continue working; False to safely end the thread
    
    def __init__(self, filename):
        Thread.__init__(self)
        self.system_command = 'play -q ' + filename
        self.t_last = clock()
        self.delay = 1000000.0
        self.is_robotting = True

    def run(self):
        while self.is_robotting:
            if clock() > self.t_last + self.delay:
                #print('running', self.system_command)
                self.t_last = clock()
                system( self.system_command )
                #print('finished', self.system_command)
            else:
                # check for blip start events ~50 times per second
                sleep(0.02)

    def set_frequency(self, frequency):
        self.delay = 1.0 / frequency
    
    # safely kill the thread
    def terminate(self):
        self.is_robotting = False