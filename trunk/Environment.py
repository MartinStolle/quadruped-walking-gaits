import visual
import ode
import random
from math import pi
import vpyode
import uuid
from operator import itemgetter

   

def create_box(world, density, lx, ly, lz):
    """Create a box body and its corresponding geom."""
    
    # Create body
    body = vpyode.GDMFrameBody(world)
    element = vpyode.GDMElement()
    element.DefineBox(density, lx, ly, lz)
    element.GetDisplayObject().color = (random.uniform(0,1),random.uniform(0,1), random.uniform(0,1))
    body.AddGDMElement('Box', element)
    
    return body

def create_cylinder(world, density, radius, length):
    '''Create a cylinder body and its corresponding geom.'''
    body = vpyode.GDMFrameBody(world)
    element = vpyode.GDMElement()
    element.DefineCylinder(density, radius, length)
    element.GetDisplayObject().color = (random.uniform(0,1),random.uniform(0,1), random.uniform(0,1))
    body.AddGDMElement('Cylinder', element)
    
    return body
    
def drop_object(world, pos):
    """Drop an object into the scene."""
    random.seed(str(uuid.uuid1()))
    
    body = create_box(world, random.uniform(10,100), random.uniform(0.5,6),random.uniform(0.1,0.6),random.uniform(0.5,6))
    x = pos[0] + random.uniform(-pos[0]-12,pos[0]+12)
    y = random.uniform(6,20)
    z = pos[2] + random.uniform(-pos[2]-12,pos[2]+12)
    body.setPosition( (x, y, z) )
        
    # Rotate by a random angle about all three axes
    theta = random.uniform(0,2*pi)
    body.RotateOrientation(theta, (1,0,0))
    theta = random.uniform(0,2*pi)
    body.RotateOrientation(theta, (0,1,0))
    theta = random.uniform(0,2*pi)
    body.RotateOrientation(theta, (0,0,1))
        
    return body


class Heightmap:
    
    def __init__(self, world):
        self.world = world
        random.seed(str(uuid.uuid1())) # initialize random module
        width, self.w = 32, 32
        height, self.h = 32, 32
        self.gridSize = 1 # size between pixels
        self.maxHeight = random.uniform(0,2)
        self.noise = random.uniform(0,2) # less noise = higher map
        self.vertices = []
        self.indices = []
        self.faces = []

        self.plasma(0,0, width, height, random.uniform(1, self.maxHeight),
               random.uniform(1, self.maxHeight), random.uniform(1, self.maxHeight),
               random.uniform(1, self.maxHeight))
        self.MakeFaces()
        
        
    def makeMesh(self):           
        mesh = vpyode.Mesh()
        mesh.build(self.vertices, self.indices, self.faces)

        return mesh

        
    def makeWorld(self):
        body = vpyode.GDMFrameBody(self.world)
        element = vpyode.GDMElement()
        mesh = self.makeMesh()
        element.DefineMeshTotal(100.0, (0,0,0), self.faces[0], mesh)
        body.AddGDMElement('Mesh', element)
        
        return body    


    def plasma(self, x, y, width, height, c1, c2, c3, c4):
        newWidth = width / 2
        newHeight = height / 2
    
        if (width > self.gridSize or height > self.gridSize):
            #Randomly displace the midpoint!
            midPoint = (c1 + c2 + c3 + c4) / 4 + self.Displace(newWidth + newHeight)
    
            #Calculate the edges by averaging the two corners of each edge.
            edge1 = (c1 + c2) / 2
            edge2 = (c2 + c3) / 2
            edge3 = (c3 + c4) / 2
            edge4 = (c4 + c1) / 2
    
            x1 = x + newWidth
            y1 = y + newHeight
            
            #Do the operation over again for each of the four new grids.
            self.plasma(x,            y,             newWidth,   newHeight, c1,        edge1,    midPoint, edge4)
            self.plasma(x + newWidth, y,             newWidth,   newHeight, edge1,     c2,       edge2,    midPoint)
            self.plasma(x + newWidth, y + newHeight, newWidth,   newHeight, midPoint,  edge2,    c3,       edge3)
            self.plasma(x,            y + newHeight, newWidth,   newHeight, edge4,     midPoint, edge3,    c4)     
        else:
            #This is the "base case," where each grid piece is less than the size of a pixel.    
            c = (c1 + c2 + c3 + c4) / 4;
    
            hw = (self.w/2)
            hh = (self.h/2)
            ch = c/2
            cc = c/self.maxHeight

            if (c > 0.5) and (c < 1.0):
                c = 0

            self.vertices.append([(x-hw),c,(y-hh)]) #center points
            #self.vertices.append([(x),(c),(y)])
    
                
    def Displace(self, num):
        rand = (random.uniform(1, self.maxHeight) - self.noise)
        return rand
    
    
    def MakeFaces(self):
        Res = self.w-1
        self.vertices = sorted(self.vertices, key=itemgetter(0,2))
        
        modCheck, nCheck = 0, 0
        for n in range(1, len(self.vertices)-self.w):
            if(n%Res != modCheck or n == nCheck):
                self.faces.append([self.vertices[n], self.vertices[n+1], self.vertices[(n+1)+Res]])
                self.faces.append([self.vertices[n+1], self.vertices[(n+2)+Res], self.vertices[(n+1)+Res]])
                self.indices.append([n, n+1, (n+1)+Res])
                self.indices.append([n+1, (n+2)+Res, (n+1)+Res])
            else:
                modCheck += 1
                nCheck += self.w
