from src import ultrasonic_sensor as usmod
import time


try:
    usmod.setup()
    while True:
        print("Distance:", usmod.find_dist())
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

