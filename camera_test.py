import picamera
import time

with picamera.PiCamera() as cam:
    cam.resolution = (800,600)
    cam.start_preview()
    time.sleep(30)
    cam.stop_preview()

