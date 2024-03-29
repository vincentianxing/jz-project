import random
import pygame
from pygame.locals import *
import cv2
import numpy as np
import sys

#colors
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0,0,0)

#globals
WIDTH = 600
HEIGHT = 400      
BALL_RADIUS = 20
ball_pos = [0,0]
ball_vel = [0,0]
score = 0

#canvas declaration
camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("Play Balls!")
screen = pygame.display.set_mode([WIDTH,HEIGHT])
image = pygame.image.load('jianzi.png')
print(image.get_rect().size)

def ball_init():
    global ball_pos, ball_vel # these are vectors stored as lists
    ball_pos = [300,100]
    horz = int(random.randrange(0,4))
    vert = 0
    
    ball_vel = [horz, vert]

# define event handlers
def init():
    global score  # these are floats
    score = 0
    ball_init()

def draw(canvas):
    global ball_pos, ball_vel, score

    ball_vel[1] += 0.981
    #update ball
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    #draw ball
    pygame.draw.circle(canvas, RED, ball_pos, 20, 0)

    #ball collision check on top and bottom walls
    if int(ball_pos[1]) <= BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]
    if int(ball_pos[0]) <= BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]
    if int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]
    
    #ball collison check on gutters or paddles
    #if int(ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
    #    ball_vel[1] = -ball_vel[1]
        #ball_vel[0] *= 1.1
        #ball_vel[1] *= 1.1
        #score += 1
    #if int(ball_pos[1]) >= y + BALL_RADIUS:
    #    ball_vel[1] = -ball_vel[1]

    if int(ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
        ball_vel[1] *= -1
        if int(ball_vel[1]) == 0:
            ball_init()
    #    ball_init()

    #update scores
    myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    label = myfont1.render("Score "+str(score), 1, (255,255,0))
    canvas.blit(label, (50,20)) 

init()


try:
    while True:

        ret, frame = camera.read()
		
        screen.fill([0,0,0])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame.swapaxes(0, 1)
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0,0))
        draw(screen)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN:
                sys.exit(0)
except(KeyboardInterrupt,SystemExit):
    pygame.quit()
    cv2.destroyAllWindows()