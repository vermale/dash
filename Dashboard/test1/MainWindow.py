from PyQt5.QtWidgets import QMainWindow, QGridLayout
from PyQt5.QtCore import QObject, pyqtSignal, QEvent, QTimer


from pylab import close, figure, get_current_fig_manager, plot, xlabel, ylabel, title, grid, connect, show, ioff
from ui_mainwindow import Ui_MainWindow
import sys, os, glob
from Dial import Dial
import serial
import CanProtocol

import numpy
import can

from matplotlib import pyplot


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
    AirList = []
    FuelList = []
    TempWin = pyplot
    tool = CanProtocol.CanTool()
    oldMess = ""
    
    
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
        
        
        
        temp = Dial("TEMP", "C", 0, 120, 0.98, 0.20, 0,1)
        clickable(temp).connect(self.graphTemp)
        self.meters.append(temp)
        layout.addWidget(temp, 0, 0)
        layout.setSpacing(0)
        
        layout.setContentsMargins(0,0,0,0)
        
        #self.showFullScreen()

        batt = Dial("BATT", "volt", 0, 15, 0.98, 0.20, 0,1)
        clickable(batt).connect(self.graphBatt)
        self.meters.append(batt)
        layout.addWidget(batt, 0, 1)

        boost = Dial("BOOST", "bar", 0, 3, 0.98, 0.20, 0,1)
        clickable(boost).connect(self.graphBoost)
        self.meters.append(boost)
        layout.addWidget(boost, 1, 0)
        
        afr = Dial("AFR", "", 0, 20, 0.98, 0.20, 0,1)
        clickable(afr).connect(self.graphAfr)
        self.meters.append(afr)
        layout.addWidget(afr, 1, 1)   

        air = Dial("AIR", "", -10, 150, 0.98, 0.2, 0, 1 )
        clickable(air).connect(self.graphAir)
        self.meters.append(air)
        layout.addWidget(air, 0, 2 )
        
        fuel = Dial("FUEL", "", 0, 150, 0.98, 0.2, 0, 1 )
        clickable(fuel).connect(self.graphFuel)
        self.meters.append(fuel)
        layout.addWidget(fuel, 1, 2 )
        
        self.BoostList.append(0)
        self.BoostList.append(2)
        self.AfrList.append(0)
        self.AfrList.append(20)
        self.TempList.append(-10)
        self.TempList.append(130)
        self.BattList.append(0)
        self.BattList.append(18)
        self.FuelList.append(0)
        self.FuelList.append(150)
        self.AirList.append(0)
        self.AirList.append(150)


        QTimer.singleShot(1000, self.increment)

        filter = [{'can_id':0x300, 'can_mask': 0x00f }]

        self.bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
       
    
    def on_click(self,event):
        # get the x and y coords, flip y from top to bottom
        if event.button == 1:
            ioff()
            close()
           
       
    def graphTemp(self):
        
        t = numpy.arange(0.0, len(self.TempList), 1) 
        s = self.TempList
        
        figure(num="TEMPERATURE",figsize=(12,10))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")                            
        plot(t, s, color="red", linewidth=1, linestyle="-")
         
        xlabel('time (s)')
        ylabel('Temperature')
        title('Water C')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()
        
                
    def graphBatt(self):
        
        t = numpy.arange(0.0, len(self.BattList), 1) 
        s = self.BattList
        figure(num="VOLTAGE",figsize=(12,10))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
         
        xlabel('events')
        ylabel('Volt')
        title('Voltage V')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()
        
    def graphBoost(self):
        
        t = numpy.arange(0.0, len(self.BoostList), 1) 
        s = self.BoostList
        figure(num="BOOST",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('Boost')
        title('Boost mbar')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()
        
    def graphAfr(self):
        
        t = numpy.arange(0.0, len(self.AfrList), 1) 
        s = self.AfrList
        figure(num="AFR",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('AFR')
        title('Afr')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()    
            
        
    def graphAir(self):
        
        t = numpy.arange(0.0, len(self.AirList), 1) 
        s = self.AirList
        figure(num="AIR",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('AIR')
        title('Air')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()    


    def graphFuel(self):
        
        t = numpy.arange(0.0, len(self.fuelList), 1) 
        s = self.fuelList
        figure(num="FUEL",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('FUEL')
        title('Fuel')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()    



    def increment(self):
        
        self.line = self.can_read(0x308)
        self.tool.decode( self.message )
        batt = self.meters[1]
        batt.setSpeed(self.tool.Tps)
        self.BattList.append(self.tool.Tps)
        
        self.line = self.can_read(0x30b)
        self.tool.decode( self.message)
        temp = self.meters[0]
        temp.setSpeed(self.tool.Temp)
        self.TempList.append(self.tool.Temp)

        air = self.meters[4]
        air.setSpeed(self.tool. Air)
        self.AirList.append(self.tool.Air)

        
        
        
        self.line = self.can_read(0x305)
        self.tool.decode( self.message )
        afr = self.meters[3]
        afr.setSpeed(self.tool.Lambda1)
        self.AfrList.append(self.tool.Lambda1)
        
        self.line = self.can_read(0x300)
        self.tool.decode( self.message )
        boost = self.meters[2]
        boost.setSpeed(self.tool.Map)
        self.BoostList.append(self.tool.Map)
        
        self.line = self.can_read(0x306)
        self.tool.decode( self.message )
        oil = self.meters[5]
        oil.setSpeed(self.tool.Oil)
        self.OilList.append(self.tool.Oil)
        
        QTimer.singleShot(300, self.increment)
        
        
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
 
    def can_read(self, id):

        filter = [{'can_id':id, 'can_mask': 0x3FF }]

            
        # Multiple filters, will be handled in Python
        #self.bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000, can_filters=filter)
        #self.bus.set_filters(filter)
        self.bus.flush_tx_buffer()
        while True:
            try:
                newMess = self.bus.recv(0)

            except:
                print("err")
            #print(newMess)
            data = str(newMess)
            idr = data[41:44]
            if idr != "":
                #print(newMess, id)
                if int(idr,16) == id:
                    break

        mess = data[69:].replace(' ', '' )
        self.message = idr+"#"+mess
        #print(message)
        #return message
