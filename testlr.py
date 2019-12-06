import unittest
# import pytest
import numpy as np
import cv2
import time
import tracking as track
import jianzi as jz
import pygame
from pygame.locals import *


# initialize global variables for tracking
hand_hist = None  # histogram generated from hand sample
size = 9  # number of rectangles
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
traverse_point = []
k = True
max_cnt = None

# initialize size and global variables for ball
WIDTH = 1000
HEIGHT = 750
ball_vel = [0, 0]
ball_x = 0
score = 0
dist = -1
rec = None
image = None
img_radius = 0

# initialize screen and bounding box coordinates
initBB = None
screen = None
cam = None

class TestStringMethods(unittest.TestCase):
    jz.screen_init()
    # print(pygame.display.get_caption())
    # print(pygame.display.get_active())

    def test_screen(self):
        self.assertEqual(pygame.display.get_caption()[0], "Play Balls!")
        self.assertTrue(pygame.display.get_active())

if __name__ == '__main__':
    unittest.main()
