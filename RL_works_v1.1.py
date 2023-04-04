# RL-based Dogfight Simulator
# developed by: Batuhan ATASOY, Ph.D. Mechatronics Engineering

import pygame
import random
import math as m
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

#%% Dims and FPS Inputs
width=700
height=700
fps=60

white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
green=(0,255,0)
blue=(0,0,255)

#%% Enemy Sprite
class Enemy(pygame.sprite.Sprite):
    
    #%% Initializing
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("enemy.png")
        self.rect=self.image.get_rect()
        #self.rect.center=(100,100) # for checking the algorithm
        self.rect.center=(random.randint(0,width),random.randint(0,height))
        self.radius=10
        pygame.draw.circle(self.image,red,self.rect.center,self.radius)

        #%% Dabin's aircraft in 2D
        self.r_speed=5*random.random()
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
        # self.r_speed=5*rn.random()
        # self.angle=100*rn.random()-50
        
        self.r_speed=0
        self.angle=0
        
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
        
        # print('Angle={:.2f},x={:.2f},y={:.2f}'.format(self.angle,self.rect.x,self.rect.y))
        
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
        
    #%% Obtaining Coordinate Informations
    def get_enemy_coordinates(self):
        #print('Enemy Info=> Angle={:.2f},x={:.2f},y={:.2f}'.format(self.angle,self.rect.x,self.rect.y))
        return (self.rect.x,self.rect.y)

#%% Player Sprite
class Player(pygame.sprite.Sprite):
    
     #%% Initializing
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("player.png")
        self.rect=self.image.get_rect()
        self.rect.center=(random.randint(0,width),random.randint(0,height))
        self.rect.center=(width/2,height)
        self.radius=10
        pygame.draw.circle(self.image,red,self.rect.center,self.radius)

        #%% Dabin's aircraft in 2D
        self.r_speed=5*random.random()
        # self.angle=90*rn.random()-45
        self.angle=0
        self.init_angle=0

        self.x_speed=0
        self.y_speed=0 
        
    # #%% Rotating the Frame
    # def rotate(self,image,angle):
    #     self.rotated_image=pygame.transform.rotozoom(self.image,self.angle,1)
    #     self.rotated_rect=self.rotated_image.get_rect(self.rotated_rect.x,self.rotated_rect.y)
        
    def update(self,action):        
        self.speedx=0
        self.speedy=0
        
        key_action=pygame.key.get_pressed()
        
        if key_action[pygame.K_LEFT] or action==1:
            self.speedx+=-10
            self.angle=45
            #print('Action: Left')

        elif key_action[pygame.K_RIGHT] or action==2:
            self.speedx+=10
            self.angle=-45
            #print('Action: Right')
            
        elif key_action[pygame.K_UP] or action==3:
            self.speedy+=-10
            #print('Action: Up')

        elif key_action[pygame.K_DOWN] or action==4:
            self.speedy+=10
            #print('Action: Down')
        
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        #%% Frame Rotation
        self.init_angle+=self.angle
        
        # #%% Rotating the Frame
        # def rotate(self,image,angle):
        #     self.rotated_image=pygame.transform.rotozoom(self.image,self.angle,1)
        #     self.rotated_rect=self.image.get_rect(self.rect.x,self.rect.y)
        #     return self.rotated_image,self.rotated_rect
        
        #self.image,self.rect=rotate(self,self.image,self.angle)
        
        #print('Angle={:.2f},x={:.2f},y={:.2f}'.format(self.angle,self.rect.x,self.rect.y))
        
        #%% Generating Geometric Constraints        
        # if self.rect.bottom>height-20:
        #     #self.angle=-self.angle
        #     print('------------------------')
        #     self.rect.bottom=height-20

        # elif self.rect.top<0:
        #     #self.angle=-self.angle
        #     print('------------------------')
        #     self.rect.top=0
            
        # elif self.rect.left<0:
        #     #self.angle=-self.angle
        #     print('------------------------')
        #     self.rect.left=0

        # elif self.rect.right>width-20:
        #     #self.angle=-self.angle 
        #     print('------------------------')
        #     self.rect.right=width-20

    #%% Obtaining Coordinate Informations
    def get_player_coordinates(self):
        #print('Player Info=> Angle={:.2f},x={:.2f},y={:.2f}'.format(self.angle,self.rect.x,self.rect.y))
        return (self.rect.x,self.rect.y)

#%% DQL Agent Design
class DQLAgent:
    def __init__(self):
        #Parameter Initializations
        
        self.state_size=2
        self.action_size=4
        
        self.gamma=0.95
        self.learning_rate=0.001
        
        self.epsilon=1
        self.epsilon_decay=0.001
        self.epsilon_min=0.01
        
        self.memory=deque(maxlen=1000)
        
        self.model=self.build_model()
        
    def build_model(self):
        model=Sequential()
        model.add(Dense(32,input_dim=self.state_size,activation='relu'))
        model.add(Dense(32,input_dim=32,activation='relu'))
        model.add(Dense(16,input_dim=32,activation='relu'))
        model.add(Dense(16,input_dim=16,activation='relu'))
        model.add(Dense(8,input_dim=16,activation='relu'))
        model.add(Dense(self.action_size,input_dim=8,activation='linear'))
        model.compile(loss='mse',optimizer=Adam(lr=self.learning_rate))
        
        return model
    
    def remember(self,state,action,reward,next_state,done):
        #Storage
        self.memory.append((state,action,reward,next_state,done))
    
    def act(self,state):
        state=np.array(state)
        
        if np.random.rand()<=self.epsilon:
            return random.randrange(self.action_size) #env.action_space.sample()
    
        act_values=self.model.predict(state)
        return np.argmax(act_values[0])
    
    def replay(self,batch_size):
        
        if len(self.memory)<batch_size:
            return
        
        minibatch=random.sample(self.memory,batch_size)
        for state,action,reward,next_state,done in minibatch:
            state=np.array(state)
            next_state=np.array(next_state)
            if done:
                target=reward
            else:
                target=reward+self.gamma*np.amax(self.model.predict(next_state)[0])
                
            train_target=self.model.predict(state)
            train_target[0][action]=target
            self.model.fit(state,train_target,verbose=0)
            
    def adaptiveEGreedy(self):
        if self.epsilon>self.epsilon_min:
            self.epsilon*=self.epsilon_decay
             
