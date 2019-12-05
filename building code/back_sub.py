import numpy as np
import cv2

cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorMOG2()

while(1):
    ret, frame = cap.read()

    fgmask = fgbg.apply(frame)
    rgbmask = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
    rgbframe = frame & rgbmask

    #cv2.imshow('fgmask', frame)
    cv2.imshow('frame', rgbframe)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break


cap.release()
cv2.destroyAllWindows()
