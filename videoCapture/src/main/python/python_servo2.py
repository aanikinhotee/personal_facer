#!/usr/bin/python
import serial
import time

delimeter = ";\r\n"


def readFromSerial(s):
    a = ""
    result = ""
    while a != delimeter:
        a = s.readline()
        if a != "" and a != delimeter:
            if a.find("=") > 0:
                command, value = a.split("=")
                result = command, int(value.strip(delimeter))

    return result


def init(initAgleHorizontal, initAngleVertical):
    global s
    serdev = '/dev/ttyACM0'
    s = serial.Serial(serdev, 9600)
    readFromSerial(s)

    a1, a2 = move(str(initAgleHorizontal), str(initAngleVertical))


def move(angleHorizontal, angleVertical):
    s.write("HA=" + str(angleHorizontal) + delimeter)
    a1 = readFromSerial(s)

    s.write("VA=" + str(angleVertical) + delimeter)
    a2 = readFromSerial(s)
    return a1[1], a2[1]


def destroy():
    time.sleep(5)
    s.close()


if __name__ == '__main__':
    init(90, 70)
    while True:
        try:
            varHor = raw_input("Give an angle horizontal: ")
            varVert = raw_input("Give an angle vertical: ")
            move(varHor, varVert)
        except KeyboardInterrupt:
            print "exit"
            break
        except:
            break

    destroy()