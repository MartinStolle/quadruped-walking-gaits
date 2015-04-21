'''
Author: Martin Stolle

Description: Builds and controls the Robot
'''

import ode
from visual import vector, pi, sphere, points
import vpyode
import numpy
from random import gauss, uniform
from math import *
import threading

import Constants as const
from Graph import Graph

class Robot:
    def __init__(self, world, space, density):
        self.world = world
        self.space = space
        self.density = density
        self.femurHeight = const.femurHeight
        self.femurWidth = const.femurWidth
        self.femurLength = const.femurLength
        self.tibiaHeight = const.tibiaHeight
        self.tibiaWidth = const.tibiaWidth
        self.tibiaLength = const.tibiaLength
        self.densityFemur = 10
        self.densityTibia = 10
        self.FMax = 10000
        self.totalMass = 0.0
        self.bodyExist = True
        self.showLabels = True
        self.center = (0,0,0)
        self.joints = []
        self.check = 0
        self.checkBack = 0
        self.centerRobot = True
        self.minDeg = const.minDeg
        self.maxDeg = const.maxDeg
        self.maxTibiaDeg = const.tibiaDeg
        self.time = 0.5
        # means how many percent of the body do have the density
        # like human body where only 90% is water
        self.bodyCoverage = 1.0
        self.graph = Graph()
        self.graphVal = []
            
            
    def setLegs(self):
        '''Adds some legs to our robot'''
        self.femur = [] # body
        self.tibia = [] # body
        
        for i in range(const.numLegs):
            tmpFemur = self.createBody(self.femurLength,
                                       self.femurHeight,
                                       self.femurWidth,
                                       self.densityFemur)
            self.femur.append(tmpFemur)
            
        for i in range(const.numLegs):
            tmpTibia = self.createBody(self.tibiaLength,
                                       self.tibiaHeight,
                                       self.tibiaWidth,
                                       self.densityTibia)
            self.tibia.append(tmpTibia)       
                                                    

    def createBody(self, lx, ly, lz, density):
        '''Creates the geom, body and visual box'''
        # Create body
        body = vpyode.GDMFrameBody(self.world)
        element = vpyode.GDMElement()
        element.DefineBox((density*self.bodyCoverage), lx, ly, lz)
        body.AddGDMElement('Box', element)
        
        self.totalMass += body.getMass().mass
        
        return body
    
    
    def dropRobot(self):
        '''Drops the whole body'''
        self.body = self.createBody(const.bodyLength,
                                    const.bodyHeight,
                                    const.bodyWidth,
                                    self.density)
        self.setLegs()
        
        self.dropLegs()
        self.dropBody()
        self.createJoints()
        
        
    def createJoints(self):
        '''Create the connections between the legs and body
           Note: Actually we do net set some of the legs to 90deg. The limitation
           of the angle stops before we can reach that angle. The reason for
           using that approach is that the force used for reaching that angle
           is much higher that way.'''
        self.joints = []
        for i in range(const.numLegs):
            fX = const.bodyLength/2
            fY = const.bodyHeight/2+const.Height
            fZ = const.bodyWidth/2
            
            tX = const.bodyLength/2
            tY = const.bodyHeight/2+const.Height
            tZ = const.bodyWidth/2+self.femurWidth/2#+const.tibiaWidth/2
            if i  == 0:
                self.addHingeJoint(self.femur[i], self.body,
                                             (fX, fY, fZ),
                                              (0, -1, 0), -0,
                                              self.minDeg, self.maxDeg)
                self.addHingeJoint(self.tibia[i], self.femur[i],
                                             (tX, tY, tZ),
                                             (1, 0, 0), const.maxAngle, -0.01,
                                             self.maxTibiaDeg)
            elif i == 1:
                self.addHingeJoint(self.femur[i], self.body,
                                             (-fX, fY, fZ),
                                              (0, -1, 0), 0,
                                              self.maxDeg, self.minDeg)
                self.addHingeJoint(self.tibia[i], self.femur[i],
                                             (-tX, tY, tZ),
                                             (1, 0, 0), const.maxAngle, -0.01,
                                             self.maxTibiaDeg)
            elif i == 2:
                self.addHingeJoint(self.femur[i], self.body,
                                             (-fX, fY, -fZ),
                                             (0, -1, 0), -const.maxAngle,
                                             self.minDeg, self.maxDeg)
                self.addHingeJoint(self.tibia[i], self.femur[i],
                                             (-tX, tY, -tZ),
                                             (-1, 0, 0), const.maxAngle, -0.01,
                                             self.maxTibiaDeg)
            elif i == 3:
                self.addHingeJoint(self.femur[i], self.body,
                                             (fX, fY, -fZ),
                                             (0, -1, 0), const.maxAngle,
                                             self.maxDeg, self.minDeg)
                self.addHingeJoint(self.tibia[i], self.femur[i],
                                             (tX, tY, -tZ),
                                             (-1, 0, 0), const.maxAngle, -0.01,
                                             self.maxTibiaDeg)
        
        
    def addFixedJoint(self, body1, body2):
        ''' '''
        joint = ode.FixedJoint(self.world)
        joint.attach(body1, body2)
        joint.setFixed()
        
        return joint


    def addHingeJoint(self, body1, body2, anchor, axis, degree=0, loStop = 0.2, hiStop=0.2):
        ''' '''
        joint = ode.HingeJoint(self.world)
        joint.attach(body1, body2)
        joint.setAnchor(anchor)        
        joint.setAxis(axis)

        joint.setParam(ode.ParamLoStop, -pi * hiStop) # must be smaller than -pi
        joint.setParam(ode.ParamHiStop, pi * loStop) # must be smaller than pi
        
        joint.setParam(ode.ParamFMax, self.FMax)
        joint.setParam(ode.ParamVel, self.DegreeToRadian(degree))
        joint.addTorque(self.FMax)
        
        self.joints.append([joint, self.visualizeHinge(anchor)])
      
        
    def setAngle(self, val, jNr):
        '''sets the angle of a specific joint'''
        val -= 180
        self.joints[jNr][0].setParam(ode.ParamVel, self.DegreeToRadian(val))
    
    
    def visualizeHinge(self, anchor):
        '''shows a point where the anchor point of the joint is'''
        #points(pos=[anchor], size=5, color=(1,0,0))
        return sphere(pos=anchor, radius=0.3, color=(0,0,1))
        
        
    def removeJointVisuals(self):
        for joint in self.joints:
            joint[1].visible = False
            del joint[1]
       
    
    def refreshJoints(self):
        for joint in self.joints:
            joint[1].pos = joint[0].getAnchor2()
            
    
    def dropLegs(self):
        '''Drops the legs of the robot'''
        fX = const.bodyLength/2
        fY = const.bodyHeight/2+const.Height
        fZ = const.bodyWidth/2+self.femurWidth/2
        
        i=0
        for leg in self.femur:
            if i == 0:
                leg.setPosition((fX, fY, fZ))
            elif i == 1:
                 leg.setPosition((-fX, fY, fZ))
            elif i == 2:
                leg.setPosition((-fX, fY, -fZ))
            elif i == 3:
                leg.setPosition((fX, fY, -fZ))
            i+=1
            
        i=0
        fX = const.bodyLength/2
        fY = const.bodyHeight/2-self.femurHeight/2-self.tibiaHeight/2+const.Height
        fZ = const.bodyWidth/2+self.femurWidth+self.tibiaWidth/2
        for leg in self.tibia:
            if i == 0:
                leg.setPosition((fX, fY, fZ))
            elif i == 1:
                 leg.setPosition((-fX, fY, fZ))
            elif i == 2:
                leg.setPosition((-fX, fY, -fZ))
            elif i == 3:
                leg.setPosition((fX, fY, -fZ))
            i+=1
            
        
    def dropBody(self):
        '''drops the main body of the robot'''
        self.body.setPosition( (0, const.bodyHeight/2+const.Height, 0) )
        
        
    def refreshRobot(self, lBody, lFemur=None, lTibia=None):
        '''Refreshes the position of the labels and camera'''
        self.refreshBody(lBody)
        #self.refreshLegs(lTibia, lFemur)
        self.refreshJoints()

    
    def refreshBody(self, lBody):
        '''Refreshes the label position and the camera of the center body'''
        self.body.UpdateDisplay()
        x,y,z = self.body.getPosition()
        self.center = (x,y,z)
        self.refreshGraph((x,y))
        if self.showLabels:
            lBody.pos = (x,y,z)
            lBody.text = '%.2f, %.2f, %.2f, %.1f kg' % (x,y,z,self.totalMass)
            
    
    def refreshGraph(self, val):
        if len(self.graphVal) > const.maxSize:
            self.graphVal = []
        else:
            self.graphVal.append(val)
            self.graph.plotData(self.graphVal)
        
    
    def refreshLegs(self, lTibia, lFemur):
        '''Refreshes the position of the labels'''
        for i in range(len(self.femur)):
            x,y,z = self.femur[i].getPosition()
            lFemur.pos = (x,y,z)
           
        for i in range(len(self.tibia)):
            x,y,z = self.tibia[i].getPosition()
            lTibia.pos = (x,y,z)
            
        
    def scalp (self, vec, scal):
        '''geometric utility functions - from ODE example'''
        vec[0] *= scal
        vec[1] *= scal
        vec[2] *= scal
    
    
    def length (self, vec):
        '''geometric utility functions - from ODE example'''
        return sqrt (vec[0]**2 + vec[1]**2 + vec[2]**2)
        
  
    def DegreeToRadian(self, deg):
        '''geometric utility functions - from ODE example  '''
        return float(deg)/180.0 * pi
        
        
    def RadianToDegree(self, rad):
        '''geometric utility functions - from ODE example  '''
        return rad/pi * 180
        
        
    def pushRobot(self):
        '''Applies a force to the robot - from ODE Example'''
        l = self.body.getPosition ()
        d = self.length (l)
        a = max(0, 800000*(1.0-0.2*d*d))
        l = [l[1] / 4, l[1], l[2] /4]
        self.scalp (l, a / self.length (l))
        for leg in self.femur:
            leg.addForce(l)
        for leg in self.tibia:
            leg.addForce(l)
        self.body.addRelForce(l)
        print 'Applied Force: ', l
 
        
    def setDensity(self, val):
        '''Sets the density of the robot, considering the percentage it is
           covered with the material''' 
        self.density = (float(val)*self.bodyCoverage)
        
    
    def setFemurDensity(self, val):
        '''Sets the density of the femur, considering the percentage it is
           covered with the material''' 
        self.densityFemur = (float(val)*self.bodyCoverage)
        
        
    def setTibiaDensity(self, val):
        '''Sets the density of the tibia, considering the percentage it is
           covered with the material''' 
        self.densityTibia = (float(val)*self.bodyCoverage)
        
    
    def setFemurLength(self, val):
        self.femurHeight = float(val)


    def setFemurHeight(self, val):
        self.femurHeight = float(val)
    
    
    def setFemurWidth(self, val):
        self.femurWidth = float(val)
        
 
    def setTibiaLength(self, val):
        self.tibiaLength = float(val)


    def setTibiaHeight(self, val):
        self.tibiaHeight = float(val)
    
    
    def setTibiaWidth(self, val):
        self.tibiaWidth = float(val)
    
    
    def setMinDeg(self, val):
        self.minDeg = float(val)
    
    
    def setMaxDeg(self, val):
        self.maxDeg = float(val)
        
        
    def setTibiaMaxDeg(self, val):
        self.maxTibiaDeg = float(val)
        
        
    def setBodyCoverage(self, val):
        '''Percentage of the body using the material'''
        self.bodyCoverage = float(val)
        print 'Bodyshare = %2.1f percent' % (float(val)*100)
        
        
    def setFMax(self, val):
        '''The maximum force or torque that the motor will use to achieve the
            desired velocity. Must be greater than zero. 0 = motor off'''
        for joint in self.joints:
            joint[0].setParam(ode.ParamFMax, float(val))
            
        self.FMax = float(val)
        print 'Torque = %1.2f' % (float(val))
        
    def bodyExists(self):
        '''Returns the boolean if the robot body exists'''
        return self.bodyExist
    
         
    def dropAgain(self):
        '''Removes the old body and readds it to its initial position'''
        self.bodyExist = False
        self.check = 0
        self.totalMass = 0.0

        for b in self.body.GetElementKeys():
            self.body.RemoveElement(b)

        for leg in self.femur:
            for b in leg.GetElementKeys():
                leg.RemoveElement(b)
  
        for leg in self.tibia:
            for b in leg.GetElementKeys():
                leg.RemoveElement(b)
       
        self.removeJointVisuals()
        self.dropRobot()
        
        print 'total mass is %.1f kg' % (self.totalMass)
        self.bodyExist = True
        
    
    def moveForward(self):
        if self.check == 0:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(90, 3)
            self.setAngle(270, 2)
        elif self.check == 1:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(270, 3)
            self.setAngle(90, 0)
        elif self.check == 2:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(90, 7)
            self.setAngle(90, 6)
        elif self.check == 3:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(270, 7)
            self.setAngle(270, 4)
        elif self.check == 4:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(90, 5)
            self.setAngle(90, 4)
        elif self.check == 5:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(270, 5)
            self.setAngle(270, 6)
        elif self.check == 6:
            t = threading.Timer(self.time, self.moveForward)
            t.start()
            self.check += 1
            self.setAngle(90, 1)
            self.setAngle(270, 0)
        elif self.check == 7:
            self.check = 0
            self.setAngle(270, 1)
            self.setAngle(90, 2)

    
    def moveBackward(self):
        if self.check == 0:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(90, 1)
            self.setAngle(90, 0)
        elif self.check == 1:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(270, 1)
            self.setAngle(270, 2)
        elif self.check == 2:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(90, 5)
            self.setAngle(270, 4)
        elif self.check == 3:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(270, 5)
            self.setAngle(90, 6)
        elif self.check == 4:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(90, 7)
            self.setAngle(270, 6)
        elif self.check == 5:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(270, 7)
            self.setAngle(90, 4)
        elif self.check == 6:
            t = threading.Timer(self.time, self.moveBackward)
            t.start()
            self.check += 1
            self.setAngle(90, 3)
            self.setAngle(90, 2)
        elif self.check == 7:
            self.check = 0
            self.setAngle(270, 3)
            self.setAngle(270, 0)
            

    def turnLeft(self):
        if self.check == 0:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(90, 3)
            self.setAngle(270, 2)
        elif self.check == 1:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(270, 3)
            self.setAngle(90, 0)
        elif self.check == 2:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(90, 5)
            self.setAngle(270, 4)
        elif self.check == 3:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(270, 5)
            self.setAngle(90, 6)
        elif self.check == 4:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(90, 7)
            self.setAngle(270, 6)
        elif self.check == 5:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(270, 7)
            self.setAngle(90, 4)
        elif self.check == 6:
            t = threading.Timer(self.time, self.turnLeft)
            t.start()
            self.check += 1
            self.setAngle(90, 1)
            self.setAngle(270, 0)
        elif self.check == 7:
            self.check = 0
            self.setAngle(270, 1)
            self.setAngle(90, 2)
            
            
    def turnRight(self):
        if self.check == 0:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(90, 1)
            self.setAngle(90, 0)
        elif self.check == 1:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(270, 1)
            self.setAngle(270, 2)
        elif self.check == 2:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(90, 7)
            self.setAngle(90, 6)
        elif self.check == 3:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(270, 7)
            self.setAngle(270, 4)
        elif self.check == 4:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(90, 5)
            self.setAngle(90, 4)
        elif self.check == 5:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(270, 5)
            self.setAngle(270, 6)
        elif self.check == 6:
            t = threading.Timer(self.time, self.turnRight)
            t.start()
            self.check += 1
            self.setAngle(90, 3)
            self.setAngle(90, 2)
        elif self.check == 7:
            self.check = 0
            self.setAngle(270, 3)
            self.setAngle(270, 0)