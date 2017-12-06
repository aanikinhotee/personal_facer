__author__ = 'anton'

import serial

serdev = '/dev/ttyACM0'
s = serial.Serial(serdev, 9600)
a = ""
while 1:
	a = s.readline()
	print(a)