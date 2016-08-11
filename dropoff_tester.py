from glob import glob
import os
import time
from PIL import Image
from src import vision, util

util.set_log_modes(util.LogMode.USE_NONE)

tested_count = 0
correct_count = 0
label_dropoff_count = 0
test_dropoff_count = 0

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
            calibration_left_pos = [
                    float(calibration_split[0].split(', ')[0]),
                    float(calibration_split[0].split(', ')[1])
            ]
            calibration_right_pos = [
                    float(calibration_split[1].split(', ')[0]),
                    float(calibration_split[1].split(', ')[1])
            ]
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
        calibration_left_pos[0] -= vision.cropbox[0]
        calibration_left_pos[1] -= vision.cropbox[1]
        calibration_right_pos[0] -= vision.cropbox[0]
        calibration_right_pos[1] -= vision.cropbox[1]
        vision.Calibration.leftpos = calibration_left_pos
        vision.Calibration.rightpos = calibration_right_pos
        vision.Calibration.separation = calibration_separation
        
        # open images in PIL
        image_on = Image.open(image_on_path)
        image_off = Image.open(image_off_path)
        
        # process images to find positions (ignoring other debugging outputs)
        time_analysis_start = time.clock()
        (pos1,pos2),_,_,_,image_diff,raw_blobs,possible_dots \
                = vision.image_process(image_on, image_off)
        dropoff_tested = vision.is_dropoff(pos1, pos2)
        analysis_time = time.clock() - time_analysis_start
        if dropoff_tested:
            test_dropoff_count += 1
            
        util.set_log_modes(util.LogMode.USE_STDOUT)
        
        util.log('calibration after adjustments: '+str(calibration_left_pos)
                 + ' - ' + str(calibration_right_pos))
        
        if analysis_time > 0.2:
            util.log('time warning: %s took %.3f seconds' 
                     % (current_dir, analysis_time))
            util.save_image(image_diff, current_dir+'/image_diff.jpg')
        
        # convert label to boolean
        dropoff_label = (label in ('d','D'))
        if dropoff_label:
            label_dropoff_count += 1
        
        tested_count += 1
        
        # compare tested value and labeled one
        if dropoff_label == dropoff_tested:
            util.log('label and test match as '+str(dropoff_tested))
            correct_count += 1
            
            # the test was successful, so delete any debugging data from 
            # the this image set
            #diff_path = current_dir+'/image_diff.jpg'
            #if os.path.exists(diff_path):
                #os.remove(diff_path)
                
        else:
            # if the labels don't match, log info to let user find the 
            # images
            util.log('test '+str(dropoff_tested)+' does not match label '
                     + str(dropoff_label)+' in dataset '+current_dir)
            util.log('  '+str(len(raw_blobs))+' blobs found')
            util.log('  '+str(len(possible_dots))+' possible laser dots')
            util.save_image(image_diff, current_dir+'/image_diff.jpg')
        
        util.set_log_modes(util.LogMode.USE_NONE)

if tested_count > 0:
    util.set_log_modes(util.LogMode.USE_STDOUT)
    percent = 100.0 * float(correct_count) / float(tested_count)
    util.log('summary: %d correct answers of %d, or %.2f percent'
              % (correct_count, tested_count, percent))
    util.log('%d dropoffs labeled vs %d good' 
             % (label_dropoff_count, tested_count - label_dropoff_count))
    util.log('%d dropoffs tested vs %d good' 
             % (test_dropoff_count, tested_count - test_dropoff_count))

