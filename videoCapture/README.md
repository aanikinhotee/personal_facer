# virtualenv using

Virtualenv is a tool to isolate python environment


## initialize virtualenv

$ virtualenv -p /usr/bin/python2.7 .

$ source bin/activate

(videoCapture) $ pip install pyserial

(videoCapture) $ pip install numpy


## install opencv library

* download source (git clone https://github.com/opencv/opencv.git)
* cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local/opencv opencv
* make
* sudo checkinstall
* add /usr/local/opencv/lib/python2.7/dist-packages/cv2.so path to python classpath

