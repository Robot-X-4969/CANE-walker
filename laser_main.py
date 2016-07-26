from picamera import PiCamera
import time
from src import vision
from src.laser import Laser
from datetime import datetime

laser = Laser(12) #will be changed to 5
camera = PiCamera()
logfile = open('Log.txt', 'w')

def log(s):
    print s
    logfile.write(s + "\n")


try:
    camera.led = False
    camera.resolution = (640,480)
    camera.framerate = 55
    time.sleep(2.0)
    vision.Calibration.calibrate(camera, laser)
    log("calibration complete")
    
    while True:
        log('\n')
        start = time.time()        
        ((pos1, pos2), image1, image2, imdiff, raw_blobs, blobs) = \
            vision.capture_to_positions(camera, laser, verbose=True)
        dropoff = vision.is_dropoff(pos1, pos2, verbose=True)
        end = time.time()
        
        log("all blobs identified:")
        for b in raw_blobs:
            log("    "+str(b))
        log("blobs chosen:")
        for b in blobs:
            log("    "+str(b))
        log("dropoff: "+str(dropoff))
        log("time taken: "+str(end-start))
        
        # if a drop-off is found, record associated image data for human study
        if dropoff:
            log("writing files to sd card")
            image1.save('img-output/image1 '+str(datetime.now())+'.png')
            image2.save('img-output/image2 '+str(datetime.now())+'.png')
            imdiff.save('img-output/imdiff '+str(datetime.now())+'.png')
        
        time.sleep(0.5)


finally:
    camera.close()
    log("**** closed camera ****")
    logfile.close()
