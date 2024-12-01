import matplotlib.path as mpath
import matplotlib.patches as mpatches
from pylab import *
import numpy as np


        
def graphBatt():
        
    Path = mpath.Path
    
    ax = plt.subplots()
    pp1 = mpatches.PathPatch(
        Path([(0, 0), (1, 0), (1, 1), (0, 0)],
             [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]),
        fc="none", transform=ax.transData)
    
    ax.add_patch(pp1)
    ax.plot([0.75], [0.25], "ro")
    ax.set_title('The red point should be on the path')
    
    plt.show()        
        
def graphBoost():
        
    Path = mpath.Path
    
    ax = plt.subplots()
    pp1 = mpatches.PathPatch(
        Path([(0, 0), (1, 0), (1, 1), (0, 0)],
             [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]),
        fc="none", transform=ax.transData)
    
    ax.add_patch(pp1)
    ax.plot([0.75], [0.25], "ro")
    ax.set_title('The red point should be on the path')
    
    plt.show()        
    
def graphAfr():
        
    Path = mpath.Path
    
    ax = plt.subplots()
    pp1 = mpatches.PathPatch(
        Path([(0, 0), (1, 0), (1, 1), (0, 0)],
             [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]),
        fc="none", transform=ax.transData)
    
    ax.add_patch(pp1)
    ax.plot([0.75], [0.25], "ro")
    ax.set_title('The red point should be on the path')
    
    plt.show()        
    
