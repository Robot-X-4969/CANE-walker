import math
from io import BytesIO
import itertools
from PIL import Image, ImageChops, ImageOps
from src import util

# CONSTANTS

# width to set camera, in pixels
imwidth = 640

# height to set camera, in pixels
imheight = 480 

# area in which to look for dots; top-left x,y, bottom-right x,y
cropbox = (200,0,450,480) 
cropwidth = cropbox[2] - cropbox[0]
cropheight = cropbox[3] - cropbox[1]

# number of pixels in a valid-sized laser dot (minimum)
blob_size_min = 4 

# number of pixels in a valid-sized laser dot (maximum)
blob_size_max = 45 

# number of pixels in a ideal-sized laser dot, used to sort
blob_size_ideal = 15 

# angle (radians) between the laser dots at normal distance
ideal_angle_1 = 0.33 
ideal_angle_2 = ideal_angle_1-3.14

# range of valid angles (radians) between dots
angle_allowed_1 = (0.0, 1.1) 
angle_allowed_2 = (angle_allowed_1[0]-3.14, angle_allowed_1[1]-3.14)

# relative importance of the dot size (as opposed to the angle)
size_weight = 1.0

# relative importance of the angle between a pair of dots
angle_weight = 15.0 

# The maximum allowed difference (in pixels) between the calibration
# values and the measured ones. Discrepancies exceeding these values
# are reported as a drop-off
movement_threshold_left = 60
movement_threshold_right = 50
separation_threshold = 40

# this is the position reported for one or both dots if said dot is not found
POSITION_NOT_FOUND = (-4969,-4969)


# CLASS DEFINITIONS
class ConnectedComponent:
    #  Stores information about pixels that are touching (connected to) one
    #  another. Connected components are commonly referred to as "blobs" 
    #  for short.
    #  variables:
    #      coords (list) stores coordinates of "connected" pixels
    #  useful methods:
    #      size: returns the number of connected pixels
    #      avg_position: returns the center of the connected component
    #      find_blobs: connected-component labeling implementation
        
    def __init__(self):
        self.coords = set() #creates a new set (datatype) of coordinates
        
    def __repr__(self):
        return "<position " + str(self.avg_position()) + ", size " \
                + str(self.size()) + ">"
                
    def add_coord(self, x, y):
        self.coords.add((x,y))
        
    def contains_coord(self, x, y):
        return (x,y) in self.coords
        
    def size(self):
        return len(self.coords)
        
    def avg_position(self):
        # calculates the center of the blob
        avgx = float(sum([c[0] for c in self.coords])) / float(self.size())
        avgy = float(sum([c[1] for c in self.coords])) / float(self.size())
        return (avgx,avgy)
    
    @staticmethod
    def get_owning_component(blobs, x, y):
        #identifies the component in which a pixel is connected, else None
        for blob in blobs:
            if blob.contains(x,y): return blob
        return None
    
    @staticmethod
    def is_eligible_move(pixelarray, x, y):
        # determines whether or not a connected-component finder should
        # assign the pixel at x,y (if it exists) to a connected component
        return (x >= 0 and x < cropwidth 
            and y >= 0 and y < cropheight 
            and pixelarray[x,y] > 1)

    # Implements a simple algorithm to label 4-connected components in 
    # a binary image.
    # <https://en.wikipedia.org/wiki/Connected-component_labeling>
    # Pixel values must be integers (PIL mode 'L' or similar) with 
    # false = 0 and true > 0.
    @staticmethod
    def find_blobs(image):
        pixelarray = image.load() #load pixel array
        blobs = [] #this will store the ConnectedComponent objects
        search_directions = ((1,0),(0,1),(-1,0),(0,-1)) #4-connectivity
        #for every pixel in the image:
        for x in xrange(cropwidth):
            for y in xrange(cropheight):
                #if the pixel is false or already belongs to a blob, skip it
                if (
                  pixelarray[x,y] < 1 or                  
                  ConnectedComponent.get_owning_component(blobs,x, y)!= None
                ):
                    continue
                #bright and not classified; therefore classify that shiznit
                current_component = ConnectedComponent()
                current_component.addcoord(x,y)
                blobs.append(current_component)
                #use a stack to back-track the 2D branching path
                position_history_stack = [(x,y)]
                
                #Traverse all bright pixels connected to the original
                #and label them part of the same connected component
                while len(position_history_stack) > 0:
                    old_x, old_y = position_history_stack.pop()
                    for dx,dy in search_directions:
                        new_x, new_y = old_x+dx, old_y+dy
                        #If the pixel is in bounds, is bright, has not 
                        #been visited already, and has no label...
                        if (
                          ConnectedComponent.is_eligible_move(pixelarray,
                                                              new_x, new_y)
                          and not (new_x, new_y) in position_history_stack
                          and ConnectedComponent.get_owning_component(
                                        blobs,new_x,new_y) == None
                        ):
                            #...then label it and add it to the stack
                            current_component.addcoord(new_x, new_y)
                            position_history_stack.append( (new_x,new_y) )
        #when all pixels have been exhausted, return the connected-comps list
        return blobs
    
        
