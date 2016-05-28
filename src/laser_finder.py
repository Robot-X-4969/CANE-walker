import time, os, threading
from PIL import Image, ImageChops, ImageOps
try:
    import picamera
    from picamera.streams import PiCameraCircularIO
except ImportError:
    pass


imwidth = 500
imheight = 500


def differentiate_images(imon, imoff):
    imdiff = ImageChops.difference(imon,imoff).convert('L')
    imdiff = ImageOps.autocontrast(imdiff)
    imdiff = imdiff.point(lambda x: 0 if x<200 else 255)
    return imdiff


class ConnectedComponent:
    def __init__(self):
        self.coords = set()
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
    for x in xrange(imwidth):
        for y in xrange(imheight):
            if pxarr[x,y]<1: 
                continue
            currentcomp = _get_owning_component(blobs,x,y)
            if currentcomp != None: 
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
    return x>=0 and x<imwidth and y>=0 and y<imheight and pxarr[x,y]>1






















#class LaserFinder(threading.Thread):
#    def __init__(self):
#        threading.Thread.__init__(self)
#    
#    def run(self):
#        with picamera.PiCamera() as camera:
#            camera.led = False
#            camera.resolution = (640,480)
#            camera.capture_continuous(
#                'image{timestamp:%H-%M-%S-%f}.bmp', format='bmp', use_video_port=True)
#
#def list_diffs():
#	time_target = time.time() + 30.0
#	os.system('rm img*.bmp; rm out*.bmp')
#	
#	with picamera.PiCamera() as cam:
#		cam.resolution = (600, 600)
#		cam.framerate = 30
#		time.sleep(2)
#		
#		# with 
#		i = 0
#		while time.time() < time_target:
#			file1 = 'img1-%02d.bmp' % i
#			file2 = 'img2-%02d.bmp' % i
#			file3 = 'out-%02d.bmp' % i
#			t1 = time.time()
#			cam.capture_sequence( [file1, file2] )
#			t2 = time.time()
#			os.system('composite -compose difference '+file1+' '+file2+' '+file3)
#			t3 = time.time()
#			i = i + 1
#			time1 = (t2-t1, t3-t2)
#			print(time1)
#
#def analyze_images(strImg1, strImg2):
#	strCmd = 'composite -compose difference '+strImg1+' '+strImg2 + \
#		' - | convert - -colorspace Gray -auto-level ' + \
#		'-black-threshold 95%% -white-threshold 95%% out.bmp'
#	os.system( strCmd )

