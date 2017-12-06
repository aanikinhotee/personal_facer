#!/usr/bin/python2.7
__author__ = 'anton'

import sys
sys.path.append('/usr/local/opencv/lib/python2.7/dist-packages')
import cv2
import random
import numpy as np

def main():
    # Create windows to show the captured images
    cv2.namedWindow("window_a", cv2.CV_WINDOW_AUTOSIZE)
    cv2.namedWindow("window_b", cv2.CV_WINDOW_AUTOSIZE)

    # Structuring element
    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,4))
    ## Webcam Settings
    capture = cv2.VideoCapture(0)

    height = 480
    width = 640

    capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
    fourcc = cv2.cv.CV_FOURCC('M', 'J', 'P', 'G')

    #dimensions
    # frameWidth = capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
    # frameHeight = capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    flag, frame = capture.read()
    previous = cv2.blur(frame, (5, 5))

    while True:
        # Capture a frame
        flag, frame = capture.read()

        current = cv2.blur(frame, (5, 5))
        difference = cv2.absdiff(current, previous)


        frame2 = cv2.cvtColor(difference, cv2.cv.CV_RGB2GRAY)
        retval, thresh = cv2.threshold(frame2, 10, 0xff, cv2.THRESH_BINARY)
        dilated1 = cv2.dilate(thresh, es)
        dilated2 = cv2.dilate(dilated1, es)
        dilated3 = cv2.dilate(dilated2, es)
        dilated4 = cv2.dilate(dilated3, es)

        x = cv2.countNonZero(dilated4)
        if x > 0:
            print x

        cv2.imshow("window_a", dilated4)
        cv2.imshow("window_b", frame)

        previous = current

        key = cv2.waitKey(10)
        if key == 27:
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print "exit"
            break
        except:
            break
