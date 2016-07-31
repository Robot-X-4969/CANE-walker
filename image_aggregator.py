import os
import picamera
from src import vision, laser, logger


datadir = 'training_data/'

try:
    cam = picamera.PiCamera()
    laser = laser.Laser(12)
    counter = 1
    
    raw_input('Press enter to calibrate')
    vision.Calibration.calibrate(cam, laser)
    print vision.Calibration.leftpos
    print vision.Calibration.rightpos
    
    while True:
        raw_input('Press enter to take picture set '+str(counter))
        counter += 1
        imon, imoff = vision.capture_images(cam, laser)
        datapath = datadir + str(logger.date_time()) + '/'
        if not os.path.exists(datapath):
            os.makedirs(datapath)
        imon.save(datapath + 'image_on.jpg')
        imoff.save(datapath + 'image_off.jpg')
        with open(datapath + 'calibration.txt') as calibrationfile:
            calibrationfile.write(str(vision.Calibration.leftpos)
                    + ';' + str(vision.Calibration.rightpos)
                    + ';' + str(vision.Calibration.separation)
                    )

except KeyboardInterrupt:
    pass

finally:
    cam.close()
    laser.turn_off()
    print '\n** closed resources **'
