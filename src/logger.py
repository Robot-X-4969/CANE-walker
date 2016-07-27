from datetime import datetime
import os

def log(L, s):
    print s
    if not L is None:
        L.append(s)

def log_dropoff(dropoff_debug_dir, imon, imoff, cropped, imdiff, loglines):
    path = dropoff_debug_dir + date_time() + '/'
    os.makedirs(path)
    imon.save(path+'raw_on.jpg')
    imoff.save(path+'raw_off.jpg')
    cropped.save(path+'cropped_on.jpg')
    imdiff.save(path+'diff.jpg')
    with open(path+'log.txt', 'w') as logfile:
        for line in loglines:
            logfile.write( (line+"\n") )

def log_calibration(inputpath, im1, im2, imdiff):
    filepath = inputpath + date_time() + '/'
    os.makedirs(filepath)
    im1.save(filepath+'calibration1.png')
    im2.save(filepath+'calibration2.png')
    imdiff.save(filepath+'calibration_diff.png')

def safe_remove_dirs(*paths):
    if paths is not None:
        for path in paths:
            if os.path.exists(path):
                os.system('rm -r '+path)
            
def date_time():
    return str(datetime.now()).replace(':', ' ')
