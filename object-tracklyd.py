from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import random

# parsing arguments
ap = argparse.ArgumentParser()
# --video : optional path to the input video file
# use your webcam if no arguments
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
# OpenCV object tracker
# set to kcf(Kernelized Correlation Filters) by default
ap.add_argument("-t", "--tracker", type=str, default="kcf",
                help="OpenCV object tracker type")
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

# grab reference to webcam if no video path
if not args.get("video", False):
    print("starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])
# initialize FPS throughput estimator
fps = None
circleX = 500
circleY =  0

# down: 0 up: 1 left: 2 right: 3
direction = 0
prevdir = 0
dvelocity = 0
changeMode = 0

# loop over frames from stream
while True:
    # grab the current frame, then handle
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame

    # check if reached end of stream
    if frame is None:
        break
    # resize the frame and grab the frame dimensions TODO
    frame = imutils.resize(frame, width=1000)
    (H, W) = frame.shape[:2]

    # check if is tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates for object
        (success, box) = tracker.update(frame)

        # check if tracking succeed
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if circleY > 500:
                break
            
            if circleX > x and circleX < x + w and circleY > y and circleY < y + h: 
                if (circleX - x) < (x + w - circleX):
                    if (circleY - y) < (y + h - circleY):
                        direction = 2
                        dvelocity = 0
                        #circleX = x
                    else:
                        direction = 0
                        dvelocity = 0
                        #circleX = x
                else:
                    if (circleY - y) < (y + h - circleY):
                        direction = 3
                        dvelocity = 0
                        #circleX = x+w
                    else:
                        direction = 0
                        dvelocity = 0
                        #circleX = x+w
                changeMode = 1

            if circleY <= 5:
                prevdir = direction
                direction = 0
            if circleX <= 5:
                prevdir = direction
                direction = 3
                changeMode = 1
            if circleX >= 995:
                prevdir = direction
                direction = 2
                changeMode = 1
            cv2.circle(frame, (circleX,circleY), 5, (255, 0, 0), 10)
            cv2.rectangle(frame, (circleX - 5, circleY - 35), (circleX + 5, circleY), (0, 0, 255), 10)
            cv2.rectangle(frame, (circleX - 7, circleY - 50), (circleX - 5, circleY - 35), (0, 255, 255), 2)
            cv2.rectangle(frame, (circleX - 1, circleY - 50), (circleX + 1, circleY - 35), (0, 255, 255), 2)
            cv2.rectangle(frame, (circleX + 5, circleY - 50), (circleX + 7, circleY - 35), (0, 255, 255), 2)
            cv2.circle(frame, (circleX-5, circleY - 25), 2, (255, 0, 0), 4)
            cv2.circle(frame, (circleX+5, circleY - 25), 2, (255, 0, 0), 4)
            cv2.circle(frame, (circleX, circleY - 15), 3, (0, 255, 0), 6)
            cv2.circle(frame, (circleX, circleY - 17), 3, (0, 0, 255), 6)
            cv2.line(frame, (circleX - 8, circleY - 15), (circleX - 38, circleY - 35), (0,125,125), 3)
            cv2.line(frame, (circleX + 8, circleY - 15), (circleX + 38, circleY - 35), (0,125,125), 3)
            if (changeMode == 1):
                changeMode = 0
                cv2.circle(frame, (circleX,circleY), 5, (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 10)
                cv2.rectangle(frame, (circleX - 5, circleY - 35), (circleX + 5, circleY), (random.randrange(1, 255),0,random.randrange(1, 255)), 10)
                cv2.rectangle(frame, (circleX - 7, circleY - 50), (circleX - 5, circleY - 35), (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 2)
                cv2.rectangle(frame, (circleX - 1, circleY - 50), (circleX + 1, circleY - 35), (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 2)
                cv2.rectangle(frame, (circleX + 5, circleY - 50), (circleX + 7, circleY - 35), (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 2)
                cv2.circle(frame, (circleX-5, circleY - 25), 2, (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 4)
                cv2.circle(frame, (circleX+5, circleY - 25), 2, (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 4)
                cv2.circle(frame, (circleX, circleY - 15), 3, (random.randrange(1, 255), random.randrange(1, 255), random.randrange(1, 255)), 6)
                cv2.circle(frame, (circleX, circleY - 17), 3, (0, 0, 255), 6)
                cv2.line(frame, (circleX - 8, circleY - 15), (circleX - random.randrange(25, 40), circleY - random.randrange(1, 40)), (random.randrange(1, 255),random.randrange(1, 255),random.randrange(1, 255)), 2)
                cv2.line(frame, (circleX + 8, circleY - 15), (circleX + random.randrange(25, 40), circleY - random.randrange(1, 40)), (random.randrange(1, 255),random.randrange(1, 255),random.randrange(1, 255)), 2)
            if direction == 0:
                if prevdir == 2:
                    circleY = circleY + 5 + dvelocity
                    circleX = circleX - 2
                    dvelocity += 1
                elif prevdir == 3:
                    circleY = circleY + 5 + dvelocity
                    circleX = circleX + 2
                    dvelocity += 1
                else:
                    circleY = circleY + 5 + dvelocity
                    dvelocity += 1
            elif direction == 2:
                circleX = circleX - 2
                circleY = circleY - 5 + dvelocity
                dvelocity += 1
            elif direction == 3:
                circleX = circleX + 2
                circleY = circleY - 5 + dvelocity
                dvelocity += 1
            else:
                circleY = circleY - 5 + dvelocity
                dvelocity += 1

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
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        
    # show the output frame
    flip = cv2.flip(frame, +1) # where flip TODO
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if 's', select a bounding box to track
    if key == ord("s"):
        # select the box of object you want to track, then press ENTER / SPACE
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                showCrosshair=True)
            
        # start opencv object tracker with supplied box coordinates
        tracker.init(frame, initBB)
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
