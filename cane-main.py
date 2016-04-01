import picamera
from time import sleep

with picamera.PiCamera() as cam:
    cam.resolution = (640, 480)
    cam.start_preview()
    sleep(20)
    cam.stop_preview()

