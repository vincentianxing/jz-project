import unittest
import pytest
import numpy as np
import cv2
import time
import tracking as track
import jianzi as jz

hand_hist = None
size = 9
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
traverse_point = []
is_hand_hist_created = False

cap = cv2.VideoCapture(0)

def test_capture():
    assert cap.isOpened()

while cap.isOpened():
    ret, frame = cap.read()
    assert ret

    is_hand_hist_created = True
    hand_hist = hand_histobram(frame)