from RPi import GPIO

laserpin = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(laserpin, GPIO.OUT)

def turn_on():
    GPIO.output(laserpin, GPIO.HIGH)

def turn_off():
    GPIO.output(laserpin, GPIO.LOW)

