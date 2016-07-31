# IMPORTS
import time
import threading
import picamera
from src import ultrasonic, sound, laser, vision, logger

# COMPILE SETTINGS
# toggle debug output
b_debug = True

# toggle ultrasonic sensing and feedback
b_run_ultrasonic = False

# toggle vision/dropoff sensing and feedback
b_run_vision = True

# PINS AND PATHS
trigger_pins = (23, 18) #L and R ultrasonic sensor trigger pins
echo_pins = (16, 21, 12, 24) #side-left, front-left, FR, + SR US echo pins
offsets = (0.02, 0.25) #distance from sensors to the side and front of walker
max_dists = (1.0, 3.5) #distance from side, front where input is not ignored
blips_min = 0.25 #beep play frequency at maximum distance
blips_max = 5.0  #beep play frequency at minimum (offset) distance
#ultrasonic feedback file names/locations (SL, FL, FR, SR)
us_sound_paths = ( 'sound/98left.wav', 'sound/884left.wav', 
                   'sound/884right.wav', 'sound/98right.wav' )
laser_pin = 12 #gpio pin powering the laser; should be 5
dropoff_sound_path = 'sound/dropoff.wav' #dropoff alert file location
dropoff_debug_dir = 'logs/dropoff/' #directory in which to store dropoff logs
calibration_debug_dir = 'logs/calibration/' #directory for calibration logs

# INITIALIZE VARIABLES
# part 1: rearrage settings shown above
trigger_pins = (trigger_pins[0],) * 2 + (trigger_pins[1],) * 2
offsets = (offsets[0], offsets[1], offsets[1], offsets[0])
max_dists = (max_dists[0], max_dists[1], max_dists[1], max_dists[0])
blips_min = (blips_min,) * 4
blips_max = (blips_max,) * 4
# part 2: build new variables
# map the UltrasonicSensor and SoxSoundThread constructor functions to
# 4-tuples of settings. Then combine those 2 lists into one where each
# index is for one sensor. sensors_and_sounds[0] -> (<UltrasonicSensor for
# side-left>, <SoxSoundThread for side-left>)
sensors_and_sounds = zip(map(ultrasonic.UltrasonicSensor, trigger_pins,
                             echo_pins, offsets, max_dists, blips_min,
                             blips_max
                             ),
                         map(sound.SoxSoundThread, us_sound_paths)
                     )
dropoff_sound_thr = sound.SoxSoundThread(dropoff_sound_path)
laser = laser.Laser(laser_pin)
camera = picamera.PiCamera()
#array of strings (log info) to be written to a file all at once
logarr = []

try:
    # clear the debugging directory (to free up space), then configure the 
    # camera for optimally quick image capturing. Wait 2 seconds to let the
    # camera adjust white balance, etc then calibrate the dropoff system
    if b_run_vision:
        logger.safe_remove_dirs(dropoff_debug_dir, calibration_debug_dir)
        camera.led = False
        camera.resolution = (640,480)
        camera.framerate = 55
        time.sleep(2.0)
        vision.Calibration.calibrate(camera, laser, calibration_debug_dir, 
                                     logarr)
        dropoff_sound_thr.start()
    
    # start the ultrasonic sound repeaters (SoxSoundThread)
    if b_run_ultrasonic:
        for _, sound_repeater in sensors_and_sounds:
            sound_repeater.start()

    while True:
        if b_run_ultrasonic:
            # get a pool of sensor-waiting threads, ping left and right
            # sides, start all threads listening, and wait for all responses
            # and/or time-outs
            sense_threads = [s.get_distance_thread() 
                             for s,_ in sensors_and_sounds]
            sensors_and_sounds[0][0].ping()
            sensors_and_sounds[0][2].ping()
            for th in sense_threads:
                th.start()
            for th in sense_threads:
                th.join()
            
            # update the blip frequencies of each sound player
            i = 0
            for sensor, sound_repeater in sensors_and_sounds:
                sound_repeater.set_frequency( sensor.blips_freq() )
                logger.log(logarr, 'sensor '+str(i)+', distance ' \
                           + str(sensor.distance)+ ', frequency ' \
                           + str(sensor.blips_freq())
                           )
                i += 1
                
        if b_run_vision:
            # get the  positions (and other info if desired) from image
            # processing
            if not b_debug:
                pos1, pos2 = vision.capture_to_positions(camera, laser, 
                                                         loglines=logarr)
            else:
                ((pos1, pos2), imon,imoff,imon_cr, imdiff, raw_blobs, blobs)\
                   = vision.capture_to_positions(camera, laser, True, logarr)
            
            # determine whether the positions indicate a dropoff
            is_dropoff = vision.is_dropoff(pos1, pos2, b_debug, logarr)
            if is_dropoff: 
                # sound clip is 1.5s, so loop it at 0.667 plays/s
                dropoff_sound_thr.set_frequency(2./3. if is_dropoff else 0.00001)
                if b_debug:
                    logger.log(logarr, "Dropoff!")
            
            logger.log(logarr,'threads active: '+str(threading.active_count()))
            
            if b_debug and is_dropoff:
                logger.log_dropoff(dropoff_debug_dir, imon, imoff, imon_cr, 
                                   imdiff, logarr)
        
        #time.sleep(2.0)
        logarr = []
        print ""

except KeyboardInterrupt:
    # ctrl-C interrupts the program. This code waits for threads to end
    if b_run_ultrasonic:
        for th in sense_threads:
            th.join()
        for _,sound_repeater in sensors_and_sounds:
            sound_repeater.terminate()
    if b_run_vision:
        dropoff_sound_thr.terminate()

finally:
    # be sure to close the camera access object, otherwise a restart is 
    # needed to open another instance
    camera.close()
    print "**** all resources closed ****"
    