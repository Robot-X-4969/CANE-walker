import picamera
from src import vision, laser, util


datadir = 'training_data'
util.super_remove_dirs(datadir)

try:
    cam = picamera.PiCamera()
    cam.led = False
    cam.resolution = (vision.imwidth, vision.imheight)
    cam.framerate = 75
    laser = laser.Laser(5)
    counter = 1
    
    raw_input('Press enter to calibrate')
    vision.Calibration.calibrate(cam, laser, None)
    print 'calibrated positions:'
    print vision.Calibration.leftpos
    print vision.Calibration.rightpos
    print ''
    
    while True:
        raw_input('Press enter to take picture set '+str(counter))
        counter += 1
        imon, imoff = vision.capture_images(cam, laser)
        datapath = datadir + '/' + str(util.time_stamp())
        util.save_image(imon, datapath + '/image_on.jpg')
        util.save_image(imoff, datapath + '/image_off.jpg')
        with open(datapath + '/calibration.txt', 'w') as calibrationfile:
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
