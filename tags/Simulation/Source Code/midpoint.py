# code adapted from http://bocoup.com/processing-js/docs/index.php?page=Plasma%20Fractals
# original from http://www.ic.sunysb.edu/Stu/jseyster/plasma/ (Justin Seyster)
import random
import visual
from operator import itemgetter
import uuid

def plasma(x, y, width, height, c1, c2, c3, c4):
    newWidth = width / 2
    newHeight = height / 2

    if (width > gridSize or height > gridSize):
        #Randomly displace the midpoint!
        midPoint = (c1 + c2 + c3 + c4) / 4 + Displace(newWidth + newHeight)

        #Calculate the edges by averaging the two corners of each edge.
        edge1 = (c1 + c2) / 2
        edge2 = (c2 + c3) / 2
        edge3 = (c3 + c4) / 2
        edge4 = (c4 + c1) / 2

        x1 = x + newWidth
        y1 = y + newHeight
        
        #Do the operation over again for each of the four new grids.
        plasma(x,            y,             newWidth,   newHeight, c1,        edge1,    midPoint, edge4)
        plasma(x + newWidth, y,             newWidth,   newHeight, edge1,     c2,       edge2,    midPoint)
        plasma(x + newWidth, y + newHeight, newWidth,   newHeight, midPoint,  edge2,    c3,       edge3)
        plasma(x,            y + newHeight, newWidth,   newHeight, edge4,     midPoint, edge3,    c4)     
    else:
        #This is the "base case," where each grid piece is less than the size of a pixel.    
        c = (c1 + c2 + c3 + c4) / 4;

        hw = (w/2)
        hh = (h/2)
        ch = c/2
        cc = c/maxHeight

        if (c > 0.5) and (c < 1.0):
            c = 0
        
	p.append([x-hw,c,y-hh])
            
def Displace(num):
    rand = (random.uniform(1, maxHeight) - noise)
    return rand


global gridSize, gamma, points, p, maxHeight, points, w, h, f
random.seed(str(uuid.uuid1()))
f = visual.frame()
p = []
width, w = 64, 64
noise = random.uniform(1,5) # less noise = higher map
height, h = 64, 64
gridSize = 1 # size between pixels
maxHeight = random.uniform(1,5)


plasma(0,0, width, height, random.uniform(1, maxHeight), random.uniform(1, maxHeight), random.uniform(1, maxHeight), random.uniform(1, maxHeight))

p = sorted(p, key=itemgetter(0,2))
print len(p)

Res = w-1

modCheck = 0
nCheck = 0
for n in range(1, len(p)-w):
    if(n%Res != modCheck or n == nCheck):
	f1 = visual.faces(frame=f, pos=[
                           p[n],
                           p[n+1],
			   p[(n+1)+Res]] )
	f2 = visual.faces(frame=f, pos=[
                           p[n+1],
                           p[(n+2)+Res],
			   p[(n+1)+Res]] )
    
	f1.make_normals()
	f1.smooth()
	f1.make_twosided()
	f2.make_normals()
	f2.smooth()
	f2.make_twosided()
	
    else:
	modCheck += 1
	nCheck += w
