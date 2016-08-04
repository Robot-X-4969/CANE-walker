# IMPORTS
from src.ultrasonic_sensor import UltrasonicSensor
from src.sox_sound_player import SoxSoundThread
import time
import threading

# GLOBALS
TRIG_L = 23
TRIG_R = 18
ECHO_LS = 16
ECHO_LF = 21
ECHO_RF = 12
ECHO_RS = 24
OFFSET_SIDE = 0.05
OFFSET_FRONT = 0.25
MAX_DIST_SIDE = 1.0
MAX_DIST_FRONT = 3.5
SOUND_LS = 'sound/98left.wav'
SOUND_LF = 'sound/884left.wav'
SOUND_RF = 'sound/884right.wav'
SOUND_RS = 'sound/98right.wav'
BLIP_FREQ_MIN = 0.25
BLIP_FREQ_MAX = 5.0


#TODO fix pin locations
sensors = [
    #UltrasonicSensor(TRIG_L, ECHO_LS, OFFSET_SIDE, MAX_DIST_SIDE, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
    #UltrasonicSensor(TRIG_L, ECHO_LF, OFFSET_FRONT, MAX_DIST_FRONT, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
    #UltrasonicSensor(TRIG_R, ECHO_RF, OFFSET_FRONT, MAX_DIST_FRONT, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
    UltrasonicSensor(TRIG_R, ECHO_RS, OFFSET_SIDE, MAX_DIST_SIDE, BLIP_FREQ_MIN, BLIP_FREQ_MAX),
]

sound_repeaters = [
    #SoxSoundThread(SOUND_LS),
    #SoxSoundThread(SOUND_LF),
    #SoxSoundThread(SOUND_RF),
    SoxSoundThread(SOUND_RS),
]

for sr in sound_repeaters:
    sr.set_frequency(0.0001)
    sr.start()

try:
    while True:
        sense_threads = [s.get_distance_thread() for s in sensors]
        for th in sense_threads:
            th.start()
        sensors[0].ping()
        for th in sense_threads:
            th.join()

        for i in range(len(sound_repeaters)):
            sound_repeaters[i].set_frequency( sensors[i].blips_freq() )
            print 'sensor '+str(sensors[i].echo)+'; distance ' \
                  +str(sensors[i].distance) \
                  +'; frequency '+str(sensors[i].blips_freq())

        print 'threads active '+str(threading.active_count())
        time.sleep(0.5)
        print ''

except KeyboardInterrupt:
    for th in sense_threads:
        th.join()
    for sr in sound_repeaters:
        sr.stop_robotting()

