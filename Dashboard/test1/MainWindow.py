from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore


from ui_mainwindow import Ui_MainWindow
import sys, os, glob
import pickle
from TablePrototype import TableWindow, TableModel
from TablePrototype import ModelVE, ModelSA
from Speedometer import Speedometer
import serial
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionVolumetric_Efficiency.triggered.connect(self.openVE)
        self.ui.actionSpark_Advance.triggered.connect(self.openSA)

        self.currentport = ""

        layout = QGridLayout(self.ui.centralwidget)
        self.ui.centralwidget.setLayout(layout)

        try:
            self.vetable = pickle.load(open("tuningve.smv", "rb"))
        except FileNotFoundError:
            print("No existing tuning found!")
            self.vetable = ModelVE()

        try:
            self.satable = pickle.load(open("tuningsa.smv", "rb"))
        except FileNotFoundError:
            print("No existing tuning found!")
            self.satable = ModelSA()

        self.vemodel = TableModel(self.vetable)
        self.vewindow = TableWindow("Volumetric Efficiency Table")
        self.vewindow.setModel(self.vemodel)

        self.samodel = TableModel(self.satable)
        self.sawindow = TableWindow("Spark Advance Table")
        self.sawindow.setModel(self.samodel)

        self.rpm_value = 0
        self.tps_value = 0
        self.temp_value = 0
        self.batt_value = 0
        self.map_value = 0
        self.meters = []
        
        rpm = Speedometer("RPM", "", 1, 8000, 0.98, 0.20, 0,1)
        self.meters.append(rpm)
        layout.addWidget(rpm, 0, 0)
        
        tps = Speedometer("TPS", "", 0, 100, 0.98, 0.20, 0,1)
        self.meters.append(tps)
        layout.addWidget(tps, 0, 1)

        temp = Speedometer("TEMP", "", 0, 120, 0.98, 0.20, 0,1.5)
        self.meters.append(temp)
        layout.addWidget(temp, 1, 0)
        
        batt = Speedometer("BATT", "", 0, 15, 0.98, 0.20, 0,1.5)
        self.meters.append(batt)
        layout.addWidget(batt, 1, 1)

        map = Speedometer("MAP", "", 0, 100, 0.98, 0.20, 0,1.5)
        self.meters.append(map)
        layout.addWidget(map, 1, 2)

        QTimer.singleShot(5, self.increment)

    def increment(self):
        self.rpm_value = (self.rpm_value + random.randint(0,100)) % 8000
        rpm = self.meters[0]
        rpm.setSpeed(self.rpm_value)
        
        self.tps_value = (self.tps_value + random.randint(0,1)) % 100
        tps = self.meters[1]
        tps.setSpeed(self.tps_value)
        
        self.temp_value = (self.temp_value + random.randint(0,1)) % 120
        temp = self.meters[2]
        temp.setSpeed(self.temp_value)
         
        QTimer.singleShot(5, self.increment) 

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