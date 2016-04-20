import threading
import os
import time

class SoxSoundThread (threading.Thread):
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.cmd_str = 'play -q ' + filename
        self.t_last = time.time()
        self.delay = 0

    def run(self):
        if time.time() > self.t_last + self.delay:
            print('running', self.cmd_str)
            os.system( self.cmd_str )
		    #print('finished', self.cmd_str)
            self.t_last = time.time()

    def set_frequency(self, frequency):
        self.delay = 1.0 / frequency

