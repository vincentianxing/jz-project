import unittest
import pytest
import numpy as np
import cv2
import time
import tracking as track

hand_hist = None
size = 9
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
traverse_point = []
is_hand_hist_created = False

cap = cv2.VideoCapture(0)
cap_test = cap.isOpened()

cx = -1
cy = -1

while cap.isOpened():
    # read first frame
    print(1)
    ret1, frame = cap.read()

    frame = track.draw_rect(frame)
    is_hand_hist_created = True
    hand_hist = track.hand_histogram(frame)

    # read next frame
    ret2, frame2 = cap.read()

    if is_hand_hist_created:
        frame2, max_cont = track.manipulate(frame, hand_hist)
        cx, cy = track.centroid(max_cont)
        a = np.array(max_cont)
    
    cap.release()
cv2.destroyAllWindows()

# test frame
def test():
    assert cap_test == True
    assert ret1 == True
    assert ret2 == True
    assert a.size != 0
    assert cx > 0
    assert cy > 0