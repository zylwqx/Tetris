import pygame
import time
import functools
from math import sqrt, floor
import random

import os
ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets/')

# Colours
BK = (0, 0, 0)
W = (255, 255, 255)
PY = (253, 253, 150)
PB = (167, 199, 231)
R = (160,80,85)
G = (20,190,80)


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))

# Input (A: game input, UI: UI input)
#pygame.key.set_repeat(1,1000//tps*player_move)
keybinds = {
        "A_LEFT": (pygame.K_LEFT, pygame.K_a),
        "A_RIGHT": (pygame.K_RIGHT, pygame.K_d),
        "A_DOWN": (pygame.K_DOWN, pygame.K_s),
        "A_UP": (pygame.K_UP, pygame.K_w),
        "UI_SELECT": (pygame.K_SPACE, pygame.K_RETURN),
        "UI_CANCEL": [pygame.K_ESCAPE],
}

held_keys_duration = {}


class Input:
    # Get dict of bound keys
    @staticmethod
    def get_keybinds():
        return keybinds

    # From keybinds
    @staticmethod
    def is_pressed(action):
        if action in keybinds:
            pressed = pygame.key.get_pressed()
            return any(
                    [pressed[key]
                     for key in keybinds[action]])
        return None

    @staticmethod
    def is_key_held(key):
        return key in held_keys_duration and held_keys_duration[key] > 0

    @staticmethod
    def is_just_pressed(action):
        if Input.is_pressed(action):
            '''
            Checks if any key bound to the action is
            currently held down and wasn't held in the previous frame
            '''
            if any(map(
                lambda key: key in held_keys_duration and held_keys_duration[key] == 0,
                keybinds[action])):
                return True
        return False

    @staticmethod
    def is_held(action):
        if action in keybinds:
            if any(map(
                lambda x: Input.is_key_held(x),
                keybinds[action])):
                return True
        return False

    @staticmethod
    def get_held(action):
        if action in keybinds:
            durations = set()
            for key in keybinds[action]:
                if Input.is_key_held(key):
                    durations.add(held_keys_duration[key])
            if durations:
                return max(durations)
        return 0

    # Quicker than get_pressed, returns true if any in actions are pressed
    @staticmethod
    def any_pressed(*actions):
        return any(map(Input.is_pressed, actions))

    # returns list of pressed actions
    @staticmethod
    def get_pressed(*actions):
        pressed = set()
        for action in actions:
            if Input.is_pressed(action):
                pressed.append(action)
        return pressed


#----------------------------------->

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
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value

    @property
    def magnitude(self):
        return sqrt(self._x**2+self._y**2)
    
    @magnitude.setter
    def magnitude(self, value):
        new_vector = self.normalise()*value
        self.x = new_vector.x
        self.y = new_vector.y

    def normalise(self):
        root = self.magnitude
        if root == 0:
            return Vector2(0,0)
        x = self._x/root
        y = self._y/root
        return Vector2(x,y)

    @staticmethod
    def average(*vectors):
        return Vector2.sum(vectors)*0.5

    def __equals__(self, v2: "Vector2"):
        return self.x == v2.x and self.y == v2.y

    def __add__(self, v2: "Vector2"):
        x = self._x + v2.x
        y = self._y + v2.y

        return Vector2(x,y)

    def __sub__(self, v2: "Vector2"):
        x = self._x - v2.x
        y = self._y - v2.y

        return Vector2(x,y)

    def sum(vectors):
        return Vector2(sum((vec.x for vec in vectors)),sum((vec.y for vec in vectors)))

    def __mul__(self, scalar: int):
        x = self._x*scalar 
        y = self._y*scalar 

        return Vector2(x,y)

    def __mod__(self, mod):
        if type(mod) == Vector2:
            return Vector2(self.x%mod.x, self.y%mod.y)
        elif type(mod) == int:
            temp = self.copy()
            temp.magnitude = temp.magnitude%mod
            return temp
        else:
            raise TypeError("__mod__ expected mod value to be of type (Vector2) or (int), not "+str(type(mod)))

    def __str__(self):
        return f"({self._x},{self._y})"

    def __iter__(self):
        return iter((self._x,self._y))

    def __getitem__(self, index):
        return self._y if index%2 else self._x



    def copy(self):
        return Vector2(self._x,self._y)


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


