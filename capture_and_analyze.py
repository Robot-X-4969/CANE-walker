import picamera, time
from src import vision
from src.laser import Laser
from PIL import Image

laser = Laser(12)
camera = picamera.PiCamera()
camera.led = False
camera.resolution = (640,480)
camera.framerate = 55
time.sleep(2.0)

totalstart = time.time()
try:  
    ((pos1, pos2), imon, imoff, imdiff, raw_blobs, blobs) = \
        vision.capture_to_positions(camera, laser, verbose=True)
    dot_separation = vision._dot_separation(pos1, pos2)
    dropoff = vision.is_dropoff(pos1, pos2, verbose=True)
    totalend = time.time()
finally:
    camera.close()

print "all blobs identified: "+str([b for b in raw_blobs])
print "blobs chosen: "+str([b for b in blobs])
print "dot separation: "+str(dot_separation)
print "drop-off is "+str(dropoff)
print "total runtime in "+str(totalend-totalstart)+" seconds"

imdiff.save('img-output/diff_image.png')
imon.save('img-output/img1.png')
imoff.save('img-output/img2.png')

markup = imon.copy()
markup = markup.convert('RGB').crop(vision.cropbox)
blue = Image.new('RGB', markup.size, color=(0,0,200))
markup.paste(blue, mask=imdiff)
markup.save('img-output/markup.png')
