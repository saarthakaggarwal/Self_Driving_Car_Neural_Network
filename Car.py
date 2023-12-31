import math
import random
import sys
import os
import neat
import pygame
import utils


BORDER_COLOR = (111,112,116) # Color To Crash on Hit

current_generation = 0 

TRACK = utils.scale_image(pygame.image.load("imgs/track.png"), 1)
TRACK_BORDER = utils.scale_image(pygame.image.load("imgs/track-border.png"), 1)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
CAR = utils.scale_image(pygame.image.load("imgs/car.png"), 0.2)
FPS = 60
BORDER_COLOR = (111,112,116)

CAR_SIZE_X = CAR.get_width()    
CAR_SIZE_Y = CAR.get_height()
WIDTH = TRACK.get_width()
HEIGHT = TRACK.get_height()

class Car:

    def __init__(self):
        self.sprite = pygame.image.load('imgs/car.png') 
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.position = [800, 800] 
        self.angle = 0
        self.speed = 2

        self.speed_set = True 

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] 

        self.radars = [] 
        self.drawing_radars = [] 

        self.alive = True 

        self.distance = 0 
        self.time = 0 

    def draw(self, screen):
        utils.blit_rotate_center(screen, self.rotated_sprite, self.position, self.angle) 
        self.draw_radar(screen) 

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, mask):
        car_mask = pygame.mask.from_surface(self.rotated_sprite)
        offset = (int(self.position[0] - 0),int(self.position[1] - 0))
        poi = mask.overlap(car_mask, offset)
        if poi is not None:
            self.alive = False

    def check_radar(self):
        for degree in range(90, 305, 45):
            length = 0
            self.center = self.rotated_sprite.get_rect(topleft = self.position).center
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
            while TRACK.get_at((x, y)) == BORDER_COLOR and length < 300:
                length = length + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
            dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
            self.radars.append([(x, y), dist])
            
    def update(self):
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True
        self.position[0] += self.speed*(-math.cos(self.angle * (math.pi/180)))
        self.position[1] += self.speed*(math.sin(self.angle * (math.pi/180)))

        self.distance += self.speed

        self.check_collision(TRACK_BORDER_MASK)
        self.radars.clear()

        self.check_radar()

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        return self.alive

    def get_reward(self):
        return self.distance / 500

    def rotate_center(self, image, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center = image.get_rect(topleft = self.position).center)
        return rotated_image, new_rect
        