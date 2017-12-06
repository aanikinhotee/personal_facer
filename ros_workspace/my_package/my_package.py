#!/usr/bin/env python2.6
import roslib
roslib.load_manifest('my_package')
import sys
import rospy
import cv

from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

#import sayanton


min_size = (20, 20)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0

class image_converter:

  def __init__(self):
    self.image_pub = rospy.Publisher("/imagecv",Image)

    cv.NamedWindow("Image window", 1)
    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/usb_cam/image_raw",Image,self.callback)
    self.cascade = cv.Load("/home/anton/ros_workspace/my_package/haarcascade_frontalface_alt2.xml")


  def callback(self,data):
    try:
      cv_image = self.bridge.imgmsg_to_cv(data, "bgr8")
    except CvBridgeError, e:
      print e

    gray = cv.CreateImage((cv_image.width,cv_image.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(cv_image.width / image_scale),
  	  	       cv.Round (cv_image.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(cv_image, gray, cv.CV_BGR2GRAY)
  
    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
  
    cv.EqualizeHist(small_img, small_img)

    #say = 0
    if(self.cascade):
        t = cv.GetTickCount()
        faces = cv.HaarDetectObjects(small_img, self.cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
        t = cv.GetTickCount() - t
        print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.))
        if faces:
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv.Rectangle(cv_image, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
		#say = 1
	   
    cv.ShowImage("Image window", cv_image)
    cv.WaitKey(3)

    try:
      self.image_pub.publish(self.bridge.cv_to_imgmsg(cv_image, "bgr8"))
      #if say == 1:
      #  import festival
      #  tts = pyTTS.Create()
      #  tts.SetVoiceByName('MSSam')
      #  tts.Speak("Hello, fellow Python programmer")
    except CvBridgeError, e:
      print e


def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print "Shutting down"
  cv.DestroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
