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


count = 0
time.sleep(0.1)	
print('Press CTL-C to exit')


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
			print(message)
			count += 1


	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	file.close() 
    #os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	
	quit()
