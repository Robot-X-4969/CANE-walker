import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(12, GPIO.OUT)

while True:

	GPIO.output(12, GPIO.HIGH)
	print("on")
	time.sleep(1)
	GPIO.output(12, GPIO.LOW)
	print("off")
	time.sleep(1)
