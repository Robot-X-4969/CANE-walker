import time

class ActionFrequencyRunner:
    """
        action - method to be run periodically
        make sure to call set_frequency(freq)
    """
    def __init__(self, action):
        self.act = action
        self.t_last = time.time()

    def set_frequency(self, frequency):
        self.delay = 1.0 / frequency

    def perform_if_needed(self):
        if time.time() > self.t_last + self.delay:
            self.act()
            self.t_last = time.time()


