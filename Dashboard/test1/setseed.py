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

def ubx_change_rate():
      msg = [0xb5, 0x62, 0x06, 0x08, 0x06, 0x00, 0x64, 0x00, 0x01, 0x00, 0x01, 0x00, 0x7A, 0x12]
      ser.write(msg)
	  
def ubx_init():
      msg = [0xb5, 0x62, 0x0A, 0x04, 0x00, 0x00, 0x0E, 0x34]
      ser.write(msg)
	  
def set_auto():
      msg = [0xB5,0x62,0x06,0x24,0x24,0x00,0xFF,0xFF,0x04,0x03,0x00,0x00,0x00,0x00,0x10,0x27,0x00,0x00,0x05,0x00,0xFA,0x00,0xFA,0x00,0x64,0x00,0x2C,0x01,0x00,0x3C,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x50,0xA4]
      ser.write(msg)	  
	  
def ubx_init():
      msg = [0xb5, 0x62, 0x0A, 0x04, 0x00, 0x00, 0x0E, 0x34]
      ser.write(msg)
	  
	  
print("set gps speed to 10Hz")      
set_auto()
ubx_change_rate()     
ubx_init()
