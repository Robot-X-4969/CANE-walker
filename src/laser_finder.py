import picamera
import time
import os


def find_difference():
	time_target = time.time() + 30.0
	os.system('rm *.bmp')
	
	with picamera.PiCamera() as cam:
		cam.resolution = (600, 600)
		cam.framerate = 30
		time.sleep(2)
		
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
			
