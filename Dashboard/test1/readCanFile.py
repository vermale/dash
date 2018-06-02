#!/usr/bin/python3
#
# can_logging_to_sdcard.py
# 
# This python3 program logs all CAN messages to the sd card.
# For use with PiCAN boards on the Raspberry Pi
# http://skpang.co.uk/catalog/pican2-canbus-board-for-raspberry-pi-2-p-1475.html
#
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
# 01-02-16 SK Pang
#
#
#
# TODO check for queue full
import time
import os
import queue
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

			
def read_file_task():
	with open("recvCan.txt")  as f: 
		for line in f: 
			q.put(line)

	
q = queue.Queue()	
t = Thread(target = read_file_task)	# Start receive thread
t.start()

# Main loop
try:
 
	while True:
		if q.empty() != True:	# Check if there is a message in queue
			message = q.get()
			decodeData(message)


	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	file.close() 
    #os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	
	quit()