class Calibration:
    # A sub-module of vision which stores calibration info.
    # Dot locations and separation are in pixels.
    leftpos = (-1,-1) 
    rightpos = (-1,-1)
    separation = -1
    
    @staticmethod 
    def calibrate(camera, laser, filepath):
        ((p1, p2), image1, image2, im1_cr, imdiff, raw_blobs, blobs) \
            = capture_to_positions(camera, laser)
        
        util.log("Vision: calibration is "+str(p1)+" and "+str(p2))
        
        Calibration.leftpos = p1 if p1[1]>p2[1] else p2
        Calibration.rightpos = p1 if p2 is Calibration.leftpos else p2
        Calibration.separation = get_dot_separation(p1,p2)
        util.save_image(image1, filepath+'/calibration1.png')
        util.save_image(image2, filepath+'/calibration2.png')
        util.save_image(imdiff, filepath+'/calibration_diff.png')
        
        success = (p1 != POSITION_NOT_FOUND and p2 != POSITION_NOT_FOUND)
        if not success:
            util.log("CALIBRATION ERROR! Failed to find 2 positions")
        return success


# UTILITY FUNCTIONS 
def is_blob_valid_size(blob):
    # determine whether a blob is the same size as a laser dot
    return blob_size_min <= blob.size() <= blob_size_max

def get_relative_dot_angle(pos1, pos2):
    # find the angle between two potential laser dots
    return math.atan2(pos2[1]-pos1[1], pos2[0]-pos1[0])

def is_valid_dot_angle(theta):
    # determine whether a pair of potential laser dots are in the correct
    # places relative to one another
    # Good:  A    or    B
    #         B          A
    #
    # Bad:    A   or     B
    #        B          A
    return (angle_allowed_1[0] < theta < angle_allowed_1[1]
         or angle_allowed_2[0] < theta < angle_allowed_2[1])

