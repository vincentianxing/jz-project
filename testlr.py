import unittest
# import pytest
import numpy as np
import cv2
import time
import tracking as track
import jianzi as jz
import pygame
from pygame.locals import *

class TestStringMethods(unittest.TestCase):
    jz.screen_init()

    # check if the screen active
    def test_screen(self):
        self.assertEqual(pygame.display.get_caption()[0], "Play Balls!")
        self.assertTrue(pygame.display.get_active())
    
    # check if the image load right
    def test_img(self):
        self.assertNotEqual(jz.image, None)
        self.assertNotEqual(jz.rec, None)
        self.assertEqual(jz.img_radius, 35)
    
    jz.init()

    def test_score(self):
        self.assertEqual(jz.score, 0)
        self.assertEqual(jz.rec.centery, 1)
    
    jz.update()

    def test_update(self):
        self.assertEqual(jz.score, 1)


if __name__ == '__main__':
    unittest.main()
