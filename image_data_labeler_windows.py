import os
import sys
import glob
from PIL import Image, ImageDraw
from src import vision

# get all paths in the training data directory
subdirs = glob.glob('training_data/*')

# for each path found:
for dropoff_entry_dir in subdirs:
    # if the path doesn't point to a directory, skip it
    if os.path.isdir(dropoff_entry_dir):
        # check if a label file exists. if not, label is an empty string
        label_path = dropoff_entry_dir + '/label.txt'
        if os.path.exists(label_path):
            with open(label_path, 'r') as labelfile:
                label = labelfile.readline()
        else:
            label = ''
        
        # If the label is empty or not recognized, then a new one needs to be
        # written. Will display the laser-on image with circles surrounding
        # the calibration points, then prompt user for input
        if not label in ('g','d','G','D'):
            # Read the calibration file as a string. Format should be
            # "(x1,y1);(x2,y2);separation"
            calibration_path = dropoff_entry_dir + '/calibration.txt'
            if os.path.exists(calibration_path):
                with open(calibration_path, 'r') as calibrationfile:
                    calibration_string = calibrationfile.readline()
                    # remove parentheses from the string
                    calibration_string = calibration_string.replace('(', '')
                    calibration_string = calibration_string.replace(')', '')
            else:
                calibration_string = ''
            
            # split the string into sections. Ideally, index 0 is "x1,y1",
            # index 1 is "x2,y2", and index 3 is the separation
            calibration_split = calibration_string.split(';')
            
            # calibration could be empty or improperly formatted
            if len(calibration_split) == 3:
                # Parse index 0 to a numeric value for left calibration point
                calibration_left_pos = (
                        float(calibration_split[0].split(', ')[0]),
                        float(calibration_split[0].split(', ')[1])
                )
                # Parse index 1 to a numeric for right calibration point
                calibration_right_pos = (
                        float(calibration_split[1].split(', ')[0]),
                        float(calibration_split[1].split(', ')[1])
                )
                # parse separation
                calibration_separation = float(calibration_split[2])
                if vision.POSITION_NOT_FOUND in (calibration_left_pos,
                                                 calibration_right_pos):
                    print 'Calibration is not helpful. Moving on'
                    continue
                
            else: #the calibration file is empty or improperly formatted
                print 'Calibration file does not have 3 sections. Moving on.'
                continue
            
            # use PIL.ImageDraw to draw circles around the calibration points
            image = Image.open(dropoff_entry_dir+'/image_on.jpg')
            draw = ImageDraw.Draw(image)
            # Draw circle. Calibration pixels refer to a cropped picture,
            # so the circles draw are shifted according to the cropping 
            # parameters from vision
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
                
            # Display image using system default image viewer
            image.show()
            
            # When that window is closed, prompt user for new label
            label = raw_input('Enter label (g, d, or exit) -->  ')
            while not label in ('g','d','G','D','exit'):
                label = raw_input('Try again (g, d, or exit) -->  ')
            if label == 'exit':
                sys.exit(1)
            # write new label to label file
            with open(label_path, 'w') as labelfile:
                labelfile.write(label)
                
        
        else: #already labeled
            print 'Already labeled. Moving on'

