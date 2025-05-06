import pygame
import time
from math import sqrt
import random


class Group(list):
    def  __init__(self,*args):
        super().__init__(arg for arg in args)

        self.remove_queue = []

    def remove(self,item):
        self.remove_queue.append(item)

    def clear(self):
        self.remove_queue.clear()
        super().clear()

    def update(self):
        if self.remove_queue:
            for item in self.remove_queue:
                super().remove(item)
        self.remove_queue = []


class Vector2:
    def __init__(self, x=0, y=0, point=None):
        if point != None:
            x = point[0]
            y = point[1]
        self.x = x
        self.y = y

    def normalise(self):
        root = sqrt(self.x**2+self.y**2)
        if root == 0:
            return Vector2(0,0)
        x = self.x/root
        y = self.y/root
        return Vector2(x,y)

    @staticmethod
    def average(*vectors):
        return Vector2.sum(vectors)*0.5

    def __add__(self, v2: "Vector2"):
        x = self.x + v2.x
        y = self.y + v2.y

        return Vector2(x,y)

    def sum(vectors):
        return Vector2(sum((vec.x for vec in vectors)),sum((vec.y for vec in vectors)))

    def __mul__(self, scalar: int):
        x = self.x*scalar 
        y = self.y*scalar 

        return Vector2(x,y)

    def __str__(self):
        return f"({self.x},{self.y})"

    def __iter__(self):
        return iter((self.x,self.y))

    def __getitem__(self, index):
        return self.y if index%2 else self.x


class Raycast:
    def __init__(self, direction: Vector2, length: int):
        self.direction = direction.normalise()
        self.length = length

    def cast(self, position: Vector2, *colliders: "RectList"):
        collided = []
        for rect in colliders:
            pos_2 = position+self.direction*self.length
            collide_line = rect.clipline(
                    (position.x,position.y),
                    (pos_2.x,pos_2.y))
            if len(collide_line) > 0:
                p = collide_line[0]
                p2 = collide_line[1]
                d = sqrt((p2[1]-p[1])**2+(p2[0]-p[0])**2)
                collided.append(
                        {"rect":rect,
                         "distance": d})
                
        return collided


class Progressbar:
    def __init__(self,
                 rect,
                 direction: Vector2,
                 maximum,
                 back_colour=(0,0,0),
                 fore_colour=(255,0,0)):

        self.rect = rect
        self.bar = pygame.Surface((rect.width,rect.height))
        self.bar.set_alpha(180)

        self.direction = direction

        prog_start_x = max(0,-rect.width*direction.x)
        prog_start_y = max(0,-rect.height*direction.y)
        self.prog_start_width = rect.width*abs(direction.y)
        self.prog_start_height = rect.height*abs(direction.x)

        self.progress_rect = pygame.Rect(prog_start_x,prog_start_y,
                                         self.prog_start_width, self.prog_start_height)

        self.back_colour = back_colour
        self.fore_colour = fore_colour

        self.maximum = maximum
        self.value = 0
        self.increment_x = self.rect.width/maximum*direction.x
        self.increment_y = self.rect.height/maximum*direction.y

    def progress_update(self):
        if self.direction.x:
            self.progress_rect.width = round(self.value*self.increment_x)*self.direction.x
        if self.direction.y:
            self.progress_rect.height = round(self.value*self.increment_y)*self.direction.y

    def set(self, amount):
        self.value = min(self.maximum,max(0,amount))
        self.progress_update()

    def increase(self, amount):
        self.set(self.value+amount)

    def decrease(self, amount):
        self.set(self.value-amount)

    def reset(self):
        self.set(0)

    def update(self, window):
        self.bar.fill(self.back_colour)
        pygame.draw.rect(self.bar, self.fore_colour, self.progress_rect)
        window.blit(self.bar,self.rect)

