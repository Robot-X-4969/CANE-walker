from picamera import PiCamera
import time
from src import vision
from src.laser import Laser
from datetime import datetime

laser = Laser(12) #will be changed to 5
camera = PiCamera()


try:
    camera.led = False
    camera.resolution = (640,480)
    camera.framerate = 55
    time.sleep(2.0)
    vision.Calibration.calibrate(camera, laser)
    
    while True:
        start = time.time()        
        ((pos1, pos2), image1, image2, imdiff, raw_blobs, blobs) = \
            vision.capture_to_positions(camera, laser, verbose=True)
        dropoff = vision.is_dropoff(pos1, pos2, verbose=True)
        end = time.time()
        
        print "all blobs identified:"
        for b in raw_blobs:
            print "    "+str(b)
        print "blobs chosen:"
        for b in blobs:
            print "    "+str(b)
        print "dropoff: "+str(dropoff)
        print "time taken: "+str(end-start)
        
        # if a drop-off is found, record associated image data for human study
        if dropoff:
            image1.save('img-output/image1 '+str(datetime.now())+'.png')
            image2.save('img-output/image2 '+str(datetime.now())+'.png')
            imdiff.save('img-output/imdiff '+str(datetime.now())+'.png')
        
        time.sleep(0.5)


finally:
    camera.close()
    print "**** closed camera ****"