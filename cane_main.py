# IMPORTS
import time
import threading
import picamera
from src import ultrasonic, sound, laser, vision, logger

# COMPILE SETTINGS
b_debug = True
b_run_ultrasonic = False
b_run_vision = True

# PINS AND PATHS
trigger_pins = (23, 18)
echo_pins = (16, 21, 12, 24)
offsets = (0.02, 0.25)
max_dists = (1.0, 3.5)
blips_min = 0.25
blips_max = 5.0
us_sound_paths = ( 'sound/98left.wav', 'sound/884left.wav', 
                   'sound/884right.wav', 'sound/98right.wav' )
laser_pin = 12 #should be 5
dropoff_sound_path = 'sound/dropoff.wav'
dropoff_debug_dir = 'logs/dropoff/'
calibration_debug_dir = 'logs/calibration/'

# INITIALIZE VARIABLES
trigger_pins = (trigger_pins[0],) * 2 + (trigger_pins[1],) * 2
offsets = (offsets[0], offsets[1], offsets[1], offsets[0])
max_dists = (max_dists[0], max_dists[1], max_dists[1], max_dists[0])
blips_min = (blips_min,) * 4
blips_max = (blips_max,) * 4
sensors_and_sounds = zip(map(ultrasonic.UltrasonicSensor, trigger_pins,
                             echo_pins, offsets, max_dists, blips_min,
                             blips_max
                             ),
                         map(sound.SoxSoundThread, us_sound_paths)
                         )
dropoff_sound_thr = sound.SoxSoundThread(dropoff_sound_path)
laser = laser.Laser(laser_pin)
camera = picamera.PiCamera()
logarr = []

try:
    if b_run_vision:
        logger.safe_remove_dirs(dropoff_debug_dir, calibration_debug_dir)
        camera.led = False
        camera.resolution = (640,480)
        camera.framerate = 55
        time.sleep(2.0)
        vision.Calibration.calibrate(camera, laser, calibration_debug_dir, 
                                     logarr)
    
    if b_run_ultrasonic:
        for _, sound_repeater in sensors_and_sounds:
            sound_repeater.start()
        dropoff_sound_thr.start()

    while True:
        sense_threads = [s.get_distance_thread() for s,_ in sensors_and_sounds]
        if b_run_ultrasonic:
            for th in sense_threads:
                th.start()
            sensors_and_sounds[0][0].ping()
            for th in sense_threads:
                th.join()
            
            i = 0
            for sensor, sound_repeater in sensors_and_sounds:
                sound_repeater.set_frequency( sensor.blips_freq() )
                logger.log(logarr, 'sensor '+str(i)+', distance ' \
                           +str(sensor.distance)+ ', frequency ' \
                           +str(sensor.blips_freq())
                           )
                i += 1
                
        if b_run_vision:
            if not b_debug:
                pos1, pos2 = vision.capture_to_positions(camera, laser, 
                                                         loglines=logarr)
            else:
                ((pos1, pos2), imon, imoff, imon_cr, imdiff, raw_blobs, blobs)\
                    = vision.capture_to_positions(camera, laser, True, logarr)
                
            is_dropoff = vision.is_dropoff(pos1, pos2, b_debug, logarr)
            if b_debug and is_dropoff: 
                logger.log(logarr, "Dropoff!")
            # sound clip is 1.5s, so loop it at 0.667 plays/s
            dropoff_sound_thr.set_frequency(2./3. if is_dropoff else 0.000001)
    
            logger.log(logarr,'threads active: '+str(threading.active_count()))
            
            if b_debug and is_dropoff:
                logger.log_dropoff(dropoff_debug_dir, imon, imoff, imon_cr, 
                                   imdiff, logarr)
        
        #time.sleep(2.o)
        logarr = []
        print ""

except KeyboardInterrupt:
    if b_run_ultrasonic:
        for th in sense_threads:
            th.join()
        for _,sound_repeater in sensors_and_sounds:
            sound_repeater.terminate()
    if b_run_vision:
        dropoff_sound_thr.terminate()

finally:
    camera.close()
    print "**** all resources closed ****"
    