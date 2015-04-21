'''
Original Author: "Xevel" alias Nicolas SAUGNIER

Description: Ground grid
'''

import visual

class grid:
    '''Ground grid of the whole scene''' 
    def __init__(self, size=100, small_interval=5, big_interval=50):
        self.frame = visual.frame(pos=(0,0,0))
        for i in range(-size, size+small_interval, small_interval):
            if i % big_interval == 0:
                c = visual.color.gray(0.65)
            else:
                c = visual.color.gray(0.25)
            visual.curve(frame=self.frame, pos=[(i,0,size),(i,0,-size)], color=c)
            visual.curve(frame=self.frame, pos=[(size,0,i),(-size,0,i)], color=c)