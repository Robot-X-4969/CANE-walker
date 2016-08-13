import time
import picamera
from src import vision, laser, util

# directory (no final slash) in which data sets should be stored on the pi
datadir = 'training_data'


try:
    # initialize the camera in the same way as in cane_main
    cam = picamera.PiCamera()
    cam.led = False
    cam.resolution = (vision.imwidth, vision.imheight)
    cam.framerate = 75
    time.sleep(1.0)
    
    # initialize the laser
    lasr = laser.Laser(5)
    
    # image counter, for more descriptive output
    counter = 1
    
    # Calibrate the walker after user has set up the hardware. Then print
    # out the values it found
    raw_input('Press enter to calibrate')
    vision.Calibration.calibrate(cam, lasr, None)
    
    # adjust calibration values to eliminate dependency on crop parameters
    vision.Calibration.leftpos[0] += vision.cropbox[0]
    vision.Calibration.leftpos[1] += vision.cropbox[1]
    vision.Calibration.rightpos[0] += vision.cropbox[2]
    vision.Calibration.rightpos[1] += vision.cropbox[3]
    
    print 'calibrated positions:'
    print vision.Calibration.leftpos
    print vision.Calibration.rightpos
    print ''
    
    while True:
        # delay until user has the walker in a good test position
        raw_input('Press enter to take picture set '+str(counter))
        counter += 1
        
        # capture two images
        imon, imoff = vision.capture_images(cam, lasr)
        
        # save images with their calibration in time-stamped directory
        datapath = datadir + '/' + str(util.time_stamp())
        util.save_image(imon, datapath + '/image_on.jpg')
        util.save_image(imoff, datapath + '/image_off.jpg')
        with open(datapath + '/calibration.txt', 'w') as calibrationfile:
            # calibration format (no spaces):
            # (x1,y1);(x2,y2);separation
            calibrationfile.write(str(vision.Calibration.leftpos)
                    + ';' + str(vision.Calibration.rightpos)
                    + ';' + str(vision.Calibration.separation)
            )

except KeyboardInterrupt:
    # gracefully exit when ctrl-C is pressed
    pass

finally:
    # close camera and switch off lasers, just in case
    cam.close()
    lasr.turn_off()
    print '\n** closed resources **'
