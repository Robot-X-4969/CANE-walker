# IMPORTS
import time
import threading
import picamera
from src import ultrasonic, sound, laser, vision, util

# COMPILE SETTINGS

# toggle ultrasonic sensing and feedback
b_run_ultrasonic = True

# toggle vision/dropoff sensing and feedback
b_run_vision = False

# change the way(s) in which log data is stored (print to stdout and/or file)
util.set_log_modes(util.LogMode.USE_STDOUT, util.LogMode.USE_MEMORY_BUFFER)


# PINS AND PATHS
trigger_pins = (23, 18) #L and R ultrasonic sensor trigger pins
echo_pins = (16, 21)#, 12, 24) #side-left, front-left, FR, + SR US echo pins
offsets = (0.02, 0.25) #distance from sensors to the side and front of walker
max_dists = (1.0, 3.5) #distance from side, front where input is not ignored
blips_min = 0.25 #beep play frequency at maximum distance
blips_max = 5.0  #beep play frequency at minimum (offset) distance
#ultrasonic feedback file names/locations (SL, FL, FR, SR)
us_sound_paths = ( 'sound/98left.wav', 'sound/884left.wav')#, 
                   #'sound/884right.wav', 'sound/98right.wav' )
laser_pin = 5 #gpio pin powering the laser
dropoff_sound_path = 'sound/dropoff.wav' #dropoff alert file location
dropoff_debug_dir = 'logs/dropoff' #directory in which to store dropoff logs
calibration_debug_dir = 'logs/calibration' #directory for calibration logs

# INITIALIZE VARIABLES
# part 1: rearrage settings shown above
trigger_pins = (trigger_pins[0],) * 2 #+ (trigger_pins[1],) * 2
offsets =   (offsets[0],   offsets[1])#,   offsets[1],   offsets[0])
max_dists = (max_dists[0], max_dists[1])#, max_dists[1], max_dists[0])
blips_min = (blips_min,) * 2#4
blips_max = (blips_max,) * 2#4
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
camera = None

try:
    # clear the debugging directory (to free up space), then configure the 
    # camera for optimally quick image capturing. Wait 2 seconds to let the
    # camera adjust white balance, etc then calibrate the dropoff system
    if b_run_vision:
        camera = picamera.PiCamera()
        util.super_remove_dirs(dropoff_debug_dir, calibration_debug_dir)
        camera.led = False
        camera.resolution = (vision.imwidth, vision.imheight)
        camera.framerate = 55
        time.sleep(2.0)
        vision.Calibration.calibrate(camera, laser, calibration_debug_dir)
        calibration_mask = vision.Calibration.get_mask()
        dropoff_sound_thr.start()
    
    # start the ultrasonic sound repeaters (SoxSoundThread)
    if b_run_ultrasonic:
        for _, sound_repeater in sensors_and_sounds:
            sound_repeater.start()

    while True:
        if b_run_ultrasonic:
            util.set_log_path(None)            
            
            # get a pool of sensor-waiting threads, ping left and right
            # sides, start all threads listening, and wait for all responses
            # and/or time-outs
            sense_threads = [s.get_distance_thread() 
                             for s,_ in sensors_and_sounds]
            sensors_and_sounds[0][0].ping()
            #sensors_and_sounds[2][0].ping()
            for th in sense_threads:
                th.start()
            for th in sense_threads:
                th.join()
            
            # update the blip frequencies of each sound player
            for sensor, sound_repeater in sensors_and_sounds:
                sound_repeater.set_frequency( sensor.blips_freq() )
                util.log('sensor '+str(sensor.echo)+'; distance '
                              +str(sensor.distance) +'; frequency '
                              +str(sensor.blips_freq())
                        )
                
        if b_run_vision:
            util.set_log_path(dropoff_debug_dir + '/' + util.time_stamp())                
            
            image_on, image_off = vision.capture_images(camera, laser)
            image_diff = vision.differentiate_images(image_on, image_off, 
                                                     calibration_mask)
            is_dropoff = vision.is_dropoff(image_diff)
            
            if is_dropoff: 
                # sound clip is 1.5s, so loop it at 0.667 plays/s
                dropoff_sound_thr.set_frequency(2./3. if is_dropoff 
                                                    else 0.000001)
                util.log("Dropoff!")
                path = dropoff_debug_dir + '/' + util.time_stamp()
                util.save_image(image_on, path+'/raw_on.jpg')
                util.save_image(image_off, path+'/raw_off.jpg')
                util.save_image(image_diff, path+'/diff.jpg')
            else:
                util.set_log_path(None)
            
        util.log('threads active: '+str(threading.active_count()))
        util.save_log_memory_to_file()
            
        #time.sleep(2.0)


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
    if not camera is None:
        camera.close()
    print "**** all resources closed ****"
    
