from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import random
import tracking as track
import numpy as np
import jianzi as jz

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
    "kcf": cv2.TrackerKCF_create,
}
# grab object tracker using dict
tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize bounding box coordinates
initBB = None

# intialize max contour
hand_hist = None # histogram generated from hand sample
size = 9 # number of rectangles
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
traverse_point = []
k = True
max_cnt = None
is_hand_hist_created = False

# grab reference to webcam if no video path
if not args.get("video", False):
    print("starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)
else:
    vs = cv2.VideoCapture(args["video"])
circleX = 500
circleY =  0

# down: 0 up: 1 left: 2 right: 3
direction = 0

# determine the previous direction
prevdir = 0

# deal with the accelaration
dvelocity = 0

# change the "phenotype" of jianzi if necessary
changeMode = 0

# set a timer for danmaku
timer = 0

# set the large timer for danmaku
xTimer = 0

# set the hitpoint
count = 5000

# set where the danmaku aims
location = -1

# set the left boss's danmaku
leftLocal = -1

# set and track the middle boss's location
bossX = 500
bossY = 100
dBossX = -1
dBossY = -1

# set the middle boss's tracking 
middleX = -1
middleY = -1

# set the right boss's bullets' trajectory
dRight = 0

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

     # display the tracking rectangles before tracking 
    if is_hand_hist_created:
        if k:
            frame, max_cnt = track.manipulate(frame, hand_hist)
    else:
        frame = track.draw_rect(frame)

    # check if is tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates for object
        (success, box) = tracker.update(frame)

        # check if tracking succeed
        if success:
            (x, y, w, h) = [int(v) for v in box]
            # Game over
            if circleY > 600:
                break
            
            #when the tracked zone hits the jianzi
            if circleX > x and circleX < x + w and circleY > y and circleY < y + h: 
                #determine the direction and reset the acceleration.
                if (circleX - x) < (x + w - circleX):
                    if (circleY - y) < (y + h - circleY):
                        direction = 2
                        dvelocity = 0
                    else:
                        direction = 0
                        dvelocity = 0
                else:
                    if (circleY - y) < (y + h - circleY):
                        direction = 3
                        dvelocity = 0
                    else:
                        direction = 0
                        dvelocity = 0
                changeMode = 1
            # hit the upper bound
            if circleY <= 5:
                prevdir = direction
                direction = 0
            # hit the left bound and rebounce
            if circleX <= 5:
                prevdir = direction
                direction = 3
                changeMode = 1
            # hit the right bound and rebounce
            if circleX >= 995:
                prevdir = direction
                direction = 2
                changeMode = 1

              # game over when hitpoint reaches 0
            if count < 0:
                break

            # display the danmaku: prestage
            if timer < 100:
                # aim the player
                if timer == 0:
                    location = circleX
                timer += 1
                cv2.line(frame, (location, 0), (location, 600), (255,255,255),5)

            # shoot the danmaku and check if it hits the player
            if timer >= 100:
                timer +=1
                cv2.rectangle(frame, (location - (timer - 98) * 5, 0), (location + (timer - 98) * 5, 600), (255, 255, 255), -1)
                if timer >= 110:
                    cv2.rectangle(frame, (location - (timer - 108) * 5, 0), (location + (timer - 108) * 5, 600), (0, 165, 255), -1)
                if timer >= 120:
                    cv2.rectangle(frame, (location - (timer - 118) * 5, 0), (location + (timer - 118) * 5, 600), (0, 255, 0), -1)
                if timer >= 130:
                    cv2.rectangle(frame, (location - (timer - 128) * 5, 0), (location + (timer - 128) * 5, 600), (255, 0, 0), -1)
                if timer >= 140:
                    cv2.rectangle(frame, (location - (timer - 138) * 5, 0), (location + (timer - 138) * 5, 600), (0, 255, 255), -1)
                #check if it hits the player
                if circleX >= (location - (timer - 98) * 5) and circleX <= (location + (timer - 98) * 5):
                    count -= 1
                    cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                    cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)

            # reset the timer
            if timer >= 160:
                timer = 0
            
            # median stage
            if xTimer >= 400 and xTimer < 1000:
                #Middle
                cv2.circle(frame, (bossX,bossY), 50, (128, 234, 67), -1)
                cv2.line(frame, (bossX - 10, bossY - 25), (bossX - 30, bossY - 45), (0, 0, 0), 8)
                cv2.line(frame, (bossX + 10, bossY - 25), (bossX + 30, bossY - 45), (0, 0, 0), 8)
                cv2.circle(frame, (bossX - 15,bossY - 10), 4, (0, 0, 0), -1)
                cv2.circle(frame, (bossX + 15,bossY - 10), 4, (0, 0, 0), -1)
                cv2.line(frame, (bossX - 25,bossY + 20), (bossX + 25,bossY + 20), (0, 0, 0), 8)
                #Left
                cv2.circle(frame, (250,100), 50, (97, 128, 234), -1)
                cv2.line(frame, (240, 75), (220, 55), (0, 0, 0), 8)
                cv2.line(frame, (260, 75), (280, 55), (0, 0, 0), 8)
                cv2.circle(frame, (235,90), 4, (0, 0, 0), -1)
                cv2.circle(frame, (265,90), 4, (0, 0, 0), -1)
                cv2.line(frame, (225, 120), (275, 120), (0, 0, 0), 8)
                #Right
                cv2.circle(frame, (750,100), 50, (203, 35, 150), -1)
                cv2.line(frame, (740, 75), (720, 55), (0, 0, 0), 8)
                cv2.line(frame, (760, 75), (780, 55), (0, 0, 0), 8)
                cv2.circle(frame, (735,90), 4, (0, 0, 0), -1)
                cv2.circle(frame, (765,90), 4, (0, 0, 0), -1)
                cv2.line(frame, (725, 120), (775, 120), (0, 0, 0), 8)

                #Draw the corresponding danmaku
                if xTimer >= 480:
                    #the left boss
                    if (xTimer % 60) == 0:
                        leftLocal = circleY
                    if (xTimer % 60) <= 20:
                        cv2.line(frame, (0, leftLocal), (1000, leftLocal), (255,255,255), 4)
                    if (xTimer % 60) > 20 and (xTimer % 60) <= 35:
                        cv2.line(frame, (0, leftLocal), (1000, leftLocal), (97, 128, 234), 8)
                        # check if this hits the player
                        if leftLocal < circleY + 8 and leftLocal > circleY - 20:
                            count -= 1
                            cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                            cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)
                    
                    #the middle boss's tracking point
                    if (xTimer % 160) == 0:
                        middleX = circleX
                        middleY = circleY
                        dBossX = int(10 * (middleX - bossX)/(abs(middleX - bossX) + abs(middleY - bossY)))
                        dBossY = int(10 * (middleY - bossY)/(abs(middleX - bossX) + abs(middleY - bossY)))
                    if (xTimer % 160) < 80:
                        bossX += dBossX
                        bossY += dBossY
                        #check if it hits the player
                        if (circleX - bossX) * (circleX - bossX) + (circleY - bossY) * (circleY - bossY) < 3100:
                            count -= 1
                            cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                            cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)   
                
                    #the right boss
                    if (xTimer % 80) == 0:
                        dRight = 0
                    # south bullet
                    cv2.circle(frame, (750,120 + dRight * 8), 20, (0, 0, 0), -1)
                    cv2.circle(frame, (750,120 + dRight * 8), 15, (255, 255, 255), -1)
                    if (circleX - 750) * (circleX - 750) + (circleY - 120 - dRight * 8) * (circleY - 120 - dRight * 8) < 625:
                        count -= 1
                        cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                        cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  
                    # southeast bullet
                    cv2.circle(frame, (750 + dRight * 6, 120 + dRight * 6), 20, (0, 0, 0), -1)
                    cv2.circle(frame, (750 + dRight * 6, 120 + dRight * 6), 15, (255, 255, 255), -1)
                    if (circleX - 750 - dRight * 6) * (circleX - 750 - dRight * 6) + (circleY - 120 - dRight * 6) * (circleY - 120 - dRight * 6) < 625:
                        count -= 1
                        cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                        cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  
                    # southwest bullet
                    cv2.circle(frame, (750 - dRight * 6, 120 + dRight * 6), 20, (0, 0, 0), -1)
                    cv2.circle(frame, (750 - dRight * 6, 120 + dRight * 6), 15, (255, 255, 255), -1)
                    if (circleX - 750 + dRight * 6) * (circleX - 750 + dRight * 6) + (circleY - 120 - dRight * 6) * (circleY - 120 - dRight * 6) < 625:
                        count -= 1
                        cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                        cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  
                    # west bullet
                    cv2.circle(frame, (750 - dRight * 9, 120), 20, (0, 0, 0), -1)
                    cv2.circle(frame, (750 - dRight * 9, 120), 15, (255, 255, 255), -1)
                    if (circleX - 750 - dRight * 9) * (circleX - 750 - dRight * 9) + (circleY - 120) * (circleY - 120) < 625:
                        count -= 1
                        cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                        cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  

            if xTimer >= 1000:
                #Middle
                cv2.circle(frame, (500,100), 50, (128, 234, 67), -1)
                cv2.line(frame, (490, 75), (470, 55), (0, 0, 0), 8)
                cv2.line(frame, (510, 75), (530, 55), (0, 0, 0), 8)
                cv2.line(frame, (490, 55), (470, 75), (0, 0, 0), 8)
                cv2.line(frame, (510, 55), (530, 75), (0, 0, 0), 8)
                cv2.line(frame, (475,120), (525,120), (0, 0, 0), 8)
                #Left
                cv2.circle(frame, (250,100), 50, (97, 128, 234), -1)
                cv2.line(frame, (240, 75), (220, 55), (0, 0, 0), 8)
                cv2.line(frame, (260, 75), (280, 55), (0, 0, 0), 8)
                cv2.line(frame, (240, 55), (220, 75), (0, 0, 0), 8)
                cv2.line(frame, (260, 55), (280, 75), (0, 0, 0), 8)
                cv2.line(frame, (225, 120), (275, 120), (0, 0, 0), 8)
                #Right
                cv2.circle(frame, (750,100), 50, (203, 35, 150), -1)
                cv2.line(frame, (740, 75), (720, 55), (0, 0, 0), 8)
                cv2.line(frame, (760, 75), (780, 55), (0, 0, 0), 8)
                cv2.line(frame, (740, 55), (720, 75), (0, 0, 0), 8)
                cv2.line(frame, (760, 55), (780, 75), (0, 0, 0), 8)
                cv2.line(frame, (725, 120), (775, 120), (0, 0, 0), 8)

            if xTimer == 1200:
                xTimer = 200
            #update xTimer
            xTimer += 1
            #update right boss's timer
            dRight += 1

            # draw the "feet"
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # What a jianzi looks like when not hitting boundaries
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
            
            # where the appearance of jianzi changes randomly
            if (changeMode == 1):
                # change it back
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

            # speed up when falling
            if direction == 0:
                if prevdir == 2:
                    circleY = circleY + 5 + dvelocity
                    circleX = circleX - 3
                    dvelocity += 1
                elif prevdir == 3:
                    circleY = circleY + 5 + dvelocity
                    circleX = circleX + 3
                    dvelocity += 1
                else:
                    circleY = circleY + 5 + dvelocity
                    dvelocity += 1
            #slow down when rising
            elif direction == 2:
                circleX = circleX - 3
                circleY = circleY - 5 + dvelocity
                dvelocity += 1
            elif direction == 3:
                circleX = circleX + 3
                circleY = circleY - 5 + dvelocity
                dvelocity += 1
            else:
                circleY = circleY - 5 + dvelocity
                dvelocity += 1

    if max_cnt is not None:
        cx, cy = track.centroid(max_cnt)
        dist = cv2.pointPolygonTest(max_cnt, (circleX, circleY), True)
        # check collision with contour
        if (dist >= 0):
            if circleX < cx:
                direction = 2
                dvelocity = 0
            else:
                direction = 3
                dvelocity = 0
            changeMode = 1

        # Game over
        if circleY > 600:
            break
        # hit the upper bound
        if circleY <= 0:
            prevdir = direction
            direction = 0
        # hit the left bound and rebounce
        if circleX <= 50:
            prevdir = direction
            direction = 3
            changeMode = 1
        # hit the right bound and rebounce
        if circleX >= 950:
            prevdir = direction
            direction = 2
            changeMode = 1

            # game over when hitpoint reaches 0
        if count < 0:
            break

        # display the danmaku: prestage
        if timer < 100:
            # aim the player
            if timer == 0:
                location = circleX
            timer += 1
            cv2.line(frame, (location, 0), (location, 600), (255,255,255),5)

        # shoot the danmaku and check if it hits the player
        if timer >= 100:
            timer +=1
            cv2.rectangle(frame, (location - (timer - 98) * 5, 0), (location + (timer - 98) * 5, 600), (255, 255, 255), -1)
            if timer >= 110:
                cv2.rectangle(frame, (location - (timer - 108) * 5, 0), (location + (timer - 108) * 5, 600), (0, 165, 255), -1)
            if timer >= 120:
                cv2.rectangle(frame, (location - (timer - 118) * 5, 0), (location + (timer - 118) * 5, 600), (0, 255, 0), -1)
            if timer >= 130:
                cv2.rectangle(frame, (location - (timer - 128) * 5, 0), (location + (timer - 128) * 5, 600), (255, 0, 0), -1)
            if timer >= 140:
                cv2.rectangle(frame, (location - (timer - 138) * 5, 0), (location + (timer - 138) * 5, 600), (0, 255, 255), -1)
            #check if it hits the player
            if circleX >= (location - (timer - 98) * 5) and circleX <= (location + (timer - 98) * 5):
                count -= 1
                cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)

        # reset the timer
        if timer >= 160:
            timer = 0
        
        # median stage
        if xTimer >= 400 and xTimer < 1000:
            #Middle
            cv2.circle(frame, (bossX,bossY), 50, (128, 234, 67), -1)
            cv2.line(frame, (bossX - 10, bossY - 25), (bossX - 30, bossY - 45), (0, 0, 0), 8)
            cv2.line(frame, (bossX + 10, bossY - 25), (bossX + 30, bossY - 45), (0, 0, 0), 8)
            cv2.circle(frame, (bossX - 15,bossY - 10), 4, (0, 0, 0), -1)
            cv2.circle(frame, (bossX + 15,bossY - 10), 4, (0, 0, 0), -1)
            cv2.line(frame, (bossX - 25,bossY + 20), (bossX + 25,bossY + 20), (0, 0, 0), 8)
            #Left
            cv2.circle(frame, (250,100), 50, (97, 128, 234), -1)
            cv2.line(frame, (240, 75), (220, 55), (0, 0, 0), 8)
            cv2.line(frame, (260, 75), (280, 55), (0, 0, 0), 8)
            cv2.circle(frame, (235,90), 4, (0, 0, 0), -1)
            cv2.circle(frame, (265,90), 4, (0, 0, 0), -1)
            cv2.line(frame, (225, 120), (275, 120), (0, 0, 0), 8)
            #Right
            cv2.circle(frame, (750,100), 50, (203, 35, 150), -1)
            cv2.line(frame, (740, 75), (720, 55), (0, 0, 0), 8)
            cv2.line(frame, (760, 75), (780, 55), (0, 0, 0), 8)
            cv2.circle(frame, (735,90), 4, (0, 0, 0), -1)
            cv2.circle(frame, (765,90), 4, (0, 0, 0), -1)
            cv2.line(frame, (725, 120), (775, 120), (0, 0, 0), 8)

            #Draw the corresponding danmaku
            if xTimer >= 480:
                #the left boss
                if (xTimer % 60) == 0:
                    leftLocal = circleY
                if (xTimer % 60) <= 20:
                    cv2.line(frame, (0, leftLocal), (1000, leftLocal), (255,255,255), 4)
                if (xTimer % 60) > 20 and (xTimer % 60) <= 35:
                    cv2.line(frame, (0, leftLocal), (1000, leftLocal), (97, 128, 234), 8)
                    # check if this hits the player
                    if leftLocal < circleY + 8 and leftLocal > circleY - 20:
                        count -= 1
                        cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                        cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)
                
                #the middle boss's tracking point
                if (xTimer % 160) == 0:
                    middleX = circleX
                    middleY = circleY
                    dBossX = int(10 * (middleX - bossX)/(abs(middleX - bossX) + abs(middleY - bossY)))
                    dBossY = int(10 * (middleY - bossY)/(abs(middleX - bossX) + abs(middleY - bossY)))
                if (xTimer % 160) < 80:
                    bossX += dBossX
                    bossY += dBossY
                    #check if it hits the player
                    if (circleX - bossX) * (circleX - bossX) + (circleY - bossY) * (circleY - bossY) < 3100:
                        count -= 1
                        cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                        cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)   
            
                #the right boss
                if (xTimer % 80) == 0:
                    dRight = 0
                # south bullet
                cv2.circle(frame, (750,120 + dRight * 8), 20, (0, 0, 0), -1)
                cv2.circle(frame, (750,120 + dRight * 8), 15, (255, 255, 255), -1)
                if (circleX - 750) * (circleX - 750) + (circleY - 120 - dRight * 8) * (circleY - 120 - dRight * 8) < 625:
                    count -= 1
                    cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                    cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  
                # southeast bullet
                cv2.circle(frame, (750 + dRight * 6, 120 + dRight * 6), 20, (0, 0, 0), -1)
                cv2.circle(frame, (750 + dRight * 6, 120 + dRight * 6), 15, (255, 255, 255), -1)
                if (circleX - 750 - dRight * 6) * (circleX - 750 - dRight * 6) + (circleY - 120 - dRight * 6) * (circleY - 120 - dRight * 6) < 625:
                    count -= 1
                    cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                    cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  
                # southwest bullet
                cv2.circle(frame, (750 - dRight * 6, 120 + dRight * 6), 20, (0, 0, 0), -1)
                cv2.circle(frame, (750 - dRight * 6, 120 + dRight * 6), 15, (255, 255, 255), -1)
                if (circleX - 750 + dRight * 6) * (circleX - 750 + dRight * 6) + (circleY - 120 - dRight * 6) * (circleY - 120 - dRight * 6) < 625:
                    count -= 1
                    cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                    cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  
                # west bullet
                cv2.circle(frame, (750 - dRight * 9, 120), 20, (0, 0, 0), -1)
                cv2.circle(frame, (750 - dRight * 9, 120), 15, (255, 255, 255), -1)
                if (circleX - 750 - dRight * 9) * (circleX - 750 - dRight * 9) + (circleY - 120) * (circleY - 120) < 625:
                    count -= 1
                    cv2.line(frame, (circleX + 25, circleY), (circleX + 35, circleY), (0, 0, 255), 4)
                    cv2.line(frame, (circleX + 20, circleY - 10), (circleX + 20, circleY + 10), (0, 0, 255), 4)  

        if xTimer >= 1000:
            #Middle
            cv2.circle(frame, (500,100), 50, (128, 234, 67), -1)
            cv2.line(frame, (490, 75), (470, 55), (0, 0, 0), 8)
            cv2.line(frame, (510, 75), (530, 55), (0, 0, 0), 8)
            cv2.line(frame, (490, 55), (470, 75), (0, 0, 0), 8)
            cv2.line(frame, (510, 55), (530, 75), (0, 0, 0), 8)
            cv2.line(frame, (475,120), (525,120), (0, 0, 0), 8)
            #Left
            cv2.circle(frame, (250,100), 50, (97, 128, 234), -1)
            cv2.line(frame, (240, 75), (220, 55), (0, 0, 0), 8)
            cv2.line(frame, (260, 75), (280, 55), (0, 0, 0), 8)
            cv2.line(frame, (240, 55), (220, 75), (0, 0, 0), 8)
            cv2.line(frame, (260, 55), (280, 75), (0, 0, 0), 8)
            cv2.line(frame, (225, 120), (275, 120), (0, 0, 0), 8)
            #Right
            cv2.circle(frame, (750,100), 50, (203, 35, 150), -1)
            cv2.line(frame, (740, 75), (720, 55), (0, 0, 0), 8)
            cv2.line(frame, (760, 75), (780, 55), (0, 0, 0), 8)
            cv2.line(frame, (740, 55), (720, 75), (0, 0, 0), 8)
            cv2.line(frame, (760, 55), (780, 75), (0, 0, 0), 8)
            cv2.line(frame, (725, 120), (775, 120), (0, 0, 0), 8)

        if xTimer == 1200:
            xTimer = 200
        #update xTimer
        xTimer += 1
        #update right boss's timer
        dRight += 1

        # What a jianzi looks like when not hitting boundaries
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
        
        # where the appearance of jianzi changes randomly
        if (changeMode == 1):
            # change it back
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

        # speed up when falling
        if direction == 0:
            if prevdir == 2:
                circleY = circleY + 5 + dvelocity
                circleX = circleX - 3
                dvelocity += 1
            elif prevdir == 3:
                circleY = circleY + 5 + dvelocity
                circleX = circleX + 3
                dvelocity += 1
            else:
                circleY = circleY + 5 + dvelocity
                dvelocity += 1
        #slow down when rising
        elif direction == 2:
            circleX = circleX - 3
            circleY = circleY - 5 + dvelocity
            dvelocity += 1
        elif direction == 3:
            circleX = circleX + 3
            circleY = circleY - 5 + dvelocity
            dvelocity += 1
        else:
            circleY = circleY - 5 + dvelocity
            dvelocity += 1

    key = cv2.waitKey(1) & 0xFF

    # if 's', select a bounding box to track
    if key == ord("s"):
        # select the box of object you want to track, then press ENTER / SPACE
        initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                showCrosshair=True)
        # start opencv object tracker with supplied box coordinates
        tracker.init(frame, initBB)
        is_hand_hist_created = True
        k = False

    elif key == ord("z"):   
        is_hand_hist_created = True
        hand_hist = track.hand_histogram(frame)

    elif key == ord("q"):
        break

    elif key == ord("r"):
        jz.main()

   
    
    # show the output frame
    flip = cv2.flip(frame, +1) # where flip TODO
    cv2.imshow("Frame", flip)

# if using webcam, release the pointer
if not args.get("video", False):
    vs.stop()
# otherwise, release the file pointer
else:
    vs.release()

# close windows
cv2.destroyAllWindows()