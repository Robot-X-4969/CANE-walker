import picamera
from picamera.streams import PiCameraCircularIO
import time
import os



def list_diffs():
	time_target = time.time() + 30.0
	os.system('rm img*.bmp; rm out*.bmp')
	
	with picamera.PiCamera() as cam:
		cam.resolution = (600, 600)
		cam.framerate = 30
		time.sleep(2)
		
		# with 
		i = 0
		while time.time() < time_target:
			file1 = 'img1-%02d.bmp' % i
			file2 = 'img2-%02d.bmp' % i
			file3 = 'out-%02d.bmp' % i
			t1 = time.time()
			cam.capture_sequence( [file1, file2] )
			t2 = time.time()
			os.system('composite -compose difference '+file1+' '+file2+' '+file3)
			t3 = time.time()
			i = i + 1
			time1 = (t2-t1, t3-t2)
			print(time1)
			
def cam_preview():
	with picamera.PiCamera() as cam:
		cam.resolution = (800, 600)
		cam.framerate = 30
		cam.led = False
		cam.start_preview()
		time.sleep(30)
		cam.stop_preview()

def capture_test_vid():
	with picamera.PiCamera() as cam:
		cam.resolution = (800, 600)
		cam.framerate = 30
		cam.led = True
		cam.start_recording("test-vid.h264")
		cam.start_preview()
		time.sleep(10)
		cam.stop_preview()
		cam.stop_recording()
		cam.led = False

def analyze_images(strImg1, strImg2):
	strCmd = 'composite -compose difference '+strImg1+' '+strImg2 + \
		' - | convert - -colorspace Gray -auto-level' + \
		'-black-threshold 95%% -white-threshold 95%% out.bmp'
	os.system( strCmd )
	

def capture_lasered_images():
        pass
        
