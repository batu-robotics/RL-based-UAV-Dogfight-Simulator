# RL-based Dogfight Simulator
# Developed by, Batuhan ATASOY, Ph.D. Mechatronics Engineering 

import pygame
import random as rn
import math
import matplotlib.pyplot as plt
import numpy as np

from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

fps=60

#%% Environment Class
class Env:
    def __init__(self,dimensions):
        # Initializing Colors
        self.white=(255,255,255)
        self.black=(0,0,0)
        self.red=(255,0,0)
        self.green=(0,255,0)
        self.blue=(0,0,100)
        
        # World Generation
        self.height=dimensions[0]
        self.width=dimensions[1]
        self.trail_set=[]
        
        # World Settings
        pygame.display.set_caption('RL-based Dogfight Simulator')
        self.map=pygame.display.set_mode((self.height,self.width))
        
    def trail(self,pos):
        for i in range(0,len(self.trail_set)-1):
            pygame.draw.line(self.map,self.yel,(self.trail_set[i][0],self.trail_set[i][1]),(self.trail_set[i+1][0],self.trail_set[i+1][1]))
            if self.trail_set.__sizeof__()>30000:
                self.trail_set.pop(0)
            self.trail_set.append(pos)
        
#%% Agent Class
class Player:
    def __init__(self,startpos,robotimg,width):
        
        # Initialization
        #self.m2p=3779.52
        self.m2p=500
        self.k=0
        self.act='Forward'
        
        # Player Positions 
        self.w=width/100
        self.x=startpos[0]
        self.y=startpos[1]
        self.theta=0
        self.vl=0.01*self.m2p
        self.vr=0.01*self.m2p
        self.minspeed=0.02*self.m2p
        self.maxspeed=0.02*self.m2p
        
        self.img=pygame.image.load(robotimg)
        self.rotated=self.img
        self.rect=self.rotated.get_rect(center=(self.x,self.y))
        
    def draw(self,map):
        map.blit(self.rotated,self.rect)
    
    def update(self,event=None):
        
        event=pygame.key.get_pressed()
        
        if event[pygame.K_UP] or action==1:
            self.vl+=0.001*self.m2p
            self.vr+=0.001*self.m2p
            self.k=0
            self.act='Forward'
            
        elif event[pygame.K_DOWN] or action==2:
            self.vl-=0.001*self.m2p
            self.vr-=0.001*self.m2p
            self.k=0
            self.act='Backward'
            
        elif event[pygame.K_LEFT] or action==3:
            self.vl+=0.001*self.m2p
            self.vr-=0.001*self.m2p
            self.k+=0.001*math.pi/180
            self.act='Left'
            
        elif event[pygame.K_RIGHT] or action==4:
            self.vl-=0.001*self.m2p
            self.vr+=0.001*self.m2p
            self.k+=-0.001*math.pi/180
            self.act='Right'
        
        self.x+=((self.vl+self.vr)*0.5)*math.cos(self.theta)*dt
        self.y-=((self.vl+self.vr)*0.5)*math.sin(self.theta)*dt
        #self.theta+=(self.vr-self.vl)/self.w*dt
        self.theta+=self.k
        
        self.rotated=pygame.transform.rotozoom(self.img,math.degrees(self.theta)%360,1)
        self.rect=self.rotated.get_rect(center=(self.x,self.y))
        
        #print('Player=> x={:.2f},y={:.2f},angle={:.2f},action={}'.format(self.x,self.y,math.degrees(self.theta)%360,self.act))
        
    # Obtaining Coordinate Informations
    def get_player_coordinates(self):
        return (self.x,self.y,math.degrees(self.theta)%360)
    