class LootTableItem:
    def __init__(self, value, weight):
        self.item = value
        self.weight = float(weight)


class LootTable:
    def __init__(self, *args: LootTableItem):
        self.table =  args

        self.total_weight = 0
        self.cumululative_weights = []
    	
        for item in self.table:
            self.total_weight += item.weight
            self.cumululative_weights.append([item.item,self.total_weight])

    def random_item(self):
    	chance_roll = random.uniform(0,self.total_weight)
    	for weight in self.cumululative_weights:
    		if chance_roll < weight[1]:
    			return weight[0]
    	
    	return None

#https://www.pygame.org/wiki/Spritesheet
class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except (pygame.error) as message:
            print('Unable to load spritesheet image:', filename)
            raise SystemExit(message)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]

    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


class Tween:
    def __init__(self, start, end, fps=1, as_tuple=False): # Frames Per Unit
        self._start = start
        self._end = end
        self.length = self._end-self._start
        self.angle = self.length.normalise()

        self.fps = fps
        self.frames = self.length.magnitude//self.angle.magnitude/fps

        self.as_tuple = as_tuple

    def update(self):
        print(self.start)
        self.length = self.end-self.start
        self.angle = self.length.normalise()
        self.frames = self.length.magnitude//self.angle.magnitude/self.fps

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def end(self):
        return self._end
    @end.setter
    def end(self, value):
        self._end = value

    def update_values(self, start=None, end=None, fps=None, as_tuple=False):
        if start != None:
            self.start = start
        if end != None:
            self.end = end
        if fps != None:
            self.fps = fps
        if as_tuple != None:
            self.as_tuple = as_tuple
        update()

    def __getitem__(self, index):
        if index < 0:
            index = self.frames + index
        new = self.angle*index*self.fps
        if new.magnitude > self.length.magnitude:
            new = self.end-new%self.length
        else:
            new = self.start+new
        if self.as_tuple:
            new = tuple(new)
        return new
    
    def __len__(self):
        return int(self.frames)


class Animation:
    PAUSED = -2
    FINISHED = -1
    STOPPED = 0
    PLAYING = 1
    def __init__(self, obj, attribute: str, frames: "list or Tween", fps, loop=False):
        self.obj = obj
        self.attr = attribute
        self.frames = frames
        self.fps = fps

        self.curr_frame = 0
        self.loop = loop

        self.playing = False

        self.total_length = len(self.frames)/self.fps
        self.curr_time = 0
        self.status = Animation.STOPPED

    def play(self):
        self.playing = True
        self.status = Animation.PLAYING

        rsetattr(self.obj, self.attr, self.frames[self.curr_frame])
        print(len(self.frames))

    def pause(self):
        self.playing = False
        self.status = Animation.PAUSED

    def stop(self):
        self.playing = False
        self.status = Animation.STOPPED
        self.reset()

    def reset(self, show_change=False):
        self.curr_frame = 0
        self.curr_time = 0

        if show_change:
            rsetattr(self.obj, self.attr, self.frames[self.curr_frame])

    def update(self, delta_t, window):
        if not self.playing:
            if self.status == Animation.FINISHED:
                self.status = self.STOPPED
            return self.status

        self.curr_time += delta_t
        new_frame = floor(self.fps*self.curr_time)
        
        if new_frame != self.curr_frame:
            self.curr_frame = min(len(self.frames),new_frame)
            if self.curr_frame >= len(self.frames):
                if self.loop:
                    self.reset()
                else:
                    self.stop()
                    self.status = Animation.FINISHED
                    return self.status
            rsetattr(self.obj, self.attr, self.frames[self.curr_frame])

        return self.status


