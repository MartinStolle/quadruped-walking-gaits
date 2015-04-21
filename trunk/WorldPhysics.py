'''
Author: Martin Stolle

Description: The physics enviroment of the simulation.
'''

import ode
import vpyode

class myWorld:
    '''' Contains the world(gravity etc.) and Space(Collision)'''    
    def __init__(self):
        self.world = vpyode.World()
        self.world.setGravity( (0,-9.81,0) ) # Gravity of Earth
        self.world.setERP(0.2)
        self.world.setCFM(1E-5)
        self.world.setContactSurfaceLayer(1E-3)
        self.world.setContactMaxCorrectingVel(0.1)
        
        # Create a plane geom which prevent the objects from falling forever
        self.floor = ode.GeomPlane(vpyode._bigSpace, (0,1,0), 0)
        vpyode._Mu = 5000
        
        
    def setGravity(self, val):
        self.world.setGravity( (0,val,0) )
        print 'Gravity: %.1f m/s^2' % (-val)
        
    
    def setFloorGrip(self, val):
        ''''Floorgrip (0-5 = very slippery, 50-500 = normal, 5000 = very sticky)'''
        vpyode._Mu = float(val)
        print 'Groundvalue = ', val
        
    
    def returnMu(self):
        return vpyode._Mu