# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 16:48:08 2021

@author: Batu
"""

import pygame
import random as rn
import math as m

#%% Player Sprite
class Player(pygame.sprite.Sprite):
    
    #%% Initializing
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("player.png")
        self.rect=self.image.get_rect()
        self.rect.center=(width/2,height/2)
        self.radius=2
        pygame.draw.circle(self.image,red,self.rect.center,self.radius)

        #%% Dabin's aircraft in 2D
        self.r_speed=5*rn.random()
        # self.angle=90*rn.random()-45
        self.angle=0
        self.init_angle=0

        self.x_speed=0
        self.y_speed=0 
        
    # #%% Rotating the Frame
    # def rotate(self,image,angle):
    #     self.rotated_image=pygame.transform.rotozoom(self.image,self.angle,1)
    #     self.rotated_rect=self.rotated_image.get_rect(self.rotated_rect.x,self.rotated_rect.y)
        
    def update(self):        
        #%% Dabin's aircraft in 2D
        self.r_speed=5*rn.random()
        self.angle=100*rn.random()-50
        
        self.x_speed=self.r_speed*m.cos(self.angle*m.pi/180)
        self.y_speed=self.r_speed*m.sin(self.angle*m.pi/180)
        
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed

        #%% Frame Rotation
        self.init_angle+=self.angle
        
        # #%% Rotating the Frame
        # def rotate(self,image,angle):
        #     self.rotated_image=pygame.transform.rotozoom(self.image,self.angle,1)
        #     self.rotated_rect=self.image.get_rect(self.rect.x,self.rect.y)
        #     return self.rotated_image,self.rotated_rect
        
        #self.image,self.rect=rotate(self,self.image,self.angle)
        
        print('Angle={:.2f},x={:.2f},y={:.2f}'.format(self.angle,self.rect.x,self.rect.y))
        
                 # Adjusting Geometric Constraints
        if self.rect.left<0 or self.rect.right>width:
            self.x_speed=-self.x_speed
            
        elif self.rect.top<0 or self.rect.bottom>height:
            self.y_speed=-self.y_speed

        #%% Generating Geometric Constraints        
        # if self.rect.bottom>height-20:
        #     #self.angle=-self.angle
        #     print('------------------------')
        #     self.y_speed=-self.y_speed
        #     self.rect.y += self.y_speed

        # elif self.rect.top<0:
        #     #self.angle=-self.angle
        #     print('------------------------')
        #     self.y_speed=-self.y_speed
        #     self.rect.y += self.y_speed

        # elif self.rect.left<0:
        #     #self.angle=-self.angle
        #     print('------------------------')
        #     self.x_speed=-self.x_speed
        #     self.rect.x += self.x_speed

        # elif self.rect.right>width-20:
        #     #self.angle=-self.angle 
        #     print('------------------------')
        #     self.x_speed=-self.x_speed
        #     self.rect.x += self.x_speed
    
#%% Dims and FPS Inputs
width=800
height=600
fps=5

white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
green=(0,255,0)
blue=(0,0,255)

#%% Initializing Pygame Environment
pygame.init()
screen=pygame.display.set_mode((width,height))
pygame.display.set_caption('AI-based Dogfight Simulator')
clock=pygame.time.Clock()

#%% Sprite Group
all_sprite=pygame.sprite.Group()
player=Player()
all_sprite.add(player)

#%% Game Loop
running=True

while running:
    # keep loop running at the right speed
    clock.tick(fps)
    
    # process input
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
            
    # update
    all_sprite.update()
    
    # draw/show
    screen.fill(white)
    all_sprite.draw(screen)
    
    # aFter drawing, flip display
    pygame.display.flip()
            
pygame.quit()