def get_dot_separation(pos1, pos2):
    # find distance in pixels between two points
    return math.sqrt( (pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 )

def get_positions_and_cost(blob1, blob2):
    # Cost function: (size error)*(size weight)+(angle error)*(angle weight)
    # As with any cost, lower is better. This is invoked only when
    # three or more blobs pass the size filter.
    position1 = blob1.avg_position()
    position2 = blob2.avg_position()
    theta = get_relative_dot_angle(position1, position2)
    if not is_valid_dot_angle(theta):
        return None
    # size factor = distance from ideal of worst-sized blob in the pairing
    # expected < 20
    size_factor = max(abs(blob1.size()-blob_size_ideal),
                      abs(blob2.size()-blob_size_ideal) )
    # angle factor = angular distance from ideal
    # expected < 0.8
    angle_factor = min(abs(theta-ideal_angle_1), 
                       abs(theta-ideal_angle_2) )
    # calculate the "cost"
    cost = (size_factor*size_weight + angle_factor*angle_weight)
    return ((position1, position2), cost)


# MAIN LOGIC

def differentiate_images(image_on, image_off):
    # Take two images, one with laser on and one with it off, and calculate
    # an image that describes what changed from one to the other using PIL's 
    # difference() method
    # 1. crop and convert to grayscale
    image_on = image_on.crop(cropbox).convert('L')
    image_off = image_off.crop(cropbox).convert('L')
    # 2. find difference image
    image_diff = ImageChops.difference(image_on,image_off)
    # 3. adjust brightness such that the darkest pixel is 0 and the 
    #    brightest is 255
    image_diff = ImageOps.autocontrast(image_diff)
    # 4. binarize image by setting every pixel to either 0 or 255
    image_diff = image_diff.point(lambda x: 0 if x<160 else 255)
    return (image_diff, image_on, image_off)





def image_process(image_on, image_off):
    # Find two laser dot points given the laser-on and laser-off pictures.
    # 1. run image difference finder
    (image_diff, image_on_cr, image_off_cr) = differentiate_images(
                                              image_on,image_off)
    # 2. find connected components in the diff image and store it as 
    #    raw_blobs (unsorted)
    raw_blobs = ConnectedComponent.find_blobs(image_diff)
    # 3. get rid of all blobs with incorrect sizes
    possible_dots = filter(is_blob_valid_size, raw_blobs)
    util.log("Vision: " + str(len(raw_blobs)) + " raw blobs")
    util.log("Vision: " + str(len(possible_dots)) + " correctly sized blobs")
    if len(possible_dots) <= 2:
        # 4a. if 2 or fewer dots are found, their positions are 
        #     automatically the best
        best_positions = [b.avg_position() for b in possible_dots]
    else:
        # 4b. if 3 or more dot are found, choose the combination
        #     (using itertools.combinations()) with the lowest cost
        combos = list(itertools.combinations(possible_dots, 2))
        positions_and_costs = []
        for b1,b2 in combos:
            pos_cost = get_positions_and_cost(b1,b2)
            if pos_cost != None:
                positions_and_costs.append(pos_cost)
        util.log("Vision: "+str(len(combos))+" pairs of blobs")
        util.log("Vision: "+str(len(positions_and_costs)) \
                                +" at correct angles")
        if len(positions_and_costs) > 0:
            # 4c. find the minimum cost (the 'key' tells min() to sort by
            # cost and not position). After selecting, the index 0 grabs the
            # position tuple and ignores the cost
            key_fn = lambda position_with_cost: position_with_cost[1]
            best_positions = min(positions_and_costs, key=key_fn)[0]
        else:
            best_positions = []
    util.log("positions:   " + str(best_positions))
    util.log("calibration: "+str((Calibration.leftpos, Calibration.rightpos)))
    # if less than 2 blobs were found, give the "no blob" position
    out_positions = (
      best_positions[0] if len(best_positions)>0 else POSITION_NOT_FOUND, \
      best_positions[1] if len(best_positions)>1 else POSITION_NOT_FOUND  )
    return (out_positions, image_on, image_off, image_on_cr, 
                image_diff, raw_blobs, possible_dots)


def capture_images(camera, laser):
    # use picamera and PIL modules to capture images
    imfile1, imfile2 = BytesIO(), BytesIO()
    laser.turn_on()
    # Use video port for rapid capture without de-noising algorithms.
    # jpeg format is also faster due to hardware acceleration
    camera.capture(imfile1, format='jpeg', use_video_port=True)
    laser.turn_off()
    camera.capture(imfile2, format='jpeg', use_video_port=True)
    imfile1.seek(0)
    imfile2.seek(0)
    # PIL image generation
    im1 = Image.open(imfile1)
    im2 = Image.open(imfile2)
    return im1, im2

# Combine image capture and processing into one function
def capture_to_positions(camera, laser):
    im1, im2 = capture_images(camera, laser)
    return image_process(im1, im2)

# Determine if the two laser dot points (or lack thereof) indicate 
# a dropoff. If left position, right position, or their separation is
# wrong, return true
def is_dropoff(pos1, pos2):
    bad_signs = 0
    (L, R) = (pos1, pos2) if pos1[1]>pos2[1] else (pos2, pos1)
    
    if get_dot_separation(L, Calibration.leftpos) > movement_threshold_left:
        util.log("Vision: left dot looks like a dropoff")
        bad_signs += 1
    else:
        util.log("Vision: left dot is okay")
        
    if get_dot_separation(R, Calibration.rightpos)> movement_threshold_right:
        util.log("Vision: right dot looks like a dropoff")
        bad_signs += 1
    else:
        util.log("Vision: right dot is okay")
        
    if (
      abs(get_dot_separation(L,R) - Calibration.separation) 
      > separation_threshold
    ):
        util.log("Vision: separation distance looks like a dropoff")
        bad_signs += 1
    else:
        util.log("Vision: separation distance is okay")
    # if anything looks suspicious, return true
    return bad_signs > 0
    
