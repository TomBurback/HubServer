# Smart Home Serial Communicator
#--------------------------------
# Sends data through serial port to Arduino.
# Arduino responds by setting pins connected to relays high or low.

import serial

ser_port = serial.Serial('COM4')

while(True):
	state = input("Turn on LED: 1\nTurn off LED: 0\n")
	if(state == '1'):
		ser_port.write(b'1')
	else:
		ser_port.write(b'0')