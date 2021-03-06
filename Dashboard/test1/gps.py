import time
import serial

import os
import sys
from string import Template

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
        
def getGpsSpeed(lines):
        return(lines[7])

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
    
while 1:
        line = readString()
        lines = line.split(",")
        if checksum(line):
                if lines[0] == "GPRMC":
                        #decode(lines)
                        print(getGpsTime(lines))
                        print(getGpsSpeed(lines))
                        
                        
