from threading import Thread
from os import system
from time import time, sleep

class SoxSoundThread (Thread):
    def __init__(self, filename):
        Thread.__init__(self)
        self.cmd_str = 'play -q ' + filename
        self.t_last = time()
        self.delay = 1000000
        self.is_robotting = True

    def run(self):
        while self.is_robotting:
            if time() > self.t_last + self.delay:
                #print('running', self.cmd_str)
                self.t_last = time()
                system( self.cmd_str )
                #print('finished', self.cmd_str)
            else:
                sleep(0.02)

    def set_frequency(self, frequency):
        self.delay = 1.0 / frequency

    def terminate(self):
        self.is_robotting = False