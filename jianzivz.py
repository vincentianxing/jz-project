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
import skin_tracking as track

hand_hist = None  # histogram generated from hand sample
size = 9  # number of rectangles
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
traverse_point = []
k = True

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
}
# grab object tracker using dict
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize bounding box coordinates
initBB = None

# grab reference to webcam if no video given
if not args.get("video", False):
    print("starting video stream...")
    # read in webcam stream cv2.VideoCapture(0)
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])

#colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

#globals
WIDTH = 600
HEIGHT = 400
# img_radius = 70
PAD_WIDTH = 8
PAD_HEIGHT = 80
# ball_pos = [0,0]
ball_vel = [0, 0]
score = 0

#canvas declaration
camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("Play Balls!")
screen = pygame.display.set_mode([WIDTH, HEIGHT])
image = pygame.image.load('jianzi.png')
rec = image.get_rect()
img_radius = int(rec.width/2)


def ball_init():
    global ball_pos, ball_vel, ball_x  # these are vectors stored as lists
    # ball_x = int(random.randrange(0, WIDTH - img_radius))
    ball_x = int(random.randrange(1, WIDTH + 1 - rec.width))
    # ball_pos = [ball_x, img_radius + 1]
    rec.left = ball_x
    rec.centery = 1
    horz = int(random.randrange(1, 4))
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

    #update ball
    ball_vel[1] += 0.981

    if ball_vel[0] > 0:
        ball_vel[0] = int(random.randrange(1, 4))
    else:
        ball_vel[0] = int(random.randrange(-4, -1))
    rec.centerx += int(ball_vel[0])
    rec.centery += int(ball_vel[1])

    #draw ball
    #pygame.draw.circle(canvas, RED, ball_pos, 20, 0)
    screen.blit(image, rec.center)

    #ball collision check on top and bottom walls
    if int(rec.centery) <= 0.5:
        ball_vel[1] = - ball_vel[1]
    if int(rec.left) <= img_radius:
        ball_vel[0] = -ball_vel[0]
    if int(rec.right) >= WIDTH - img_radius:
        ball_vel[0] = -ball_vel[0]

    # if int(rec.centery) in range(y - img_radius, y + h - img_radius) and int(rec.centerx) in range(x - img_radius, x + w + img_radius):
    #     score += 1
    #     ball_vel[1] = -ball_vel[1]
    #     ball_vel[0] *= 0.5
    #     ball_vel[1] *= 1.0

    if int(rec.bottom) in range(y - img_radius, y) and int(rec.centerx) in range(x - img_radius, x + w + img_radius):
        score += 1
        ball_vel[1] = -ball_vel[1]
        vel_x = random.choice((-1, 1))
        if abs(ball_vel[1]) >= 24.0:
            vel_y = random.uniform(0.8, 0.9)
        else:
            vel_y = random.uniform(1, 1.2)
        ball_vel[0] *= vel_x
        ball_vel[1] *= vel_y

    # if int(ball_pos[1]) >= y - img_radius:
    #     if int(ball_pos[1]) <= y + h - 1 - img_radius:
    #         if int(ball_pos[0]) == x - img_radius:
    #             score += 1
    #             ball_vel[0] = -ball_vel[0]
    #         elif int(ball_pos[0]) == x + w - 1 - img_radius:
    #             score += 1
    #             ball_vel[0] = -ball_vel[0]

    if int(rec.centery) >= HEIGHT + 1 - img_radius:
        ball_init()

    #update scores
    myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    label = myfont1.render("Score "+str(score), 1, (255, 255, 0))
    canvas.blit(label, (50, 20))


init()

is_hand_hist_created = False

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

    # show the output frame
    #flip = cv2.flip(frame, +1)
    #cv2.imshow("frame", flip)

    key = cv2.waitKey(1) & 0xFF

    # if 's', select a bounding box to track
    if key == ord("r"):
        k = False
        # select the box of object you want to track, then press ENTER / SPACE
        initBB = cv2.selectROI("frame", frame, fromCenter=False,
                               showCrosshair=True)

        # start opencv object tracker with supplied box coordinates
        tracker.init(frame, initBB)
        is_hand_hist_created = True

    # if 'z', use skin tracking
    if key == ord("z"):
        is_hand_hist_created = True
        hand_hist = track.hand_histogram(frame)

    if is_hand_hist_created:
        if k:
            frame = track.manipulate(frame, hand_hist)

    else:
        frame = track.draw_rect(frame)

    cv2.imshow("Frame", frame)

    if key == ord("q"):
        break

    screen.fill([0, 0, 0])
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame.swapaxes(0, 1)
    
    # input frame to pygame screen
    frame = pygame.surfarray.make_surface(frame)
    screen.blit(frame, (0, 0))
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
