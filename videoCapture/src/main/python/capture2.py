#!/usr/bin/python2.7
__author__ = 'anton'

UNKNOWN = "unknown"
TRAINED_DATA = "test.yml"
LABELS_FILE = 'labels.csv'
FOR_TRAIN_DIR = 'forTrain'
FOR_TRAIN_SCALED_DIR = "forTrain/scaled"
DOWNSCALE = 5
VIDEO_INPUT = 0

import sys
sys.path.append('/usr/local/opencv/lib/python2.7/dist-packages')
import csv
import cv2
from time import time
import collections
import numpy as N
import os
import python_servo2 as ps

model = cv2.createLBPHFaceRecognizer()
faceDetector = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
person = collections.namedtuple("Person", "labelId name")
labelsNames = []


def saveSnapshot(imageInt, filename):
    cv2.imwrite(filename, imageInt)


def detectFaces(image):
    t1 = time()
    clone = image.copy(cv2.cv.CV_INTER_NN)
    minisize = (clone.shape[1] / DOWNSCALE, clone.shape[0] / DOWNSCALE)
    miniframe = cv2.resize(clone, minisize)
    gray = cv2.cvtColor(miniframe, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    faces = faceDetector.detectMultiScale(equalized, minSize=(25, 25), minNeighbors=4)
    croppedFaces = []
    x = y = x_w = y_h = 0

    for f in faces:
        x, y, w, h = [v*DOWNSCALE for v in f]
        x_w = x + w
        y_h = y + h
        cv2.rectangle(image, (x, y), (x_w, y_h), (255, 255, 255))
        cropped = image[y:y+h, x:x+w]
        croppedFaces.append(cropped)
        t2 = time()
        print str(frameId) + " | face detected in " + str(round((t2-t1)*1000, 0)) + " milliseconds"

    return croppedFaces, x, y, x_w, y_h


def trainFace(g_capture):
    name = raw_input("Please enter the name : ")

    timestamp = time()
    winname1 = "camera_a" + str(timestamp)
    winname2 = "camera_b" + str(timestamp)
    cv2.namedWindow(winname1)
    cv2.namedWindow(winname2)


    nextLabelId = getNextLabelId()
    imagesForTrain = []
    ns = []
    counter = 0
    while counter < 20:
        try:
            flag, image = g_capture.read()

            if image is not None:
                cv2.imshow(winname1, image)
                croppedFaces, x, y, x_w, y_h = detectFaces(image)
                cv2.imshow(winname2, image)
                if len(croppedFaces) == 1:
                    gray = cv2.cvtColor(croppedFaces[0], cv2.COLOR_BGR2GRAY)
                    minisize = (100, 100)
                    miniframe = cv2.resize(gray, minisize)
                    imagesForTrain.append(miniframe)
                    counter += 1
                    ns.append(nextLabelId)

            key = cv2.waitKey(10)
            if key == 27:
                cv2.destroyAllWindows()
                break

        except KeyboardInterrupt:
            cv2.destroyWindow(winname1)
            cv2.destroyWindow(winname2)
            cv2.destroyAllWindows()
            break
        except:
            cv2.destroyWindow(winname1)
            cv2.destroyWindow(winname2)
            cv2.destroyAllWindows()
            break

    model.train(imagesForTrain, N.array(ns))
    model.save(TRAINED_DATA)

    p = person(labelId=nextLabelId, name=name)
    labelsNames.append(p)

    saveLabels()
    counter = 0
    for face in imagesForTrain:
        path = FOR_TRAIN_SCALED_DIR + "/" + name + "/"
        if not os.path.exists(path):
            os.mkdir(path)

        ts = int(time())
        path = path + str(ts) + "/"
        if not os.path.exists(path):
            os.mkdir(path)

        saveSnapshot(face, path + str(counter) + ".png")
        counter += 1


def loadLabels():
    if os.path.exists(LABELS_FILE):
        with open(LABELS_FILE, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in spamreader:
                p = person(labelId=row[0], name=row[1])
                labelsNames.append(p)


def saveLabels():
    with open(LABELS_FILE, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in labelsNames:
            spamwriter.writerow([row.labelId, row.name])


def searchName(labelId):
    for person in labelsNames:
        if int(person.labelId) == int(labelId):
            return person.name

    return UNKNOWN


def loadFaces():
    counter = 0
    for r, d, f in os.walk(FOR_TRAIN_DIR):
        print d
        if not r.__contains__('.svn') and not r.__eq__(FOR_TRAIN_DIR):
            for files in os.listdir(r):
                path = r + "/" + files
                print path
                image = cv2.imread(path)
                croppedFaces, x, y, x_w, y_h = detectFaces(image)
                cv2.imwrite(FOR_TRAIN_DIR + "/" + str(counter) + ".png", image)
                for face in croppedFaces:
                    cv2.imwrite(FOR_TRAIN_DIR + "/cropped" + str(counter) + ".png", face)

                counter += 1

    print "load faces from file"


def getNextLabelId():
    result = 1
    for person in labelsNames:
        result = int(max(person.labelId, result)) + 1

    return result


def getRecognizedName(croppedFaces):
    if len(croppedFaces) > 0:
        model.load(TRAINED_DATA)
        for face in croppedFaces:
            minisize = (face.shape[1] / DOWNSCALE, face.shape[0] / DOWNSCALE)
            miniframe = cv2.resize(face, minisize)
            gray = cv2.cvtColor(miniframe, cv2.COLOR_BGR2GRAY)
            minisize = (100, 100)
            miniframe = cv2.resize(gray, minisize)
            equalized = cv2.equalizeHist(miniframe)
            label, predicted_confidence = model.predict(equalized)
            confidence = 1 - (predicted_confidence/255)
            if confidence > 0.5:
                name = searchName(label)
                print label, confidence, name
                return name
    return None


def recognizeFace(image, position, name):
    t1 = time()
    croppedFaces, x, y, x_w, y_h = detectFaces(image)
    p1 = x + (x_w - x)/2
    p2 = y - 20
    if abs(position[0] - p1) > 30 or abs(position[1] - p2) > 30:
        name = getRecognizedName(croppedFaces)
        position = (p1, p2)

    if name is not None:
        cv2.putText(image, name, (p1, p2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        t2 = time()
        print str(frameId) + " | face recognized in " + str(round((t2-t1)*1000, 0)) + " milliseconds"

    fp1 = x + (x_w - x)/2
    fp2 = y + (y_h - y)/2
    facePosition = (fp1, fp2)
    return name, position, facePosition


def adjustAngle(fpDiff, previousAngle):
    if fpDiff < 0:
        if fpDiff < -10:
            previousAngle -= 1
        else:
            if fpDiff < -20:
                previousAngle -= 2
    else:
        if fpDiff > 10:
            previousAngle += 1
        else:
            if fpDiff > 20:
                previousAngle += 2

    if previousAngle > 180:
        previousAngle = 180

    if previousAngle <= 50:
        previousAngle = 50

    return previousAngle


def trackFace(facePosition, image, lastfps, previousAngleHorizontal, previousAngleVertical):
    t1 = time()
    fp1diff = (width / 2 - facePosition[0])
    fp2diff = (height / 2 - facePosition[1])
    angleH = previousAngleHorizontal
    angleV = previousAngleVertical
    if fp1diff != width / 2 and fp2diff != height / 2:

        angleH = adjustAngle(fp1diff, previousAngleHorizontal)
        angleV = adjustAngle(-1 * fp2diff, previousAngleVertical)

        if angleH != previousAngleHorizontal and angleV != previousAngleVertical:
            previousAngleHorizontal = angleH
            previousAngleVertical = angleV

            a1, a2 = ps.move(angleH, angleV)
            print str(frameId) + " | positions", a1, a2
            if a1 != previousAngleHorizontal:
                print str(frameId) + " | horizontal not the same a1 = " + a1 + " prev = " + previousAngleHorizontal
            if a2 != previousAngleVertical:
                print str(frameId) + " | vertical not the same a2 = " + a2 + " prev = " + previousAngleVertical
            t2 = time()
            print str(frameId) + " | moved in " + str(round((t2-t1)*1000, 0)) + " milliseconds"

    cv2.putText(image, "fps: " + str(lastfps) + ", angleH: " + str(angleH) + ", angleV: " + str(angleV), (30, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    return previousAngleHorizontal, previousAngleVertical


def recognizedFaceMain(g_capture):
    lasttime = time()
    framecounter = 0

    timestamp = time()

    # winname1 = "camera_a" + str(timestamp)
    winname2 = "camera_b" + str(timestamp)
    # cv2.namedWindow(winname1)
    cv2.namedWindow(winname2)

    previousAngleHorizontal = 130
    previousAngleVertical = 71
    ps.init(previousAngleHorizontal, previousAngleVertical)

    position = (0, 0)
    name = None

    lastfps = 0
    global frameId

    while True:
        try:
            newtime = time()

            flag, image = g_capture.read()
            frameId = str(int(time()*1000))
            if image is not None:
                # cv2.imshow(winname1, image)
                name, position, facePosition = recognizeFace(image, position, name)
                duration = newtime - lasttime
                framecounter += 1

                if duration >= 1:
                    lastfps = framecounter
                    framecounter = 0
                    lasttime = time()

                previousAngleHorizontal, previousAngleVertical = trackFace(facePosition, image, lastfps, previousAngleHorizontal, previousAngleVertical)

                cv2.imshow(winname2, image)

            key = cv2.waitKey(10)
            if key == 27:
                cv2.destroyAllWindows()
                ps.destroy()
                break

        except KeyboardInterrupt:
            # cv2.destroyWindow(winname1)
            cv2.destroyWindow(winname2)
            cv2.destroyAllWindows()
            ps.destroy()
            break


def main():
    global var, g_capture, height, width
    print cv2.__file__
    loadLabels()

    g_capture = cv2.VideoCapture(VIDEO_INPUT)
    var = raw_input("Do you want train (t), recognize (r), train from files (f) : ")

    height = 480
    width = 640
    g_capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
    g_capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)

    if var == "r":
        recognizedFaceMain(g_capture)

    elif var == "t":
        trainFace(g_capture)

    elif var == "f":
        loadFaces()
    g_capture.release()


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print "exit"
            break
