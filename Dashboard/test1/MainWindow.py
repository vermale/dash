from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

from pylab import plot, xlabel, ylabel, title, grid, show
from ui_mainwindow import Ui_MainWindow
import sys, os, glob
import pickle
from TablePrototype import TableWindow, TableModel
from TablePrototype import ModelVE, ModelSA
from Dial import Dial
import serial
import random
import can
from warnings import catch_warnings
import CanProtocol
import graph
import matplotlib.path as mpath
import matplotlib.patches as mpatches

import numpy

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
    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked
   
   
class MainWindow(QMainWindow):
    
    
    TempList = []
    
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionVolumetric_Efficiency.triggered.connect(self.openVE)
        self.ui.actionSpark_Advance.triggered.connect(self.openSA)

        self.currentport = ""
        
        layout = QGridLayout(self.ui.centralwidget)
        layout.setContentsMargins(1,1,1,1)
        layout.setColumnMinimumWidth(1,1)
        
        self.ui.centralwidget.setLayout(layout)
                          
        self.temp_value = 0
        self.batt_value = 0
        self.boost_value = 0
        self.afr_value = 0
        self.message =""
        self.meters = []
        
        graphBatt = graph.graphBatt
        graphAfr = graph.graphAfr
        graphBoost = graph.graphBoost     
        
        
        temp = Dial("TEMP", "", 0, 120, 0.98, 0.20, 0,1)
        clickable(temp).connect(self.graphTemp)
        self.meters.append(temp)
        layout.addWidget(temp, 0, 0)
        
        batt = Dial("BATT", "", 0, 15, 0.98, 0.20, 0,1)
        clickable(batt).connect(graphBatt)
        self.meters.append(batt)
        layout.addWidget(batt, 0, 1)

        boost = Dial("MAP", "", 0, 30, 0.98, 0.20, 0,1)
        clickable(boost).connect(graphBoost)
        self.meters.append(boost)
        layout.addWidget(boost, 1, 0)
        
        afr = Dial("AFR", "", 0, 20, 0.98, 0.20, 0,1)
        clickable(afr).connect(graphAfr)
        self.meters.append(afr)
        layout.addWidget(afr, 1, 1)
        
             
        

        try:
            self.bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=500000)
        except: 
            print("Erreur lors de la conversion de l'année.")

        QTimer.singleShot(1, self.increment)
       
       
    def graphTemp(self):
        
        t = numpy.arange(0.0, len(self.TempList), 1)
        s = self.TempList
        plot(t, s)
         
        xlabel('time (s)')
        ylabel('Temperature')
        title('Water C°')
        grid(True)
        show()
        
     
            
        

    def increment(self):
        
        self.temp_value = (self.temp_value + random.randint(0,1)) % 120
        temp = self.meters[0]
        temp.setSpeed(self.temp_value)
        self.TempList.append(self.temp_value)
        
        self.batt_value = (self.batt_value + random.randint(0,1)/10) % 15
        batt = self.meters[1]
        batt.setSpeed(self.batt_value)
        
        self.boost_value = (self.boost_value + random.randint(0,1)/10) % 30
        boost = self.meters[2]
        boost.setSpeed(self.boost_value)
        
        self.afr_value = (self.afr_value + random.randint(0,1)/10) % 20
        afr = self.meters[3]
        afr.setSpeed(self.afr_value)
        
        try:
            self.message = self.bus.recv()
        except:
            print("No message")
        print(self.message)
         
        QTimer.singleShot(10, self.increment) 

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