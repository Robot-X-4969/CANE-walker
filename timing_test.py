import os
import picamera
import time
from src import laser_finder

with picamera.PiCamera() as cam:
    cam.resolution = (800,600)
    time.sleep(2.0)

    start1 = time.time()
    cam.capture('timingimage1.bmp', format='bmp', use_video_port=False)
    time1 = time.time() - start1

    time.sleep(0.1)
    start2 = time.time()
    cam.capture('timingimage2.bmp', format='bmp', use_video_port=True)
    time2 = time.time() - start2

    time.sleep(0.1)
    start3 = time.time()
    cam.capture_sequence(list(range(10)), format='bmp', use_video_port=True)
    time3 = time.time() - start3

start4 = time.time()
laser_finder.analyze_images('timingimage1.bmp', 'timingimage2.bmp')
time4 = time.time() - start4

print('single image, image port:', time1)
print('single image, video port:', time2)
print('10 images, video port:', time3)
print('800x600 image analysis:', time4)
