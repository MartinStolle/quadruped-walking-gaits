'''
Author: Martin Stolle

Description: Adds an window with a graph in it
'''

import visual as v
import Constants as const

class Graph:
    
    def __init__(self):
        self.yMax = 100
        self.showGraph()
    
    
    def showGraph(self):
        self.posGraph = v.graph.gdisplay(x=0, y=const.windowHeight, width=const.windowWidth, height=200,
                          title='Position', xmax=100., xmin=-100., ymax=self.yMax, ymin=0.)
        self.x_pos = None
        self.y_pos = None
        
        
    def plotData(self, data):       
        self.clearCurveGraph(self.x_pos)
        self.clearCurveGraph(self.y_pos)

        self.x_pos = v.graph.gcurve(color=v.color.blue)
        self.x_pos.plot(pos=(100, data[-1][1]))
        self.x_pos.plot(pos=(-100, data[-1][1]))
        
        self.y_pos = v.graph.gcurve(color=v.color.red)
        self.y_pos.plot(pos=(data[-1][0], 100))
        self.y_pos.plot(pos=(data[-1][0], 0))
        
        if len(data) == const.maxSize:
            pass
        
    
    def updateGraph(self, data):
        self.plotData(data)
    
    
    def clearCurveGraph(self, g):
        if g:
            g.gcurve.visible = False
        del g
        