#%% Environment Design
class Env(pygame.sprite.Sprite):
    def __init__(self):
        #%% Sprite Group
        pygame.sprite.Sprite.__init__(self)
        self.player=pygame.sprite.Group()
        self.enemy=pygame.sprite.Group()
        
        self.player1=Player()
        self.player2=Enemy()
        self.player.add(self.player1)
        self.enemy.add(self.player2)
        
        self.reward=0
        self.done=False
        self.total_reward=0
        self.agent=DQLAgent()
        
    def find_distance(self,a,b):
        return a-b
    
    def step(self,action):
        state_list=[]
        
        #Update
        self.player1.update(action)
        self.enemy.update()
        
        # Get Coordinates
        next_player_state=self.player1.get_player_coordinates()
        next_enemy_state=self.player2.get_enemy_coordinates()
        
        # Finding the Distance between Them
        state_list.append(self.find_distance(next_player_state[0],next_enemy_state[0]))
        state_list.append(self.find_distance(next_player_state[1],next_enemy_state[1]))
        
        return [state_list]
    
    def initialStates(self):
        #%% Sprite Group
        pygame.sprite.Sprite.__init__(self)
        self.player=pygame.sprite.Group()
        self.enemy=pygame.sprite.Group()
        
        self.player1=Player()
        self.player2=Enemy()
        self.player.add(self.player1)
        self.enemy.add(self.player2)
        
        self.reward=0
        self.done=False
        self.total_reward=0
    
        state_list=[]
        
        # Get Coordinates
        player_state=self.player1.get_player_coordinates()
        enemy_state=self.player2.get_enemy_coordinates()

        # Finding the Distance between Them
        state_list.append(self.find_distance(player_state[0],enemy_state[0]))
        state_list.append(self.find_distance(player_state[1],enemy_state[1]))
        
        return [state_list]
    
    def run(self):
        running=True
        batch_size=16
        
        state=self.initialStates()
        
        
        distance=[0]
        
        while running:
            # keep loop running at the right speed
            clock.tick(fps)
            
            player_state=self.player1.get_player_coordinates()
            enemy_state=self.player2.get_enemy_coordinates()
            
            metric_distance=((player_state[0]-enemy_state[0])**2+(player_state[1]-enemy_state[1])**2)**0.5

            
            self.reward=float('{:.0f}'.format(-metric_distance))
            distance.append(metric_distance)
            
            # process input
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                    
            # Update
            action=self.agent.act(state)
            next_state=self.step(action)
            self.total_reward+=self.reward  
            
            # Hit Check
            hit=pygame.sprite.spritecollide(self.player1,self.enemy, False, pygame.sprite.collide_circle)
            
            if hit:
                self.reward=-150
                self.total_reward+=self.reward
                self.done=True
                running=False
                print('Episode ended because of collision.')
                print('Total Reward=> {}'.format(self.total_reward))

                        
            if distance[-2]>distance[-1]:
                self.reward=1
                self.total_reward+=self.reward
                self.done=False
                running=False
                
            if metric_distance>100:
                self.reward=-150
                self.total_reward+=self.reward
                self.done=False
                running=False
                print('Episode ended because the agent is too far away.')
                print('Total Reward=> {}'.format(self.total_reward))
               
            if player_state[1]-enemy_state[1]<10:
                self.reward=300
                self.total_reward+=self.reward
                self.done=True
                running=False
                print('Episode ended succesfully.')
                print('Total Reward=> {}'.format(self.total_reward))
            
            self.agent.remember(state,action,self.reward,next_state,self.done)
            
            # Update State
            state=next_state
            
            # Training Agent
            self.agent.replay(batch_size)
            
            # Epsilon-greedy
            self.agent.adaptiveEGreedy()
            
            # draw/show
            # screen.fill(white)
            # self.player.draw(screen)
            # self.enemy.draw(screen)
            
            # after drawing, flip display
            # pygame.display.flip()
                    
        pygame.quit()

#%% Initializing Pygame Environment
if __name__=='__main__':
    env=Env()
    tot_reward=[]
    tot_reward_100=[]
    t=0
    
    while True:
        t+=1
        print('Episode=>',t)
        tot_reward.append(env.total_reward)
        if t%10==0:
            tot_reward_100.append(env.total_reward)

        pygame.init()
        screen=pygame.display.set_mode((width,height))
        pygame.display.set_caption('AI-based Dogfight Simulator')
        clock=pygame.time.Clock()
        
        env.run()
        
        


