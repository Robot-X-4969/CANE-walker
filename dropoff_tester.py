from glob import glob
import os
from PIL import Image
from src import vision, util

util.set_log_modes(util.LogMode.USE_STDOUT)

tested_count = 0
correct_count = 0

items = glob('training_data/*')
subdirs = filter(os.path.isdir, items)
if len(subdirs) == 0:
    util.log('Found no directories to train from. Exiting')    
else:    
    for current_dir in subdirs:
        label_path = current_dir + '/label.txt'
        if os.path.exists(label_path):
            with open(label_path, 'r') as label_file:
                label = label_file.readline()
        else:
            util.log('Dataset has no label file. Skipping '+current_dir)
            continue
        
        if not label in ('g','G','d','D'):
            util.log('Did not understand label "'+label+'". Skipping '
                     + current_dir)
            continue
        
        # Taken from image labeler. See documentation there
        calibration_path = current_dir + '/calibration.txt'
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
            
            # skip testing on this image if the calibration is not complete
            if vision.POSITION_NOT_FOUND in (calibration_left_pos,
                                             calibration_right_pos):
                util.log('Calibration is not helpful. Skipping '+current_dir)
                continue
        
        else:
            util.log('Calibration file does not have 3 sections. Skipping '
                     + current_dir)
            continue
        
        # Test whether both image files exist. If not, skip this folder
        image_on_path = current_dir + '/image_on.jpg'
        image_off_path = current_dir + '/image_off.jpg'
        if not (os.path.exists(image_on_path) 
                and os.path.exists(image_off_path)):
            util.log('Could not find two images. Skipping '+current_dir)
            continue
        
        # If we have reached this point, the test of dropoff algorithm
        # against labeled data can be run. Step 1: transfer calibration data
        # to the vision module
        vision.Calibration.leftpos = calibration_left_pos
        vision.Calibration.rightpos = calibration_right_pos
        vision.Calibration.separation = calibration_separation
        
        # open images in PIL
        image_on = Image.open(image_on_path)
        image_off = Image.open(image_off_path)
        
        # process images to find positions (ignoring other debugging outputs)
        (pos1,pos2),_,_,_,_,_,_ = vision.image_process(image_on, image_off)
        dropoff_tested = vision.is_dropoff(pos1, pos2)
        
        # convert label to boolean
        dropoff_label = (label in ('g','G'))
        tested_count += 1
        # compare tested value and labeled one
        if dropoff_label == dropoff_tested:
            util.log('label and test match as '+str(dropoff_tested))
            correct_count += 1
        else:
            # if the labels don't match, log info to let user find the 
            # images
            util.log('test '+str(dropoff_tested)+' does not match label '
                     + str(dropoff_label)+' in dataset '+current_dir)

if tested_count > 0:
    percent = 100.0 * float(correct_count) / float(tested_count)
    util.log('summary: %s correct answers of %s, or %.2f percent'
              % (correct_count, tested_count, percent))

