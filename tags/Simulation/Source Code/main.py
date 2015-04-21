'''
Author: Martin Stolle
Description: Simulation of Quadruped Robot using ODE and VPython

PyOde: http://pyode.sourceforge.net
VPython: http://www.vpython.org
NOTE: Changed some things, therefore the version is not compatible anymore
VPyOde: http://www.missioncognition.net/visualpyode/

CGKit(Rendering): http://cgkit.sourceforge.net/
Pixie: http://www.renderpixie.com/

Definition Quadruped:
1. noun: an animal especially a mammal having four limbs specialized for walking
2. adjective: having four feet
'''

# Standard Python Library
import sys
# VPython
import visual.graph
# Merged Lib between pyODE and VPython
import vpyode
# GUI
import Tkinter
import thread

from Controls import ControlWindow, tkWindow
from Simu import Simulation


def GUImode():
	root = Tkinter.Tk()
	root.geometry('200x730+1050+0')
	sim = Simulation()
	thread.start_new_thread(sim.startLoop,())
	app = tkWindow(root, sim)
	root.mainloop()
 
def usage():
    '''Prints the usage of this program.'''
    print 'Right-Click Rotate, Mid-Click Move'
    
def usageRender():
    '''Prints rendering how-to.'''
    print 'usageRender'

def main(argv):
    if '--help' in argv:
        usage()
        usageRender()
    elif '--render' in argv:
        if len(argv) < 2:
            usageRender()
        else:
            renderMode(argv[-1])
    else:
        GUImode()
        
if __name__ == "__main__":
    main(sys.argv[1:])