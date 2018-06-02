from PyQt5.QtWidgets import QMainWindow, QGridLayout,QPushButton, QWidget, QLabel, QApplication, QLCDNumber
from PyQt5.QtCore import QObject, pyqtSignal, QEvent, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor
import os

from pylab import close, figure, get_current_fig_manager, plot, xlabel, ylabel, title, grid, connect, show, ioff
from ui_mainwindow import Ui_MainWindow
import sys, os, glob
from Dial import Dial
import serial
#import CanProtocol

import numpy
import can

import time

from matplotlib import pyplot
from string import Template
from threading import Thread

Temp = 0.0
Volt = 0.0
Map = 0.0
Lambda1 = 0.0
Lambda2 = 0.0
Air = 0.0
Fuel = 0.0 
Rpm = 0
Tps = 0

def decodeData(message):

	global Temp 
	global Volt 
	global Map 
	global Lambda1 
	global Lambda2 
	global Air 
	global Fuel 
	global Rpm 
	global Tps 
	
	message = str(message)
	canid = message[41:44]
	mess = message[69:].replace(' ', '' )
	message = canid+"#"+mess
	
	data = message[4:]
	#print("mess:", message, "canid:",canid," message:",data)
	if ( canid == '300' ):
		val = float(int(data[8:10],16)*256+int(data[10:12],16))
		Map = val/1000
		val = int(data[0:2],16)*256+int(data[2:4],16)
		Rpm = val
		val = int(data[4:6],16)*100/255
		Tps = val
	if ( canid == '301' ):
		Lambda2 = float(int(data[4:6],16))*2*14.7/255
	if ( canid == '305' ):
		Lambda1=  float(int(data[0:2],16))*2*14.7/255
	if ( canid == '306' ):
		Fuel = float(int(data[12:14],16)*256+int(data[14:16],16))*0.1
	if ( canid == '308'):
		val = 0.0
		val = float(int(data[0:2],16)*256+int(data[2:4],16))
		Volt = val
		Volt = Volt*18/1000
	if ( canid == '30b'):
		Temp = float((int(data[0:2],16)*160))/255-10
		Air = float((int(data[6:8],16)*160))/255-10

			
def can_rx_task():
	bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
	while True:
		message = bus.recv()
		decodeData(message)

t = Thread(target = can_rx_task)	# Start receive thread
t.start()
			

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)
ser.isOpen()


def getTime(string,format,returnFormat):
        return time.strftime(returnFormat, time.strptime(string, format)) # Convert date and time to a nice printable format

def getLatLng(latString,lngString):
        #print(latString, lngString)
        lat = ""
        lng = ""
        if (len(latString) > 0 ):
               lat = latString[:2].lstrip('0') + "." + "%.7s" % str(float(latString[2:])*1.0/60.0).lstrip("0.")
               lng = lngString[:3].lstrip('0') + "." + "%.7s" % str(float(lngString[3:])*1.0/60.0).lstrip("0.")
        return(lat,lng)

def decode(lines):
        print("Time:", lines[1][0:2]+":"+lines[1][2:4]+":"+lines[1][4:6])
        print("Status (A=OK,V=KO):", lines[2])
        latlng = getLatLng(lines[3],lines[5])
        print("Lat,Long: ", latlng[0], lines[4], ", ", latlng[1], lines[6])
        print("Speed (knots):", lines[7])

def getGpsTime(lines):
        return(lines[1][0:2]+":"+lines[1][2:4]+":"+lines[1][4:6])
        
def getGpsLat(lines):
        return(lines[3])        
        
def getGpsLong(lines):
        return(lines[5])        

def getGpsSpeed(lines):
		  ch = lines[7]
		  if ( ch == ''):
		  	   ch = '0'
		  km = float(ch)*1.852	   
		  return(int(km))


def checksum(line):
   checkString = line.partition("*")
   checksum = 0
   for c in checkString[0]:
      checksum ^= ord(c)

   try: # Just to make sure
      inputChecksum = int(checkString[2].rstrip(), 16);
   except:
      print("Error in string")
      return False

   if checksum == inputChecksum:
      return True
   else:
      print("=====================================================================================")
      print("===================================Checksum error!===================================")
      print("=====================================================================================")
      print(hex(checksum), "!=", hex(inputChecksum))
      return False

def readString():
        while 1:
                while ser.read().decode("utf-8") != '$': # Wait for the begging of the string
                      pass # Do nothing
                line = ser.readline().decode("utf-8") # Read the entire string
                return line             

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
    
    
class DigitalSpeed(QLCDNumber):

    def __init__(self, parent=None):
        super(DigitalSpeed, self).__init__(parent)
        self.setSegmentStyle(QLCDNumber.Filled)
        self.showTime("152")
        self.resize(200, 40)     

    def showTime(self,texte):
        self.display(texte)
          
