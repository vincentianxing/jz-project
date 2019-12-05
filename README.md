# Project Useful Links

## Detection and Tracking with OpenCV

* videoio module: <https://docs.opencv.org/master/df/d2c/tutorial_table_of_content_videoio.html>

* Meanshift and Camshift for tracking object in video: <https://docs.opencv.org/master/d7/d00/tutorial_meanshift.html>

* Object tracking: <https://www.pyimagesearch.com/2018/07/30/opencv-object-tracking/>
  * `pip install --upgrade imutils`
  * `pip install opencv-contrib-python`
  * run: `python object-track.py --tracker csrt`

* Background subtraction for generating foreground mask: <https://docs.opencv.org/master/d1/dc5/tutorial_background_subtraction.html>

* Contours
  * Features: <https://docs.opencv.org/3.4/dd/d49/tutorial_py_contour_features.html>
  * Hierarchy: <https://docs.opencv.org/3.4/d9/d8b/tutorial_py_contours_hierarchy.html>

* Tracking
  * Hand detection: <https://github.com/PierfrancescoSoffritti/handy>

  * Finger detection:
    * <https://github.com/amarlearning/Finger-Detection-and-Tracking>
    * <http://www.benmeline.com/finger-tracking-with-opencv-and-python/>
  
  * Back projection: <https://docs.opencv.org/2.4/doc/tutorials/imgproc/histograms/back_projection/back_projection.html>

  * image_analysis.py: <https://github.com/benmel/point-to-define/blob/master/point_to_define/image_analysis.py>

## Motion of ball with PyGame

* Basic mechanism of "pingpong" (see code)

* Combining pygame and opencv: <https://github.com/stbnps/DanceCV>

* turtle module documentation: <https://docs.python.org/3.3/library/turtle.html?highlight=turtle#turtle.ycor>

* Bouncing ball simulator with turtle: <https://www.youtube.com/watch?v=ibdICVK0W3Q>

## Other

* Webcam test: <https://www.codingforentrepreneurs.com/blog/opencv-python-web-camera-quick-test/>

* Possible resolution for OpenCV: <https://stackoverflow.com/questions/19448078/python-opencv-access-webcam-maximum-resolution>

## Detection with OpenPose

* Documents: <https://github.com/CMU-Perceptual-Computing-Lab/openpose> (including installation)

  * Installation: <https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation.md#installation>

  * Installation prerequisite: <https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/prerequisites.md#mac-os-prerequisites>

  * Configuration: <https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation.md#installation>

  * Cmake-gui configuration for mac
    * `/usr/local/Cellar/caffe`
    * `/usr/local/lib/libcaffe.dylib`
  
  * Building for mac:
  `cd build/`
  `make -j sysctl -n hw.logicalcpu`

* Quick start: <https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/quick_start.md#quick-start>

* Demo: <https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/demo_overview.md>
  * Demo output keypoints: <https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md#keypoint-ordering-in-c-python>
  
* Human foot keypoint dataset: <https://cmu-perceptual-computing-lab.github.io/foot_keypoint_dataset/>

### Member: Ran Liu, Yuda Liu, Vincent Zhu