#%% Agent Class
class Enemy:
    def __init__(self,startpos,robotimg,width):
        
        # Initialization
        #self.m2p=3779.52
        self.m2p=500
        self.k=0
        
        # Player Positions 
        self.w=width/100
        self.x=startpos[0]
        self.y=startpos[1]
        self.theta=0
        self.vl=0.01*self.m2p
        self.vr=0.01*self.m2p
        self.minspeed=0.02*self.m2p
        self.maxspeed=0.02*self.m2p
        
        self.img=pygame.image.load(robotimg)
        self.rotated=self.img
        self.rect=self.rotated.get_rect(center=(self.x,self.y))
        self.act=rn.randint(1,4)
        
    def draw(self,map):
        map.blit(self.rotated,self.rect)
    
    def update(self):
        
        self.act=rn.randint(1,4)
        
        if self.act==1:
            self.vl+=0.001*self.m2p
            self.vr+=0.001*self.m2p
            self.k=0
        elif self.act==2:
            self.vl-=0.001*self.m2p
            self.vr-=0.001*self.m2p
            self.k=0
        elif self.act==3:
            self.vl+=0.001*self.m2p
            self.vr-=0.001*self.m2p
            self.k+=0.001*math.pi/180
        elif self.act==4:
            self.vl-=0.001*self.m2p
            self.vr+=0.001*self.m2p
            self.k+=-0.001*math.pi/180
                       
        self.x+=((self.vl+self.vr)*0.5)*math.cos(self.theta)*dt
        self.y-=((self.vl+self.vr)*0.5)*math.sin(self.theta)*dt
        #self.theta+=(self.vr-self.vl)/self.w*dt
        self.theta+=self.k
        
        self.action_dict={1:'Accelerate',2:'Decelerate',3:'Left',4:'Right'}
              
        self.rotated=pygame.transform.rotozoom(self.img,math.degrees(self.theta)%360,1)
        self.rect=self.rotated.get_rect(center=(self.x,self.y))
     
        #print('Enemy=> x={:.2f},y={:.2f},angle={:.2f},action={}'.format(self.x,self.y,math.degrees(self.theta)%360,self.action_dict[self.act]))
        
    # Obtaining Coordinate Informations
    def get_enemy_coordinates(self):
        return (self.x,self.y,math.degrees(self.theta)%360)
    
#%% DQL Agent Design
class DQLAgent:
    def __init__(self):
        #Parameter Initializations
        
        self.state_size=3 # Position-x, position-y, heading angle
        self.action_size=4 # Accelerate, Decelerate, Left, Rgiht
        
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
            return rn.randrange(self.action_size) #env.action_space.sample()
    
        act_values=self.model.predict(state)
        return np.argmax(act_values[0])
    
    def replay(self,batch_size):
        
        if len(self.memory)<batch_size:
            return
        
        minibatch=rn.sample(self.memory,batch_size)
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
# class Env:
#     def __init__(self,dimensions):
#         # Initializing Colors
#         self.white=(255,255,255)
#         self.black=(0,0,0)
#         self.red=(255,0,0)
#         self.green=(0,255,0)
#         self.blue=(0,0,100)
        
#         # World Generation
#         self.height=dimensions[0]
#         self.width=dimensions[1]
#         self.trail_set=[]
        
#         self.reward=0
#         self.done=False
#         self.total_reward=0
#         self.start1=(rn.randint(300,600),rn.randint(300,600))
#         self.start2=(rn.randint(300,600),rn.randint(300,600))
#         self.player_img='player.png'
#         self.enemy_img='enemy.png'
        
#         # Agent and Enemy
#         self.player=Player(self.start1, self.player_img, 100*rn.random())
#         self.enemy=Enemy(self.start2, self.enemy_img, 100*rn.random()-200)
#         self.agent=DQLAgent()
        
#         # World Settings
#         pygame.display.set_caption('RL-based Dogfight Simulator')
#         self.map=pygame.display.set_mode((self.height,self.width))

#     # def trail(self,pos):
#     #     for i in range(0,len(self.trail_set)-1):
#     #         pygame.draw.line(self.map,self.yel,(self.trail_set[i][0],self.trail_set[i][1]),(self.trail_set[i+1][0],self.trail_set[i+1][1]))
#     #         if self.trail_set.__sizeof__()>30000:
#     #             self.trail_set.pop(0)
#     #         self.trail_set.append(pos)
        
#     def find_distance(self,a,b):
#         return a-b
    
#     def step(self,action):
#         state_list=[]
        
#         #Update
#         self.player.update(action)
#         self.enemy.update()
        
#         # Get Coordinates
#         next_player_state=self.player.get_player_coordinates()
#         next_enemy_state=self.enemy.get_enemy_coordinates()
        
#         # Finding the Distance between Them
#         state_list.append(self.find_distance(next_player_state[0],next_enemy_state[0]))
#         state_list.append(self.find_distance(next_player_state[1],next_enemy_state[1]))
#         state_list.append(self.find_distance(next_player_state[2],next_enemy_state[2]))
        
#         return [state_list]
    
#     def initialStates(self):
        
#         self.start1=(rn.randint(300,600),rn.randint(300,600))
#         self.start2=(rn.randint(300,600),rn.randint(300,600))

#         self.player=Player(self.start1,'player.png', 100*rn.random())
#         self.enemy=Enemy(self.start2,'enemy.png', 100*rn.random()-200)
        
#         self.reward=0
#         self.done=False
#         self.total_reward=0
    
#         state_list=[]
        
#         # Get Coordinates
#         player_state=self.player.get_player_coordinates()
#         enemy_state=self.enemy.get_enemy_coordinates()

#         # Finding the Distance between Them
#         state_list.append(self.find_distance(player_state[0],enemy_state[0]))
#         state_list.append(self.find_distance(player_state[1],enemy_state[1]))
#         state_list.append(self.find_distance(player_state[2],enemy_state[2]))
        