class GpsPoint():
	
    latitude = 0
    longitude = 0
	
    def __init__(self, Lat=0, Long= 0):	
        latitude = Lat
        longitude = Long
	
    def GpsPoint():
        latitude = 0.0
        longitude = 0.0
	   
    def GpsPoint(Lat, Long):
        latitude = Lat
        longitude = Long

           
class Track():
	
	 #43.7112163,4.011291
	 #43.7112131,4.0025198
	 
    finishLinePoint1 = GpsPoint(43.7112163,4.011291)
    finishLinePoint2 = GpsPoint(43.7112131,4.0025198)
    

    def isFinishLinePassed(self,start, finish):
		
        delta0 = (self.finishLinePoint1.latitude - self.finishLinePoint2.latitude) * (finish.longitude - start.longitude)
        delta0 = delta0 -(self.finishLinePoint1.longitude - self.finishLinePoint2.longitude) * (finish.latitude - start.latitude)
        if (delta0 == 0.0 ):
             return(0)
        delta1 = (self.finishLinePoint1.longitude - self.finishLinePoint2.longitude) * (start.latitude - self.finishLinePoint2.latitude)
        delta1 = delta1 -(self.finishLinePoint1.latitude - self.finishLinePoint2.latitude) * (start.longitude - self.finishLinePoint2.longitude)	
        delta2 = (finish.longitude - start.longitude) * (start.latitude - self.finishLinePoint2.latitude)
        delta2 = delta2 -(finish.latitude - start.latitude) * (start.longitude - self.finishLinePoint2.longitude)

        ka = delta1/delta0
        kb = delta2/delta0
		
        if (ka < 0 or ka > 1 or kb < 0 or kb > 1):
      	  return(0)
      
        Long = start.longitude + ka * (finish.longitude - start.longitude)
        Lat = start.latitude + ka * (finish.latitude - start.latitude)

        intersection = GpsPoint(Lat, Long);
        return(1)         
		  
	  
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
    KmList = []
    TempWin = pyplot
    #tool = CanProtocol.CanTool()
    oldMess = ""
    myTrack = Track() 
    start = GpsPoint(0,0)
    
    
    def myShutDown(self):
        os.system("sudo /sbin/halt")

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
        
        Quit = self.addPushB( 0, 'linux.jpg', layout)
        Quit.clicked.connect(exit)
        motor = self.addPushB( 2, 'motor.jpg', layout)
        speed = self.addPushB( 3, 'speed.jpg', layout)   
        #speed.clicked.connect( layout.setEnabled(false))
        FileSave = self.addPushB( 4, 'save.jpg', layout)
        FileSave.clicked.connect(self.saveAll)
        shutdown = self.addPushB( 5, 'shutdown.jpg', layout)
        shutdown.clicked.connect(self.myShutDown)
       
        temp = Dial("TEMP", "C", 0, 120, 0.98, 0.20, 0,1)

        clickable(temp).connect(self.graphTemp)
        self.meters.append(temp)
        layout.addWidget(temp, 3, 1, 3, 3)
        layout.setSpacing(0)
        
        afr = Dial("AFR", "", 0, 20, 0.98, 0.20, 0,1)
        clickable(afr).connect(self.graphAfr)
        self.meters.append(afr)
        layout.addWidget(afr, 0, 1, 3, 3)   

        layout.setContentsMargins(0,0,0,0)
                        
        batt = Dial("BATT", "volt", 0, 15, 0.98, 0.20, 0,1)
        clickable(batt).connect(self.graphBatt)
        self.meters.append(batt)
        layout.addWidget(batt, 5, 5, 1, 1 )

        air = Dial("AIR", "C", -10, 150, 0.98, 0.2, 0, 1 )
        clickable(air).connect(self.graphAir)
        self.meters.append(air)
        layout.addWidget(air, 5, 6, 1, 1 )
        
        fuel = Dial("FUEL", "bar", 0, 150, 0.98, 0.2, 0, 1 )
        clickable(fuel).connect(self.graphFuel)
        self.meters.append(fuel)
        layout.addWidget(fuel, 5, 7, 1, 1 )

        rpm = Dial("RPM", "tr/min", 0, 7500, 0.98, 0.2, 0, 1 )
        clickable(rpm).connect(self.graphRpm)
        self.meters.append(rpm)
        layout.addWidget(rpm, 0, 5, 6, 3 )

        boost = Dial("BOOST", "bar", 0, 3, 0.98, 0.20, 0,1)
        clickable(boost).connect(self.graphBoost)
        self.meters.append(boost)
        layout.addWidget(boost, 0, 8, 3, 3)

        tps = Dial("TPS", "%", 0, 100, 0.98, 0.2, 0, 1 )
        clickable(tps).connect(self.graphTps)
        self.meters.append(tps)
        layout.addWidget(tps, 3, 8, 3, 3 )
        
        km = DigitalSpeed()
        clickable(km).connect(self.graphKm)
        self.meters.append(km)
        layout.addWidget(km, 0, 5, 1, 3 ) 

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
        self.KmList.append(0)
        self.KmList.append(200)
        

        #filter = [{'can_id':0x300, 'can_mask': 0x00f }]
        #bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)

        #self.showFullScreen()
        print("start")
        QTimer.singleShot(50,self.increment)
       
    def addPushB(self,pos,icon, layout):

        size = QSize(100,100)
        pb = QPushButton(QIcon(icon), '', self)
        pb.setIconSize(size)
        layout.addWidget(pb, pos, 0)
        return pb
    
    def on_click(self,event):
        # get the x and y coords, flip y from top to bottom
        if event.button == 1:
            ioff()
            close()
           
    def graphWin(self, xLabel, yLabel, Title):
         
        xlabel(xLabel)
        ylabel(yLabel)
        title(Title)
        grid(True)
        connect('button_press_event', self.on_click)
        mng = pyplot.get_current_fig_manager()
        mng.window.showMaximized()
        show()

    def defList(self, sList,sTitle ):

        t = numpy.arange(0.0, len(sList), 1) 
        s = sList
        figure(num=sTitle,figsize=(12,10))
        thismanager = get_current_fig_manager()
        plot(t, s, color="red", linewidth=1, linestyle="-")

    def graphTemp(self):
        
        self.defList(self.TempList, "TEMPERATURE" )
        self.graphWin('time(s)', 'Temperature', 'Water C')
        
    def graphKm(self):
        
        self.defList(self.KmList, "Speed" )
        self.graphWin('time(1/50s)', 'km/h', 'km/h')
                
                
    def graphBatt(self):
        
        self.defList(self.BattList, "VOLTAGE" )
        self.graphWin('events', 'Volts', 'Voltage V')
        
    def graphBoost(self):
        
        self.defList(self.BoostList, "BOOST" )
        self.graphWin('events', 'Boost', 'Boost mbar')


    def graphAfr(self):

        self.defList(self.AfrList, "AFR" )        
        self.graphWin('events', 'AFR', 'Afr')

        
    def graphAir(self):

        self.defList(self.AirList, "AIR" )        
        self.graphWin('events', 'AIR', 'Air')


    def graphFuel(self):

        self.defList(self.FuelList, "FUEL" )        
        self.graphWin('events', 'FUEL', 'Fuel')


    def graphRpm(self):

        self.defList(self.RpmList, "RPM" )        
        self.graphWin('events', 'RPM', 'Rpm')

    def graphTps(self):

        self.defList(self.TpsList, "TPS" )        
        self.graphWin('events', 'TPS', 'Thottle body%')



    def saveAll(self):

        print("save")
        self.fileWrite(self.TempList, "temp.txt") 
        self.fileWrite(self.BoostList, "boost.txt") 
        self.fileWrite(self.AirList, "air.txt") 
        self.fileWrite(self.AfrList, "afr.txt") 
        self.fileWrite(self.RpmList, "rpm.txt") 
        self.fileWrite(self.TpsList, "tps.txt") 
        self.fileWrite(self.FuelList, "fuel.txt") 
        self.fileWrite(self.BattList, "batt.txt") 
        return


    def openVE(self):
        self.vewindow.show()

    def openSA(self):
        self.sawindow.show()

    def closeEvent(self, evt):
        evt.accept()
 
    def increment(self):
	
        global Temp 
        global Volt 
        global Map 
        global Lambda1 
        global Lambda2 
        global Air 
        global Fuel 
        global Rpm 
        global Tps 

        
        batt = self.meters[2]
        batt.setSpeed(Volt)
        self.BattList.append(Volt)

        temp = self.meters[0]
        temp.setSpeed(Temp)
        self.TempList.append(Temp)
        air = self.meters[3]
        air.setSpeed(Air)
        self.AirList.append(Air)

        afr = self.meters[1]
        afr.setSpeed(Lambda1)
        self.AfrList.append(Lambda1)
        
        fuel = self.meters[4]
        fuel.setSpeed(Fuel)
        self.FuelList.append(Fuel)
        
        boost = self.meters[6]
        boost.setSpeed(Map)
        self.BoostList.append(Map)
        tps = self.meters[7]
        tps.setSpeed(Tps)
        self.TpsList.append(Tps)
        rpm = self.meters[5]
        rpm.setSpeed(Rpm)
        self.RpmList.append(Rpm)
        
        
        
        QTimer.singleShot(50, self.increment)