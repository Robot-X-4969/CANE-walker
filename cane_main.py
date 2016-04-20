# IMPORTS
from src.ultrasonic_sensor import UltrasonicSensor
from src.sox_sound_player import SoxSoundThread
import time
import threading

# GLOBALS
TRIG_L = 12
TRIG_R = 23 #fix
ECHO_LS = 20
ECHO_LF = 19 #fix
ECHO_RF = 20 #fix
ECHO_RS = 21 #fix
OFFSET_SIDE = 0.0
OFFSET_FRONT = 0.25
MAX_DIST_SIDE = 5.0
MAX_DIST_FRONT = 3.5
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

sound_repeaters = [
    SoxSoundThread(SOUND_LS),
    #SoxSoundThread(SOUND_LF),
    #SoxSoundThread(SOUND_RF),
    #SoxSoundThread(SOUND_RS),
]

try:
    while True:
        sense_threads = []
        for s in sensors:
            sense_threads.append( s.get_distance_thread() )
        for th in sense_threads:
            th.start()
        for th in sense_threads:
            th.join()

        #all_done = False
        #while not all_done:
            #all_done = True
            #for t in sense_threads:
                #all_done = all_done and not t.is_alive()
            #for r in sound_repeaters:
                #r.play_if_needed()

        for i in range(len(sound_repeaters)):
            sound_repeaters[i].set_frequency( sensors[i].blips_freq() )
            print('sensor', i, 'frequency', sensors[i].blips_freq())
        
        print('threads active', threading.active_count())
        time.sleep(0.5)
        

except KeyboardInterrupt:
    for t in sense_threads:
        t.join()

