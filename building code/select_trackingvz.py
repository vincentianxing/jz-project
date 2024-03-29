from __future__ import print_function
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2

# parsing arguments
ap = argparse.ArgumentParser()
ap.add_argument('--input', type=str,
                help='Path to a video or a sequence of image.', default='vtest.avi')
ap.add_argument('--algo', type=str,
                help='Background subtraction method (KNN, MOG2).', default='MOG2')
# --video : optional path to the input video file
# use your webcam if no arguments
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
# OpenCV object tracker
# set to kcf(Kernelized Correlation Filters) by default
ap.add_argument("-t", "--tracker", type=str, default="kcf",
                help="OpenCV object tracker type")

arg = ap.parse_args()
args = vars(ap.parse_args())

# call appropriate object tracker constructor
# intialize dict for tracker
OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}
# grab object tracker using dict
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize bounding box coordinates
initBB = None

# create background subtractor objects
# generate foreground mask
if arg.algo == 'MOG2':
    backSub = cv2.createBackgroundSubtractorMOG2()
else:
    backSub = cv2.createBackgroundSubtractorKNN()

# grab reference to webcam if no video given
if not args.get("video", False):
    print("starting video stream...")
    # read in webcam stream cv2.VideoCapture(0)
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])
# initialize FPS throughput estimator
fps = None

# loop over frames from stream
while True:
    # grab the current frame, then handle
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    # check if reached end of stream
    if frame is None:
        break

    # resize the frame and grab the frame dimensions TODO
    frame = imutils.resize(frame, width=600)
    (H, W) = frame.shape[:2]

    # update the background model for mask
    mask = backSub.apply(frame)  # frame -> mask

    # check if is tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates for object
        (success, box) = tracker.update(mask)

        # check if tracking succeed
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # update FPS counter
        fps.update()
        fps.stop()

        # initialize info displayed on frame
        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No"),
            ("FPS", "{:.2f}".format(fps.fps())),
        ]
        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            #flip = cv2.flip(fgMask, +1)
            cv2.putText(mask, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # show the output frame
    flip = cv2.flip(frame, +1)
    cv2.imshow("mask", flip)
    key = cv2.waitKey(1) & 0xFF

    # if 's', select a bounding box to track
    if key == ord("s"):
        # select the box of object you want to track, then press ENTER / SPACE
        initBB = cv2.selectROI("mask", mask, fromCenter=False,
                               showCrosshair=True)

        # start opencv object tracker with supplied box coordinates
        tracker.init(mask, initBB)
        fps = FPS().start()

    elif key == ord("q"):
        break

# if using webcam, release the pointer
if not args.get("video", False):
    vs.stop()
# otherwise, release the file pointer
else:
    vs.release()

# close windows
cv2.destroyAllWindows()
