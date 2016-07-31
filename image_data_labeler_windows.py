import os
import glob
from PIL import Image

subdirs = glob.glob('training_data/*')
for dropoff_entry_dir in subdirs:
    if os.path.isdir(dropoff_entry_dir):
        #print os.path.basename(dropoff_entry_dir)
        labelpath = dropoff_entry_dir + '/label.txt'
        if os.path.exists(labelpath):
            with open(labelpath, 'r') as labelfile:
                label = labelfile.readline()
        else:
            label = ''
        if not (label=='g' or label=='d'):
            imon = Image.open(dropoff_entry_dir+'/image_on.jpg')
            imon.show()
            with open(labelpath, 'w') as labelfile:
                labelfile.write(raw_input('Enter label (g or d) --> '))

