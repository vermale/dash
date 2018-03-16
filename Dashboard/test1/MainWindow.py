#from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow, QGridLayout
#from PyQt5.QtCore import *
from PyQt5.QtCore import QObject, pyqtSignal, QEvent, QTimer
#from PyQt5 import *


from pylab import close, figure, get_current_fig_manager, plot, xlabel, ylabel, title, grid, connect, show, ioff
from ui_mainwindow import Ui_MainWindow
import sys, os, glob
#import pickle
#from TablePrototype import TableWindow, TableModel
#from TablePrototype import ModelVE, ModelSA
from Dial import Dial
import serial
#import random
#import can
#from warnings import catch_warnings
import CanProtocol

#mport matplotlib.path as mpath

import numpy

from matplotlib import pyplot
#mport matplotlib.pyplot as plt


def clickable(widget):
      
    class Filter(QObject):
        
        clicked = pyqtSignal()
           
        def eventFilter(self, obj, event):
           
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        # The developer can opt for .emit(obj) to get the object within the slot.
                        return True
            return False
    tfilter = Filter(widget)
    widget.installEventFilter(tfilter)
    return tfilter.clicked
   
   
class MainWindow(QMainWindow):
    
    nb= 0
    TempList = []
    AfrList = []
    BoostList = []
    BattList = []
    TempWin = pyplot
    tool = CanProtocol.CanTool()
    
    
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.currentport = ""
        
        layout = QGridLayout(self.ui.centralwidget)
        layout.setContentsMargins(1,1,1,1)
        layout.setColumnMinimumWidth(1,1)
        
        self.move(0,0)
        
        self.ui.centralwidget.setLayout(layout)
                          
        self.temp_value = 0
        self.batt_value = 0
        self.boost_value = 0
        self.afr_value = 0
        self.message =""
        self.meters = []
        self.line = ''
        self.file = ''
        
        
        
        temp = Dial("TEMP", "", 0, 120, 0.98, 0.20, 0,1)
        clickable(temp).connect(self.graphTemp)
        self.meters.append(temp)
        layout.addWidget(temp, 0, 0)
        
        batt = Dial("BATT", "", 0, 15, 0.98, 0.20, 0,1)
        clickable(batt).connect(self.graphBatt)
        self.meters.append(batt)
        layout.addWidget(batt, 0, 1)

        boost = Dial("MAP", "", 0, 2, 0.98, 0.20, 0,1)
        clickable(boost).connect(self.graphBoost)
        self.meters.append(boost)
        layout.addWidget(boost, 1, 0)
        
        afr = Dial("AFR", "", 0, 20, 0.98, 0.20, 0,1)
        clickable(afr).connect(self.graphAfr)
        self.meters.append(afr)
        layout.addWidget(afr, 1, 1)   
        
        self.BoostList.append(0)
        self.BoostList.append(2)
        self.AfrList.append(0)
        self.AfrList.append(20)
        self.TempList.append(-10)
        self.TempList.append(130)
        self.BattList.append(0)
        self.BattList.append(18)

        #try:
        #    self.bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=500000)
        #except: 
        #    print("Erreur lors de la conversion de l'année.")

        QTimer.singleShot(10, self.increment)
       
    
    def on_click(self,event):
        # get the x and y coords, flip y from top to bottom
        if event.button == 1:
            ioff()
            close()
           
       
    def graphTemp(self):
        
        t = numpy.arange(0.0, len(self.TempList), 1) 
        s = self.TempList
        
        figure(num="TEMPERATURE",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        thismanager.window.wm_geometry("+0+0")                            
        plot(t, s, color="red", linewidth=1, linestyle="-")
         
        xlabel('time (s)')
        ylabel('Temperature')
        title('Water C°')
        grid(True)
        connect('button_press_event', self.on_click)
        show()
        
                
    def graphBatt(self):
        
        t = numpy.arange(0.0, len(self.BattList), 1) 
        s = self.BattList
        figure(num="VOLTAGE",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
         
        xlabel('events')
        ylabel('Volt')
        title('Voltage V')
        grid(True)
        connect('button_press_event', self.on_click)
        show()
        
    def graphBoost(self):
        
        t = numpy.arange(0.0, len(self.BoostList), 1) 
        s = self.BoostList
        figure(num="BOOST",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('Boost')
        title('Boost mbar')
        grid(True)
        connect('button_press_event', self.on_click)
        show()
        
    def graphAfr(self):
        
        t = numpy.arange(0.0, len(self.AfrList), 1) 
        s = self.AfrList
        figure(num="AFR",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('AFR')
        title('Afr')
        grid(True)
        connect('button_press_event', self.on_click)
        show()    
            
        

    def increment(self):
        
        self.fileRead()
        line = self.line
        
        self.tool.decode( self.line)
        
        batt = self.meters[1]
        batt.setSpeed(self.tool.Volt)
        self.BattList.append(self.tool.Volt)
        
        temp = self.meters[0]
        temp.setSpeed(self.tool.Temp)
        self.TempList.append(self.tool.Temp)
        
        afr = self.meters[3]
        afr.setSpeed(self.tool.Lambda1)
        self.AfrList.append(self.tool.Lambda1)
        
        boost = self.meters[2]
        boost.setSpeed(self.tool.Map)
        self.BoostList.append(self.tool.Map)
        
        
        
        try:
            self.message = self.bus.recv()
        except:
            a =0
             
        QTimer.singleShot(20, self.increment)
        
        
    def fileRead(self):        
        
        try: 
            self.line = self.file.readline()
            if ( self.line == "" ):
                self.file.close() 
                self.file = open('candata.txt','r')   
                self.line = self.file.readline()
    
            
        except:
            #self.file.close() 
            self.file = open('candata.txt','r')   
            self.line = self.file.readline()
            
            
                

    def openVE(self):
        self.vewindow.show()

    def openSA(self):
        self.sawindow.show()

    def closeEvent(self, evt):
        evt.accept()
 
    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        
        for port in ports:
            try:
                serial.Serial.setPort(self, port)

                serial.Serial.close(self)
                result.append(port)
                print("found %s" % port)
            except (OSError, serial.SerialException):
                pass
        return result