import numpy as np
import cv2
import time

# capture video
cap = cv2.VideoCapture(0)

while(True):
    # capture frame-by-frame
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 680)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # set framerate 30
    cap.set(cv2.CAP_PROP_FPS, 30)

    # read frame
    ret, frame = cap.read()

    # operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # display the resulting frame
    flip = cv2.flip(frame, +1)

    #cv2.imshow('frame',frame)
    cv2.imshow('gray', gray)
    cv2.imshow('flip', flip)
    
    #cv2.resizeWindow('frame', 1200, 900)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
