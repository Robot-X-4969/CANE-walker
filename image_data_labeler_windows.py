import os
import glob
from PIL import Image, ImageDraw

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
            else:
                print 'Calibration file does not have 3 sections. Moving on.'
                continue
            
            image = Image.open(dropoff_entry_dir+'/image_on.jpg')
            draw = ImageDraw.Draw(image, mode='rgba')
            draw.ellipse(
                (
                    calibration_left_pos[0] - 30,
                    calibration_left_pos[1] - 30,
                    calibration_left_pos[0] + 30,
                    calibration_left_pos[1] + 30
                ),
                fill = (0,0,0,0), #transparent fill
                outline = (255,255,255,127) #partially transparent outline
            )
            draw.ellipse(
                (
                    calibration_right_pos[0] - 30,
                    calibration_right_pos[1] - 30,
                    calibration_right_pos[0] + 30,
                    calibration_right_pos[1] + 30
                ),
                fill = (0,0,0,0),
                outline = (255,255,255,127)
            )
            image.show()
            label = raw_input('Enter label (g or d) -->  ')
            while not label in ('g','d','G','D'):
                label = raw_input('Try again (g or d) -->  ')
            with open(label_path, 'w') as labelfile:
                labelfile.write(label)

