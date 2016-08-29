#!/bin/sh

python cane_main.py &
python newUltrasonicTest.py &
python shutdownButton.py &

