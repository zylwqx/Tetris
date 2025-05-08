import pygame
import random
import time
from math import ceil
from utilities import *


pygame.init()


# Settings
wind_size = Vector2(800, 900)

GRID_DIMS = Vector2(10,20)

# Game ticks
tps = 20 
gravity = 15
player_move = 4
player_move_delay = 10

tile_size = wind_size.y/22.5
grid_size = Vector2(tile_size*GRID_DIMS.x, tile_size*GRID_DIMS.y)
square_speed = tile_size

# Colours
BK = (0, 0, 0)
W = (255, 255, 255)
PY = (253, 253, 150)
PB = (167, 199, 231)

# Input (A: game input, UI: UI input)
#pygame.key.set_repeat(1,1000//tps*player_move)
keybinds = {
        "A_LEFT": (pygame.K_LEFT, pygame.K_a),
        "A_RIGHT": (pygame.K_RIGHT, pygame.K_d),
        "A_DOWN": (pygame.K_DOWN, pygame.K_s),
        "A_UP": (pygame.K_UP, pygame.K_w),
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
            return any(
                    [pygame.key.get_pressed()[key]
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

#game grid
grid = pygame.Rect((wind_size.x-grid_size.x)/2, (wind_size.y-grid_size.y)/2,
                    grid_size.x, grid_size.y)


class Tile(pygame.Rect):
    def __init__(self, colour):
        super().__init__(0, 0, tile_size, tile_size)
        self.colour = colour
        self.hide = False
        self.sprite = pygame.image.load("tile.png").convert_alpha()
        self.grid_pos = Vector2(5,0)

    def draw(self, window):
        pygame.draw.rect(window, self.colour, self)
        window.blit(self.sprite, self)

    def update(self, delta_t, window):
        # Set position
        self.topleft = (grid.left+falling_pos.x*tile_size, grid.top+falling_pos.y*tile_size)

        # Collisions
        if falling_pos.x <= 0:
            falling_pos.x = 0
        elif falling_pos.x >= GRID_DIMS.x:
            falling_pos.x = GRID_DIMS.x-1
        if falling_pos.y >= GRID_DIMS.y:
            falling_pos.y = GRID_DIMS.y-1

        if not self.hide:
            self.draw(window)
        

#different pieces
falling_pos = Vector2(5,0)
drop_pos = (grid.left+falling_pos.x*tile_size, grid.top)


def set_window_size(size=None, width=0, height=0):
    global wind_size, tile_size, grid_size, grid, square_speed, square
    if size == None:
        size = (width,height)

    wind_size = Vector2(point=size)

    tile_size = wind_size.y/22.5
    grid_size = Vector2(tile_size*GRID_DIMS.x, tile_size*GRID_DIMS.y)
    square_speed = tile_size

    grid = pygame.Rect((wind_size.x-grid_size.x)/2, (wind_size.y-grid_size.y)/2,
                       grid_size.x, grid_size.y)
    #square = pygame.Rect(falling_pos.x*tile_size+grid.left, falling_pos.y*tile_size+grid.top, tile_size, tile_size)

            #if not set(keybinds[action]).isdisjoint(held_keys_duration):
def main():
    global falling_pos, held_keys

    #display
    window = pygame.display.set_mode(tuple(wind_size), pygame.RESIZABLE)
    falling_pos = Vector2(5,0)
    set_window_size(wind_size)


    #game loop
    running = True

    # Setup
    tps_timer = 0
    g_timer = gravity
    p_timer = player_move

    curr_time = time.time()
    prev_time = curr_time

    Tilee = Tile((255,0,0))
    Tilee.topleft = drop_pos
    while running:
        # Delta time
        delta_t = curr_time - prev_time
        prev_time = curr_time
        curr_time = time.time()

        # Input hold times
        for key in held_keys_duration:
            held_keys_duration[key] += delta_t

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                set_window_size(event.size)
            if event.type == pygame.KEYDOWN:

            # Game Input
                if event.key not in held_keys_duration:
                    held_keys_duration[event.key] = 0
            if event.type == pygame.KEYUP:
                held_keys_duration.pop(event.key)


        tps_timer += delta_t
        if Input.is_just_pressed("A_LEFT"):
            p_timer = player_move_delay
            falling_pos.x -= 1
        if Input.is_just_pressed("A_RIGHT"):# or Input.get_held("A_RIGHT")>p_timer/tps:
            p_timer = player_move_delay
            falling_pos.x += 1
        if Input.is_just_pressed("A_DOWN"):# or Input.get_held("A_DOWN")>p_timer/tps:
            p_timer = player_move_delay
            falling_pos.y += 1
        # Quick drop
        if Input.is_just_pressed("A_UP"):
            falling_pos.y += 100

# current_tiile = Tile(..)
#crrent_tile.fallingpos.x =efhiuefh
#current_tile = nextt tile

        # Handle events
        if tps_timer >= 1/tps:
            tps_timer = 0

            g_timer -= 1
            p_timer -= 1
            if g_timer <= 0:
                g_timer = gravity
                falling_pos.y += 1

            p_timer -= 1
            if p_timer <= 0:
                p_timer = player_move
                if Input.is_held("A_LEFT"):
                    falling_pos.x -= 1
                if Input.is_held("A_RIGHT"):
                    falling_pos.x += 1
                if Input.is_held("A_DOWN"):
                    falling_pos.y += 1
        

        # wall limits
        if falling_pos.x <= 0:
            falling_pos.x = 0
        if falling_pos.x >= GRID_DIMS.x:
            falling_pos.x = GRID_DIMS.x-1
        if falling_pos.y >= GRID_DIMS.y:
            falling_pos.y = GRID_DIMS.y-1

        window.fill(BK)

        # draw grid
        pygame.draw.rect(window, W, grid)
        # draw square
        Tilee.update(delta_t, window)


        pygame.display.update()

    return 0 # All good, exit game

main()