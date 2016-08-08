import os
import sys
import glob
from PIL import Image, ImageDraw
from src import vision

subdirs = glob.glob('training_data/*')
for dropoff_entry_dir in subdirs:
    if os.path.isdir(dropoff_entry_dir):
        label_path = dropoff_entry_dir + '/label.txt'
        if os.path.exists(label_path):
            with open(label_path, 'r') as labelfile:
                label = labelfile.readline()
        else:
            label = ''
        
        if not label in ('g','d','G','D'):
            calibration_path = dropoff_entry_dir + '/calibration.txt'
            if os.path.exists(calibration_path):
                with open(calibration_path, 'r') as calibrationfile:
                    calibration_string = calibrationfile.readline()
                    calibration_string = calibration_string.replace('(', '')
                    calibration_string = calibration_string.replace(')', '')
            else:
                calibration_string = ''
            calibration_split = calibration_string.split(';')
            if len(calibration_split) == 3:
                calibration_left_pos = (
                        float(calibration_split[0].split(', ')[0]),
                        float(calibration_split[0].split(', ')[1])
                )
                calibration_right_pos = (
                        float(calibration_split[1].split(', ')[0]),
                        float(calibration_split[1].split(', ')[1])
                )
                calibration_separation = float(calibration_split[2])
                if vision.POSITION_NOT_FOUND in (calibration_left_pos,
                                                 calibration_right_pos):
                    print 'Calibration is not helpful. Moving on'
                    continue
            else:
                print 'Calibration file does not have 3 sections. Moving on.'
                continue
            
            image = Image.open(dropoff_entry_dir+'/image_on.jpg')
            draw = ImageDraw.Draw(image)
            draw.ellipse(
                (
                    calibration_left_pos[0] - 30 + vision.cropbox[0],
                    calibration_left_pos[1] - 30 + vision.cropbox[1],
                    calibration_left_pos[0] + 30 + vision.cropbox[0],
                    calibration_left_pos[1] + 30 + vision.cropbox[1]
                ),
                fill = None, #transparent fill
                outline = (128,128,255) #partially bright outline
            )
            draw.ellipse(
                (
                    calibration_right_pos[0] - 30 + vision.cropbox[0],
                    calibration_right_pos[1] - 30 + vision.cropbox[1],
                    calibration_right_pos[0] + 30 + vision.cropbox[0],
                    calibration_right_pos[1] + 30 + vision.cropbox[1]
                ),
                fill = None,
                outline = (128,128,255)
            )
            image.show()
            label = raw_input('Enter label (g, d, or exit) -->  ')
            while not label in ('g','d','G','D','exit'):
                label = raw_input('Try again (g, d, or exit) -->  ')
            if label == 'exit':
                sys.exit(1)
            with open(label_path, 'w') as labelfile:
                labelfile.write(label)
        else: #already labeled
            print 'Already labeled. Moving on'

