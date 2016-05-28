# -*- coding: utf-8 -*-
"""
Created on Fri May 27 21:12:38 2016

@author: Evan
"""

from PIL import Image
from src import laser_finder
import time
imon = Image.open('on1.png')
imoff = Image.open('off1.png')
start = time.time()

imdiff = laser_finder.differentiate_images(imon, imoff)
connected_components = laser_finder.find_connected_components(imdiff)
test = lambda c: 5 < c.size() < 30
correct_dots = [c for c in connected_components if test(c)]
positions = [c.avg_position() for c in correct_dots]

print "total processing time:", (time.time() - start)
print "number of components identified:", len(connected_components)
print "dot positions:"
for pos in positions: print "    ", pos
print "dot pixel list:"
for comp in correct_dots: print "    ", comp.coords
    
markup = imdiff.copy()
markup = markup.convert('RGB')
markuparr = markup.load()
for comp in correct_dots:
    for x,y in comp.coords:
        markuparr[x,y] = (0,255,0)
markup.show()