#         return [state_list]
    
#     def run(self):
#         running=True
#         batch_size=16
        
#         state=self.initialStates()
        
        
#         distance=[0]
        
#         while running:
#             # keep loop running at the right speed
#             clock.tick(fps)
            
#             player_state=self.player.get_player_coordinates()
#             enemy_state=self.enemy.get_enemy_coordinates()
            
#             metric_distance=((player_state[0]-enemy_state[0])**2+(player_state[1]-enemy_state[1])**2)**0.5

            
#             self.reward=float('{:.0f}'.format(-metric_distance))
#             distance.append(metric_distance)
            
#             # process input
#             # for event in pygame.event.get():
#             #     if event.type==pygame.QUIT:
#             #         running=False
                    
#             # Update
#             action=self.agent.act(state)
#             next_state=self.step(action)
#             self.total_reward+=self.reward  
            
#             self.lasttime=pygame.time.get_ticks()
#             self.time=(pygame.time.get_ticks()-self.lasttime)/1000  
            
#             # Hit Check
#             if metric_distance==0:
#                 self.reward=-150
#                 self.total_reward+=self.reward
#                 self.done=True
#                 running=False
#                 print('Episode ended because of collision.')
#                 print('Total Reward=> {}'.format(self.total_reward))

#             if distance[-2]>distance[-1]:
#                 self.reward=1
#                 self.total_reward+=self.reward
#                 self.done=False
#                 running=False
                
#             if metric_distance>100:
#                 self.reward=-150
#                 self.total_reward+=self.reward
#                 self.done=False
#                 running=False
#                 print('Episode ended because the agent is too far away.')
#                 print('Total Reward=> {}'.format(self.total_reward))
               
#             if player_state[1]-enemy_state[1]<10:
#                 self.reward=300
#                 self.total_reward+=self.reward
#                 self.done=True
#                 running=False
#                 print('Episode ended succesfully.')
#                 print('Total Reward=> {}'.format(self.total_reward))
            
#             self.agent.remember(state,action,self.reward,next_state,self.done)
            
#             # Update State
#             state=next_state
            
#             # Training Agent
#             self.agent.replay(batch_size)
            
#             # Epsilon-greedy
#             self.agent.adaptiveEGreedy()
            
#             # draw/show
#             # screen.fill(white)
#             # self.player.draw(screen)
#             # self.enemy.draw(screen)
            
#             # after drawing, flip display
#             # pygame.display.flip()
            
#             #pygame.display.update()
#             #env.map.fill(env.white)
#             #self.player.draw(env.map)
#             #self.enemy.draw(env.map)
#             # env.trail((player.x,player.y))
            
#             #print('Distance={:.3f},Reward={:.1f}'.format(distance[-1],self.total_reward))
                    
#     pygame.quit()
        
#%% Main Program
      
if __name__=='__main__': 
    tot_reward=[]
    tot_reward_100=[]
    t=0
    
    # Robot Initialization
    pygame.init()
    
    # Start Position
    horizontal=1000
    vertical=600
    
    # Time Interval
    dt=0
    lasttime=pygame.time.get_ticks()
    
    start1=(rn.randint(300,600),rn.randint(300,600))
    start2=(rn.randint(300,600),rn.randint(300,600))
    
    dims=(horizontal,vertical)
    
    # Simulation Process => Default: True
    running=True
    
    # Hiring environment class
    env=Env(dims)
    
    # Hiring Player Class
    player=Player(start1,'player.png', 0.01*1000)
    enemy=Enemy(start2,'enemy.png', 0.01*1000)
    
    # Main Loop
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        
        action=rn.randint(1,4)
        player.update(event)
        enemy.update()
        
        dt=(pygame.time.get_ticks()-lasttime)/1000        
        lasttime=pygame.time.get_ticks()
        pygame.display.update()
        env.map.fill(env.white)
        player.draw(env.map)
        enemy.draw(env.map)
        env.trail((player.x,player.y))
        
    pygame.quit()
    
    
# if __name__=='__main__':
#     horizontal=400
#     vertical=400
#     dims=(horizontal,vertical)
#     env=Env(dims)
#     tot_reward=[]
#     tot_reward_100=[]
#     t=0
    
    
#     while True:
#         t+=1
#         print('Episode=>',t)
#         tot_reward.append(env.total_reward)
#         if t%10==0:
#             tot_reward_100.append(env.total_reward)
    
#         lasttime=pygame.time.get_ticks()
#         dt=(pygame.time.get_ticks()-lasttime)/1000        
        
#         #pygame.display.update()
#         #env.map.fill(env.white)
#         #player.draw(env.map)
#         #enemy.draw(env.map)
#         # env.trail((player.x,player.y))
        
#         clock=pygame.time.Clock()
        
#         env.run()