from src import ultrasonic_sensor as usmod

#TODO fix pin locations
sensors = [
	UltrasonicSensor(22,18),
	# UltrasonicSensor(22,19),
	# UltrasonicSensor(22,20),
	# UltrasonicSensor(22,21),
]

sense_threads = []

try:
    while True:
        for s in sensors:
            thread = s.get_distance_thread()
            sense_threads.append( thread )
            thread.start()
        for t in sense_threads:
            t.join()
except KeyboardInterrupt:
    for t in sense_threads:
        t.join()

