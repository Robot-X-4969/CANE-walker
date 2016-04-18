# IMPORTS
from src.ultrasonic_sensor import UltrasonicSensor
from src.action_frequency_runner import ActionFrequencyRunner
from src.sox_sound_player import play_sound
import time
import threading

# GLOBALS
TRIG_L = 22
TRIG_R = 23 #fix
ECHO_LS = 18 
ECHO_LF = 19 #fix
ECHO_RF = 20 #fix
ECHO_RS = 21 #fix
OFFSET_SIDE = 5
OFFSET_FRONT = 25
MAX_DIST_SIDE = 200
MAX_DIST_FRONT = 350
SOUND_LS = 'sound/98left.wav'
SOUND_LF = 'sound/98right.wav'
SOUND_RF = 'sound/884left.wav'
SOUND_RS = 'sound/884right.wav'
BLIP_FREQ_MIN = 0.25
BLIP_FREQ_MAX = 5.0


#TODO fix pin locations
sensors = [
    UltrasonicSensor(TRIG_L, ECHO_LS, OFFSET_SIDE, MAX_DIST_SIDE, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
    #UltrasonicSensor(TRIG_L, ECHO_LF, OFFSET_FRONT, MAX_DIST_FRONT, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
    #UltrasonicSensor(TRIG_R, ECHO_RF, OFFSET_FRONT, MAX_DIST_FRONT, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
    #UltrasonicSensor(TRIG_R, ECHO_RS, OFFSET_SIDE, MAX_DIST_SIDE, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
]

sound_runners = [
    ActionFrequencyRunner( play_sound(SOUND_LS) ),
    #ActionFrequencyRunner( play_sound(SOUND_LF) ),
    #ActionFrequencyRunner( play_sound(SOUND_RF) ),
    #ActionFrequencyRunner( play_sound(SOUND_RS) ),
]

try:
    while True:
        for s in sensors:
            sense_threads = []
            thread = s.get_distance_thread()
            sense_threads.append( thread )
            thread.start()
        
        all_done = False
        while not all_done:
            all_done = True
            for t in sense_threads:
                all_done = all_done and not t.is_alive()
            for r in sound_runners:
                r.perform_if_needed()

        for i in range(1): #range(4)
            sound_runners[i].set_frequency( sensors[i].blips_freq() )
        
        print('threads active', threading.active_count())
        time.sleep(0.02)
        

except KeyboardInterrupt:
    for t in sense_threads:
        t.join()

