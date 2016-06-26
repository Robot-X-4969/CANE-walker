# IMPORTS
from src.ultrasonic import UltrasonicSensor
from src.laser import Laser
from src import vision
from src.sound import SoxSoundThread
from picamera import PiCamera
from time import sleep
from threading import active_count as threads_active


# PINS AND PATHS
trigger_pins = (23, 18)
echo_pins = (16, 21, 12, 24)
offsets = (0.02, 0.25)
max_dists = (1.0, 3.5)
blips_min = 0.25
blips_max = 5.0
us_sound_paths = ( 'sound/98left.wav', 'sound/884left.wav', \
                   'sound/884right.wav', 'sound/98right.wav' )
laser_pin = 5
dropoff_sound_path = 'sound/dropoff.wav'

# INITIALIZE VARIABLES
trigger_pins = (trigger_pins[0],) * 2 + (trigger_pins[1],) * 2
offsets = (offsets[0], offsets[1], offsets[1], offsets[0])
max_dists = (max_dists[0], max_dists[1], max_dists[1], max_dists[0])
blips_min = (blips_min,) * 4
blips_max = (blips_max,) * 4
sensors_and_sounds = zip( map(UltrasonicSensor, trigger_pins, echo_pins, \
                              offsets, max_dists, blips_min, blips_max), \
                          map(SoxSoundThread, us_sound_paths) )
dropoff_sound_thr = SoxSoundThread(dropoff_sound_path)
laser = Laser(laser_pin)
camera = PiCamera()

try:
    camera.led = False
    camera.resolution = (640,480)
    camera.framerate = 55
    sleep(2.0)
    vision.Calibration.calibrate(camera, laser)
    print "camera calibration complete"
    
    for _, sound_repeater in sensors_and_sounds:
        sound_repeater.start()
    dropoff_sound_thr.start()

    while True:
        sense_threads = [s.get_distance_thread() for s,_ in sensors_and_sounds]
        for th in sense_threads:
            th.start()
        sensors_and_sounds[0][0].ping()
        for th in sense_threads:
            th.join()
        
        i = 0
        for sensor, sound_repeater in sensors_and_sounds:
            sound_repeater.set_frequency( sensor.blips_freq() )
            print 'sensor '+str(i)+', distance '+str(sensor.distance)+ \
                  ', frequency '+str(sensor.blips_freq())
            i += 1
        
        pos1, pos2 = vision.capture_to_positions(camera, laser)
        is_dropoff = vision.is_dropoff(pos1, pos2)
        # sound clip is 1.5s, so loop it at 0.667 plays/s
        if is_dropoff: print "Dropoff!"
        dropoff_sound_thr.set_frequency( 2./3. if is_dropoff else 0.000001 )

        print( 'threads active', threads_active(), "\n" )
        #sleep(2.0)

except KeyboardInterrupt:
    for th in sense_threads:
        th.join()
    for _,sound_repeater in sensors_and_sounds:
        sound_repeater.terminate()

finally:
    camera.close()
    print "**** closed camera ****"
    