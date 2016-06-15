from picamera import PiCamera
import time
from src import vision, laser
from datetime import datetime

try:
    camera = PiCamera()
    camera.led = False
    camera.resolution = (640,480)
    camera.framerate = 55
    time.sleep(2.0)
    vision.Calibration.calibrate(camera)
    
    while True:
        start = time.time()        
        ((pos1, pos2), image1, image2, imdiff, raw_blobs, blobs) = \
            vision.capture_to_positions(camera, laser.turn_on, \
            laser.turn_off, verbose=True)
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
            dir_out = 'img_output/dropoff '+str(datetime.now())+'/'
            image1.save(dir_out+'image1.png')
            image2.save(dir_out+'image2.png')
            imdiff.save(dir_out+'imdiff.png')
        
        time.sleep(5.0)


finally:
    camera.close()
    print "**** closed camera ****"