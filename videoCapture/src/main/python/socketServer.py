# Echo server program
import socket
import serial

delimeter = ";\r\n"
serialDevice = "/dev/ttyACM0"

def readFromSerial(serial1):
    a = ""
    result = ""
    while a != delimeter:
        a = serial1.readline()
        if a != "" and a != delimeter:
            if a.find("=") > 0:
                command, value = a.split("=")
                result = command, int(value.strip(delimeter))
    return result


def initSerial():
    global serial1
    serial1 = serial.Serial(serialDevice, 9600)
    result = readFromSerial(serial1)
    print result


if __name__ == '__main__':
    HOST = ''                 # Symbolic name meaning the local host
    PORT = 50007              # Arbitrary non-privileged port
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket1.bind((HOST, PORT))
    socket1.listen(1)
    counterA = 0
    #initSerial()

    while 1:
        conn, addr = socket1.accept()
        try:
            print 'Connected by', addr
            while 1:
                data = conn.recv(1024)
                counterA += 1
                conn.send('OK' + str(counterA))
            conn.close()
        except:
            conn.close()