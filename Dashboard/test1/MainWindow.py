from PyQt5.QtWidgets import QMainWindow, QGridLayout,QPushButton, QWidget, QLabel, QApplication, QLCDNumber
from PyQt5.QtCore import QObject, pyqtSignal, QEvent, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor
import os

from matplotlib.pyplot import close, figure, get_current_fig_manager, plot, xlabel, ylabel, title, grid, connect, show, ioff
from ui_mainwindow import Ui_MainWindow
import sys, os, glob
from Dial import Dial
import datetime
import numpy as np

import numpy
import can

import time
import csv

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
dataList = []

os.system("sudo /sbin/ip link set down can0")
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
time.sleep(0.1)

headers = ['hh', 'Rpm', 'Tps', 'Temp', 'Boost', 'Afr', 'Volt', 'Air','Fuel']
csvfile =  open('my_data.csv', 'a', newline='')
csv_writer = csv.writer(csvfile)
csv_writer.writerow(headers)


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
	mess = message[78:]
	message = canid+"#"+mess

	data = message[4:]
	print("mess:", message, "canid:",canid," message:",data)
	if ( canid == '300' ):
		val = float(int(data[12:14],16)*256+int(data[15:17],16))
		Map = val/1000
		val = int(data[0:2],16)*256+int(data[3:5],16)
		Rpm = val
		print("rpm=", Rpm)
		val = int(data[6:8],16)*100/255
		Tps = val
	if ( canid == '301' ):
		Lambda2 = float(int(data[6:8],16))*2*14.7/255
	if ( canid == '305' ):
		Lambda1=  int(data[0:2],16)*2*14.7/255
	if ( canid == '306' ):
		Fuel = float(int(data[18:20],16)*256+int(data[21:23],16))*0.1
	if ( canid == '308'):
		val = 0.0
		val = int(data[0:2],16)*256+int(data[3:5],16)
		Volt = val
		Volt = Volt*18/1023
	if ( canid == '30b'):
		Temp = float((int(data[0:2],16)))*150/255-10
		Air = float((int(data[9:11],16)))*150/255-10

def task():
	if Rpm >0:
		now = datetime.datetime.now()
		formatted_time = now.strftime("%H:%M:%S:%f")[:-4]  # Remove the last 3 digits of microseconds
		dataList.append(formatted_time)
		dataList.append(format(Rpm,'.2f'))
		dataList.append(format(Tps,'.2f'))
		dataList.append(format(Temp,'.2f'))
		dataList.append(format(Map,'.2f'))
		dataList.append(format(Lambda1,'.2f'))
		dataList.append(format(Volt,'.2f'))
		dataList.append(format(Air,'.2f'))
		dataList.append(format(Fuel,'.2f'))
		csv_writer.writerow(dataList)
		csvfile.flush()
		dataList.clear()

def can_rx_task():

    nb = 0
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)
    print("init")
    while True:
        #if nb==10:
        #     nb=0
        task()
        #nb = nb+1
        message = bus.recv(24)
        decodeData(message)
        time.sleep(0.05)

t = Thread(target = can_rx_task)	# Start receive thread
t.start()

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
    KmList = []
    TempWin = pyplot
    #tool = CanProtocol.CanTool()
    oldMess = ""

    def myShutDown(self):
        os.system("sudo /sbin/halt")

    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.currentport = ""
        self.showFullScreen()
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
        Quit.clicked.connect(self.close)
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

    def defLists(self, sList_list,sTitle ):

        figure(num=sTitle,figsize=(12,10))
        thismanager = get_current_fig_manager()
        for sList in sList_list:
                t = np.arange(0.0, len(sList), 1)
                plot(t, sList, linewidth=1, linestyle="-")

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

        data_list = [self.TpsList, self.RpmList]
        #self.defList(self.TpsList, "TPS" )
        self.defLists(data_list,"TPS RPM" )
        self.graphWin('events', 'TPS RPM', 'Thottle body% / Rpm')


    def write_to_csv(self, filename, headers):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(headers)
            writer.writerows(lignes)    #csv_writer.writerows(zip(*data_arrays))

    def fileWrite(self, data, name):

        try:
            f = open(name, 'w+')
            for line in data:
                f.writelines(str(line)+'\n')
            f.close()

        except:
            print("Error writing file")


    def saveAll(self):

        headers = ['Rpm', 'Tps', 'Temp', 'Boost', 'Afr', 'Volt', 'Air','Fuel']
        self.write_to_csv('my_data.csv', [self.RpmList, self.TpsList, self.TempList, self.BoostList, self.AfrList, self.BattList, self.AirList, self.FuelList], headers)
        print("save")
        #self.fileWrite(self.TempList, "temp.txt") 
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
