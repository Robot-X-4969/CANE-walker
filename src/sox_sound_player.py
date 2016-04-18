import threading
import os

class SoxSoundThread (threading.Thread):
	def __init__(self, filename):
		threading.Thread.__init__(self)
		self.cmd_str = 'play ' + filename

	def run(self):
		print('running', self.cmd_str)
		os.system( self.cmd_str )
		print('finished', self.cmd_str)

def play_sound(filename):
    SoxSoundThread(filename).start()