'''
Author: Martin Stolle
Description: Main Simulation loop
'''
import visual

import vpyode

from WorldPhysics import myWorld
from Robot import Robot
from Controls import ControlWindow, tkWindow
import Constants as const
import Grid
import Environment as e
import random

class Simulation:
    
    def __init__(self):
        '''Uses VPython to visualize, manipulate and simulate the Quadruped live.'''
        self.bodies = []
        self.cWorld = myWorld()
        self.createUI(self.cWorld.world._getScene())
        
        # terrain for future implementation
        #self.myWorld = e.Heightmap(self.cWorld.world)
        #self.Terrain = self.myWorld.makeWorld()
        
        self.cRobot = Robot(self.cWorld.world, vpyode._bigSpace, 50)
        self.cCtrl = ControlWindow(self.cWorld.world._getScene(), self.cRobot, self.cWorld)
        
        self.cRobot.dropRobot()
        
        self.dt = 1.0/const.framerate
        self.refresh = 0
        
        self.bodies.append(e.drop_object(self.cWorld.world, self.cRobot.center))
    
    def startLoop(self):
        itemcount = 0
        count = random.uniform(1,50)
        random.seed()
        
        while(1):
            visual.rate(const.framerate) # Frame rate
            
            # check for events, drive actions; must be executed repeatedly in a loop
            self.cCtrl.ctrls.interact()
            
            # do multiple simulation steps per frame to prevent jittering due to
            # 'small' collisions
            n = 6
            
            if itemcount < count:
                itemcount += 1
                self.bodies.append(e.drop_object(self.cWorld.world, self.cRobot.center))
                    
            itemcount+=1
            
            if itemcount == 500:
                itemcount = 0
                for b in self.bodies:
                    for body in b.GetElementKeys():
                        b.RemoveElement(body)
                self.bodies = []
        
            for i in range(n):           
                # Simulation step
                self.cWorld.world.step(self.dt/n)
                
                # terrain for future implementation
                #self.Terrain.UpdateDisplay()
                
                if self.cRobot.bodyExists():
                    self.cRobot.refreshRobot(self.cCtrl.lBody)
                
                    if (self.cRobot.centerRobot):
                        self.cWorld.world._getScene().center = self.cRobot.center
                    
                    for leg in self.cRobot.tibia:
                        leg.UpdateDisplay()
                        
                    for leg in self.cRobot.femur:
                        leg.UpdateDisplay()
                        
                    for b in self.bodies:
                        b.UpdateDisplay()
                        
                        
    def setupWindow(self, scene):
        scene.title = 'Quadruped Simulation'
        scene.height = const.windowHeight
        scene.width = const.windowWidth
        scene.autoscale = 0
        scene.forward = (-5,-5,-5)
        scene.background = (0.0,0.0,0.0)
        
        self.createFloor()
        self.createArrows()
        
    def createFloor(self):
        Grid.grid(500)
    
    def createArrows(self):
        ''' Create arrow coordinates '''
        visual.arrow(pos=(0,0,0), axis=(1,0,0), radius=1, color=(0,0,1), length=3)
        visual.arrow(pos=(0,0,0), axis=(0,1,0), radius=1, color=(1,0,0), length=3)
        visual.arrow(pos=(0,0,0), axis=(0,0,1), radius=1, color=(0,1,0), length=3)
        
        visual.controls.label(pos = (3,0,0), text='x',box=False, opacity=0.0)
        visual.controls.label(pos = (0,3,0), text='y',box=False, opacity=0.0)
        visual.controls.label(pos = (0,0,3), text='z',box=False, opacity=0.0)
        
    def createUI(self, scene):
        '''Setup window and controls'''
        self.setupWindow(scene)
        
    def showLabel(self, val):
        if val:
            self.cRobot.showLabels = False
            self.cCtrl.lBody.visible = False
        else:
            self.cRobot.showLabels = True
            self.cCtrl.lBody.visible = True