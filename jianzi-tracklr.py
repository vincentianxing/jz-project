from __future__ import print_function
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import random
import pygame
from pygame.locals import *
import numpy as np
import sys

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
    vs = VideoStream(src=0).start()  # read in webcam stream cv2.VideoCapture(0)
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])
# initialize FPS throughput estimator
fps = None

#colors
WHITE = (255,255,255)
RED = (255,0,0)

#globals
WIDTH = 600
HEIGHT = 400      
image_radius = 70
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
ball_pos = [0,0]
ball_vel = [0,0]
#paddle_vel = 0
#paddle2_vel = 0
score = 0
#r_score = 0

#canvas declaration
camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("Play Balls!")
screen = pygame.display.set_mode([WIDTH,HEIGHT])
image = pygame.image.load('jianzi.png')

def ball_init():
    global ball_pos, ball_vel, ball_x # these are vectors stored as lists
    ball_x = int(random.randrange(0, WIDTH - image_radius))
    ball_pos = [ball_x, image_radius + 1]
    horz = int(random.randrange(1,4))
    vert = 0
    
    #if right == False:
    #    horz = - horz
    ball_vel = [horz, vert]

# define event handlers
def init():
    global score  # these are floats
    score = 0
    ball_init()

def draw(canvas, x, y, w, h):
    global ball_pos, ball_vel, score

    #pygame.draw.line(canvas, WHITE, [0, HEIGHT + 1 - PAD_WIDTH],[WIDTH, HEIGHT + 1 - PAD_WIDTH], 1)

    ball_vel[1] += 0.981
    #update ball
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    #draw ball
    #pygame.draw.circle(canvas, RED, ball_pos, 20, 0)
    screen.blit(image, ball_pos)

    #ball collision check on top and bottom walls
    if int(ball_pos[1]) <= image_radius:
        ball_vel[1] = - ball_vel[1]
    if int(ball_pos[0]) <= image_radius:
        ball_vel[0] = -ball_vel[0]
    if int(ball_pos[0]) >= WIDTH + 1 - image_radius:
        ball_vel[0] = -ball_vel[0]
    
    if int(ball_pos[1]) in range(y - image_radius, y + h - image_radius) and int(ball_pos[0]) in range(x - image_radius, x + w + image_radius):
        score += 1
        ball_vel[1] = -ball_vel[1]
        ball_vel[0] *= 0.5
        ball_vel[1] *= 1.0

    # if int(ball_pos[1]) >= y - image_radius:
    #     if int(ball_pos[1]) <= y + h - 1 - image_radius:
    #         if int(ball_pos[0]) == x - image_radius:
    #             score += 1
    #             ball_vel[0] = -ball_vel[0]
    #         elif int(ball_pos[0]) == x + w - 1 - image_radius:
    #             score += 1
    #             ball_vel[0] = -ball_vel[0]
                    



    if int(ball_pos[1]) >= HEIGHT + 1 - image_radius:
        ball_init()

    #update scores
    myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    label = myfont1.render("Score "+str(score), 1, (255,255,0))
    canvas.blit(label, (50,20)) 

init()



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
    #mask = backSub.apply(frame)  # frame -> mask

    # declare x, y
    x = 0
    y = 0
    w = 0
    h = 0

    # check if is tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates for object
        (success, box) = tracker.update(frame)

        # check if tracking succeed
        if success:
            (x, y, w, h) = [int(v) for v in box]
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
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
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # show the output frame
    flip = cv2.flip(frame, +1)
    cv2.imshow("frame", flip)
    key = cv2.waitKey(1) & 0xFF

    # if 's', select a bounding box to track
    if key == ord("s"):
        # select the box of object you want to track, then press ENTER / SPACE
        initBB = cv2.selectROI("frame", frame, fromCenter=False,
                               showCrosshair=True)

        # start opencv object tracker with supplied box coordinates
        tracker.init(frame, initBB)
        fps = FPS().start()

    elif key == ord("q"):
        break

    #ret, frame = camera.read()
		
    screen.fill([0,0,0])
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame.swapaxes(0, 1)
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0,0))
    draw(screen, x, y, w, h)
        
    pygame.display.update()
        
    for event in pygame.event.get():
        if event.type == QUIT or event.type == KEYDOWN:
            sys.exit(0)

# if using webcam, release the pointer
if not args.get("video", False):
    vs.stop()
# otherwise, release the file pointer
else:
    vs.release()

# close windows
cv2.destroyAllWindows()