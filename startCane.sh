#!/bin/sh

python cane_main.py &
python newUltrasonicTest.py &
python shutdown_button.py &

