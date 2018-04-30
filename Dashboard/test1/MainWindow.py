from PyQt5.QtWidgets import QMainWindow, QGridLayout,QPushButton
from PyQt5.QtCore import QObject, pyqtSignal, QEvent, QTimer


from pylab import close, figure, get_current_fig_manager, plot, xlabel, ylabel, title, grid, connect, show, ioff
from ui_mainwindow import Ui_MainWindow
import sys, os, glob
from Dial import Dial
import serial
import CanProtocol

import numpy
import can
import time

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
    TpsList = []
    RpmList = []
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
        layout.setContentsMargins(0,0,0,0)
        layout.setColumnMinimumWidth(1,1)
       
        
        self.move(0,0)
        
        self.ui.centralwidget.setLayout(layout)
                          
        self.temp_value = 0
        self.batt_value = 0
        self.boost_value = 0
        self.afr_value = 0
        self.tps_value = 0
        self.rpm_value = 0
        self.message =""
        self.meters = []
        self.line = ''
        self.file = ''
        
        btn = QPushButton('QUIT', self)
        btn.clicked.connect(exit)
        
        temp = Dial("TEMP", "C", 0, 120, 0.98, 0.20, 0,1)

        clickable(temp).connect(self.graphTemp)
        self.meters.append(temp)
        layout.addWidget(temp, 3, 0, 2, 3)
        layout.setSpacing(0)
        
        afr = Dial("AFR", "", 0, 20, 0.98, 0.20, 0,1)
        clickable(afr).connect(self.graphAfr)
        self.meters.append(afr)
        layout.addWidget(afr, 0, 0, 2, 3)   

        layout.setContentsMargins(50,20,0,0)
        
        #self.showFullScreen()

        batt = Dial("BATT", "volt", 0, 15, 0.98, 0.20, 0,1)
        clickable(batt).connect(self.graphBatt)
        self.meters.append(batt)
        layout.addWidget(batt, 4, 3, 1, 1 )

        air = Dial("AIR", "C", -10, 150, 0.98, 0.2, 0, 1 )
        clickable(air).connect(self.graphAir)
        self.meters.append(air)
        layout.addWidget(air, 4, 4, 1, 1 )
        
        fuel = Dial("FUEL", "bar", 0, 150, 0.98, 0.2, 0, 1 )
        clickable(fuel).connect(self.graphFuel)
        self.meters.append(fuel)
        layout.addWidget(fuel, 4, 5, 1, 1 )

        rpm = Dial("RPM", "tr/min", 0, 7500, 0.98, 0.2, 0, 1 )
        clickable(rpm).connect(self.graphRpm)
        self.meters.append(rpm)
        layout.addWidget(rpm, 0, 3, 4, 3 )

        boost = Dial("BOOST", "bar", 0, 3, 0.98, 0.20, 0,1)
        clickable(boost).connect(self.graphBoost)
        self.meters.append(boost)
        layout.addWidget(boost, 0, 6, 2, 3)

        tps = Dial("TPS", "%", 0, 100, 0.98, 0.2, 0, 1 )
        clickable(tps).connect(self.graphTps)
        self.meters.append(tps)
        layout.addWidget(tps, 3, 6, 2, 3 )

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
        self.TpsList.append(0)
        self.TpsList.append(100)
        self.RpmList.append(0)
        self.RpmList.append(7500)

        filter = [{'can_id':0x300, 'can_mask': 0x00f }]
        self.bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)

        self.showFullScreen()
        QTimer.singleShot(50, self.increment)
       
    
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
        figure(num="BOOST",figsize=(20,20))
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
        
        t = numpy.arange(0.0, len(self.FuelList), 1) 
        s = self.FuelList
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


    def graphRpm(self):
        
        t = numpy.arange(0.0, len(self.RpmList), 1) 
        s = self.RpmList
        figure(num="RPM",figsize=(12,12))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('RPM')
        title('Rpm')
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()    

    def graphTps(self):
        
        t = numpy.arange(0.0, len(self.TpsList), 1) 
        s = self.TpsList
        figure(num="TPS",figsize=(9.5,5.5))
        thismanager = get_current_fig_manager()
        #thismanager.window.wm_geometry("+0+0")  
        plot(t, s)
        xlabel('events')
        ylabel('RPM')
        title('rpm')
        grid(True)
        connect('button_press_event', self.on_click)
        
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()    

    def fastRead(self):

        self.line = self.can_read(0x300)
        if ( self.message != "#" ):
            self.tool.decode( self.message )
            boost = self.meters[6]
            boost.setSpeed(self.tool.Map)
            self.BoostList.append(self.tool.Map)
            tps = self.meters[7]
            tps.setSpeed(self.tool.Tps)
            self.TpsList.append(self.tool.Tps)
            rpm = self.meters[5]
            rpm.setSpeed(self.tool.Rpm)
            self.RpmList.append(self.tool.Rpm)

    def increment(self):
        
        self.fastRead()
        
        self.line = self.can_read(0x308)
        if ( self.message != "#" ):
            print("message",self.message)
            self.tool.decode( self.message )
            batt = self.meters[2]
            batt.setSpeed(self.tool.Volt)
            self.BattList.append(self.tool.Volt)

        self.fastRead()
        
        self.line = self.can_read(0x30b)
        if ( self.message != "#" ):
            self.tool.decode( self.message)
            temp = self.meters[0]
            temp.setSpeed(self.tool.Temp)
            #print("temp", self.tool.Temp)
            self.TempList.append(self.tool.Temp)
            air = self.meters[3]
            air.setSpeed(self.tool.Air)
            self.AirList.append(self.tool.Air)

        self.fastRead()

        self.line = self.can_read(0x305)
        if ( self.message != "#" ):
            self.tool.decode( self.message )
            afr = self.meters[1]
            afr.setSpeed(self.tool.Lambda1)
            print("afr", self.tool.Lambda1)
            self.AfrList.append(self.tool.Lambda1)
        
        self.fastRead()

        self.line = self.can_read(0x306)
        if ( self.message != "#" ):
            self.tool.decode( self.message )
            fuel = self.meters[4]
            fuel.setSpeed(self.tool.Fuel)
            self.FuelList.append(self.tool.Fuel)
        
        self.fastRead()

        QTimer.singleShot(50, self.increment)
        
        
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
            self.message = ""
            data = str(newMess)
            idr = data[41:44]
            if idr != "":
                #print(newMess, id)
                if int(idr,16) == id:
                    break
            else:
                #print(time.time())
                break
        mess = data[69:].replace(' ', '' )
        self.message = idr+"#"+mess
        #print(message)
