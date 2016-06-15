import picamera, io, time, csv
from src import vision, laser
from PIL import Image

with picamera.PiCamera() as cam:
    cam.resolution = (640, 480)
    cam.led = False
    cam.framerate = 55
    time.sleep(2.0)
    
    with open('laser-warmup-data.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel')
        writer.writerow(["delay", "blobs found", "size 1", "size 2"])
        
        for delay in [x*0.02 for x in range(1,15)]:
            imfile1, imfile2 = io.BytesIO(), io.BytesIO()
            laser.turn_on()
            time.sleep(delay)
            cam.capture(imfile1, format='jpeg', use_video_port=True)
            laser.turn_off()
            #time.sleep(0.2)
            cam.capture(imfile2, format='jpeg', use_video_port=True)
    
            imfile1.seek(0)
            imfile2.seek(0)
            im1 = Image.open(imfile1)
            im2 = Image.open(imfile2)

            ((pos1,pos2), imdiff, raw_blobs, blobs) = vision.image_process(
                    im1, im2, verbose_output=True)
            size1 = blobs[0].size() if len(blobs)>0 else 0
            size2 = blobs[1].size() if len(blobs)>1 else 0
            writer.writerow([delay, len(raw_blobs), size1, size2])
            print "finished measurement "#+str(loopnum)
            
            time.sleep(0.1)

