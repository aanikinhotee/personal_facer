#!/usr/bin/python
import serial
import time
serdev = '/dev/ttyACM0'
s = serial.Serial(serdev, 9600)
a = ""
while a == "":
	a = s.readline()
	print(a)

while(True):
	userNumber = raw_input('Give me an integer number: ')
	s.write(userNumber)

time.sleep(5)
s.close()
