from RPi import GPIO

class Laser:
    # Instances of this class toggle specific GPIO pins
    def __init__(self, laser_pin):
        self.laserpin = laser_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.laserpin, GPIO.OUT)
        self.turn_off()

    def turn_on(self):
        GPIO.output(self.laserpin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.laserpin, GPIO.LOW)

