from PIL import ImageChops, ImageOps
from math import sqrt


imwidth = 640
imheight = 480
cropbox = (200,0,450,480) #find better values
cropwidth = 250
cropheight = 480
blob_size_min = 7
blob_size_max = 36


def differentiate_images(imon, imoff):
    imon = imon.crop(cropbox)
    imoff = imoff.crop(cropbox)
    imdiff = ImageChops.difference(imon,imoff).convert('L')
    imdiff = ImageOps.autocontrast(imdiff)
    imdiff = imdiff.point(lambda x: 0 if x<200 else 255)
    return imdiff


class ConnectedComponent:
    def __init__(self):
        self.coords = set()
    def __repr__(self):
        return "position "+str(self.avg_position())+", size "+str(self.size())
    def addcoord(self, x, y):
        self.coords.add((x,y))
    def contains(self, x, y):
        return (x,y) in self.coords
    def size(self):
        return len(self.coords)
    def avg_position(self):
        avgx = float(sum([c[0] for c in self.coords])) / float(self.size())
        avgy = float(sum([c[1] for c in self.coords])) / float(self.size())
        return (avgx,avgy)

def find_connected_components(img):
    pxarr = img.load()
    blobs = []
    search_dirs = ((1,0),(0,1),(-1,0),(0,-1))
    for x in xrange(cropwidth):
        for y in xrange(cropheight):
            if pxarr[x,y]<1 or _get_owning_component(blobs,x,y) != None:
                continue
            #bright and not classified; therefore classify that shiznit
            currentcomp = ConnectedComponent()
            currentcomp.addcoord(x,y)
            blobs.append(currentcomp)
            posstack = [(x,y)]
            while len(posstack) > 0:
                tmpx, tmpy = posstack.pop()
                for dx,dy in search_dirs:
                    newx, newy = tmpx+dx, tmpy+dy
                    if _eligible_move(pxarr,newx,newy) and not (newx,newy) in posstack \
                            and _get_owning_component(blobs,newx,newy) == None:
                        posstack.append((newx,newy))
                        currentcomp.addcoord(newx,newy)
    return blobs

def _get_owning_component(blobs, x, y):
    for blob in blobs:
        if blob.contains(x,y): return blob
    return None

def _eligible_move(pxarr, x, y):
    return x>=0 and x<cropwidth and y>=0 and y<cropheight and pxarr[x,y]>1

def _blob_size_filter(blob):
    return blob_size_min <= blob.size() <= blob_size_max
    
def _blob_usage_cost(blob):
    #temporary strategy: closest to size 18
    return abs(blob.size() - 18)

def image_process(image1, image2, verbose_output=False):
    imdiff = differentiate_images(image1,image2)
    raw_blobs = find_connected_components(imdiff)
    blobs = [b for b in filter(_blob_size_filter, raw_blobs)]
    good_positions = ((0,0),(0,0))
    if len(blobs) < 2:
        if verbose_output: print "Vision: Warning: Fewer than 2 blobs found"
    elif len(blobs) == 2:
        good_positions = (blobs[0].avg_position(), blobs[1].avg_position())
        if verbose_output: print "Vision: Exactly 2 blobs found"
    elif len(blobs) > 2:
        srt_list = sorted(blobs, key=_blob_usage_cost)
        good_positions = (srt_list[0].avg_position(), srt_list[1].avg_position())
        if verbose_output: print "Vision: More than 2 blobs found, sorted"
    if verbose_output:
        return (good_positions, imdiff, raw_blobs, blobs)
    else:
        return good_positions

def dot_separation(pos1, pos2):
    return sqrt( (pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2 )

