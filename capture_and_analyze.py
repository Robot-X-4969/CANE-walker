import picamera, io, time
from src import vision, laser
from PIL import Image

totalstart = time.time()

imfile1, imfile2 = io.BytesIO(), io.BytesIO()
#imfile1, imfile2 = 'laseron.jpeg', 'laseroff.jpeg'

with picamera.PiCamera() as cam:
    cam.resolution = (640, 480)
    cam.led = False
    cam.framerate = 85
    imagestart = time.time()
    laser.turn_on()
    cam.capture(imfile1, format='jpeg', use_video_port=True)
    laser.turn_off()
    cam.capture(imfile2, format='jpeg', use_video_port=True)
    imageend = time.time()
    
imfile1.seek(0)
imfile2.seek(0)
im1 = Image.open(imfile1)
im2 = Image.open(imfile2)

processstart = time.time()
((pos1,pos2), imdiff, raw_blobs, blobs) = vision.image_process(im1, im2, vebose_output=True)
dot_separation = vision.dot_separation(pos1, pos2)
processend = totalend = time.time()

print "all blobs identified: "+str([b for b in raw_blobs])
print "blobs chosen: "+str([b for b in blobs])
print "dot separation: "+str(dot_separation)
print "captured images in "+str(imageend-imagestart)+" seconds"
print "processed images in "+str(processend-processstart)+" seconds"
print "total runtime in "+str(totalend-totalstart)+" seconds"

imdiff.save('img-output/diff_image.png')
im1.save('img-output/img1.png')
im2.save('img-output/img2.png')

markup = im1.copy()
markup = markup.convert('RGB').crop(vision.cropbox)
blue = Image.new('RGB', markup.size, color=(0,0,200))
markup.paste(blue, mask=imdiff)
markup.save('img-output/markup.png')
