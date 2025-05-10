import pygame
import random
import time
from math import ceil
from utilities import *


pygame.init()


# Settings
wind_size = Vector2(800, 900)

GRID_DIMS = Vector2(10,20)
VIDEO_FLAGS = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE

# Game ticks
tps = 20 
gravity = 15
player_move = 4
player_move_delay = 10
lock_delay = 22
lock_delay_timer = pygame.USEREVENT + 1

# Tile info
tile_size = wind_size.y/22.5
grid_size = Vector2(tile_size*GRID_DIMS.x, tile_size*GRID_DIMS.y)
square_speed = tile_size

# Blocks
SQUARE_LAYOUT = """
11
11
"""

T_LAYOUT = """
010
111
"""
L_LAYOUT = """
010
010
011
"""

LAYOUTS = (SQUARE_LAYOUT,T_LAYOUT,L_LAYOUT)

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
grid_drop_pos = Vector2(5,0)

def grid_pos_to_coord(grid_pos):
    return (grid.left+grid_pos.x*tile_size, grid.top+grid_pos.y*tile_size)


class Tile(pygame.Rect):
    def __init__(self, colour, grid_pos=Vector2(5,0), collision_list=None):
        super().__init__(0, 0, tile_size, tile_size)
        self.sprite = pygame.image.load("tile.png").convert_alpha()
        self.colour = colour
        self.hide = False

        self.collision_list = collision_list

        self.grid_pos = grid_pos
        self.prev_grid_pos = self.grid_pos
        self.falling = True

    def draw(self, window):
        if self.hide:
            return
        pygame.draw.rect(window, self.colour, self)
        window.blit(self.sprite, self)

    def update(self, delta_t, window, redraw=True):
        # Collisions
        # >--------------------->
        
        # Walls
#        if self.grid_pos.x < 0:
#            self.grid_pos.x = 0
#
#        elif self.grid_pos.x >= GRID_DIMS.x:
#            self.grid_pos.x = GRID_DIMS.x-1
#
#        if self.grid_pos.y > GRID_DIMS.y-1:
#            self.grid_pos.y = GRID_DIMS.y-1
#            if self.falling:
#                self.falling = False
#                print("locking")
#                pygame.time.set_timer(lock_delay_timer, int(1000*lock_delay/tps))
#
#        # Tiles
#        test = self.copy()
#        test.topleft = grid_pos_to_coord(self.grid_pos)
#        
#        if self.collision_list and (c:=test.collidelist(self.collision_list)) != -1:
#            print(test.collidelist(self.collision_list))
#            if self.grid_pos.x != self.prev_grid_pos.x:
#                self.grid_pos.x = self.prev_grid_pos.x
#
#            if self.grid_pos.y != self.prev_grid_pos.y:
#                c_y = self.collision_list[c].grid_pos.y
#                if self.prev_grid_pos.y < c_y:
#                    self.grid_pos.y = c_y-1
#                else:
#                    self.grid_pos.y = c_y+1
#                if self.falling:
#                    self.falling = False
#                    print("locking")
#                    pygame.time.set_timer(lock_delay_timer, int(1000*lock_delay/tps))
        # >--------------------->

        # Set position
        prev_pos = self.topleft
        self.prev_grid_pos = self.grid_pos.copy()
        self.topleft = grid_pos_to_coord(self.grid_pos)

        # Uncomment for resetting lock delay if moving
        if not self.falling and self.topleft != prev_pos:
            self.falling = True
            pygame.time.set_timer(lock_delay_timer, 0)


        if redraw:
            self.draw(window)


class TileList(list):
    def __init__(self, *items):
        if not all(type(x) == Tile for x in items):
            raise TypeError("Not all items are of type 'Tile'")
        super().__init__(items)

    def draw(self, window):
        for tile in self:
            tile.draw(window)


class Block:
    def __init__(self, layout, colour, collision_list):
        self.layout = layout
        self.colour = colour

        convert = layout.split()

        self._grid_pos = grid_drop_pos.copy()
        self._grid_pos.x -= len(convert[0])//2

        self._bin_grid_pos = self._grid_pos.copy()
        self.grid_pos_updated = False
        
        self.collision_list = collision_list
        self.falling = True

        self.tiles = []
        self.only_tiles = None

        for row in range(len(convert)):
            if not convert[row].strip():
                continue
            self.tiles.append([])
            for column in range(len(convert[row])):
                if convert[row][column] == '1':
                    drop_pos = self._grid_pos+Vector2(column, row)
                    self.tiles[row].append(
                        Tile(colour, drop_pos, collision_list))
                else:
                    self.tiles[row].append(None)

    def get_tiles_only(self):
        if self.only_tiles:
            return self.only_tiles
        self.only_tiles = []

        # Merge tiles
        for row in self.tiles:
            self.only_tiles.extend(row)
        self.only_tiles = list(filter(lambda x: x is not None,self.only_tiles))
        return self.only_tiles


    @property
    def grid_pos(self):
        self.grid_pos_updated = True
        self._bin_grid_pos = self._grid_pos.copy()
        return self._bin_grid_pos

    @grid_pos.setter
    def grid_pos(self, new_value):
        print()
        displacement = new_value-self._grid_pos
        move_hor = True if displacement.x else False
        move_ver = True if displacement.y else False

        if not (move_hor or move_ver):
            return

        dx = 0 if displacement.x < 0 else -1

        for row in range(len(self.tiles)):
            r = list(filter(lambda x: x is not None, self.tiles[row]))

            if move_hor:
                if 0 <= r[dx].grid_pos.x+displacement.x <= GRID_DIMS.x-1:
                    test = r[dx].copy()
                    test.left = grid_pos_to_coord(
                            r[dx].grid_pos+Vector2(displacement.x,0))[0]
                    if test.collidelist(self.collision_list) != -1:
                        move_hor = False
                else:
                    move_hor = False


            if not ((row == 0 or row == len(self.tiles)-1) and move_ver):
                continue
            for tile in r:
                if not 0 <= tile.grid_pos.y+displacement.y <= GRID_DIMS.y-1:
                    move_ver = False
                    if self.falling:
                        self.falling = False
                        print("locking")
                        pygame.time.set_timer(lock_delay_timer, int(1000*lock_delay/tps))
                    break
                test = tile.copy()
                test.top = grid_pos_to_coord(
                        tile.grid_pos+Vector2(0, displacement.y))[1]
                if test.collidelist(self.collision_list) != -1:
                    move_ver = False
                    if self.falling:
                        self.falling = False
                        print("locking")
                        pygame.time.set_timer(lock_delay_timer, int(1000*lock_delay/tps))
                    break

        if not (move_hor or move_ver):
            return

        self._grid_pos += displacement
        for tile in self.get_tiles_only():
            tile.grid_pos += displacement

    def update(self, delta_t, window, redraw=True):
        if self.grid_pos_updated:
            self.grid_pos_updated = False
            print ("bin "+ str(self._bin_grid_pos))
            self.grid_pos = self._bin_grid_pos
        for tile in self.get_tiles_only():
            tile.update(delta_t,window,redraw)


def block_factory(layout, collision_list):
    return Block(layout, [random.randint(0,255) for i in range(3)], collision_list)

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
    master_window = pygame.display.set_mode(tuple(wind_size), VIDEO_FLAGS)
    window = master_window.copy()
    set_window_size(wind_size)


    #game loop
    running = True

    # Setup
    tps_timer = 0
    g_timer = gravity
    p_timer = player_move

    curr_time = time.time()
    prev_time = curr_time


    test = TileList()
    current_tile = Block(SQUARE_LAYOUT, (255,0,0), test)

    hard_dropped = False

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
                size = list(event.size)
                size[0] = size[1]*wind_size.x/wind_size.y
                master_window = pygame.display.set_mode(size, VIDEO_FLAGS)

            if event.type == pygame.KEYDOWN:
                # Game Input
                if event.key not in held_keys_duration:
                    held_keys_duration[event.key] = 0
                if event.key == pygame.K_i:
                    hard_dropped = False
                    pygame.time.set_timer(lock_delay_timer, 0)
                    print("locked")
                    if current_tile:
                        test.append(current_tile)
                        current_tile = Tile((100,200,38), test)


            if event.type == pygame.KEYUP:
                # Game Input
                held_keys_duration.pop(event.key)

            # Timers
            if event.type == lock_delay_timer or hard_dropped:
                hard_dropped = False
                pygame.time.set_timer(lock_delay_timer, 0)
                print("locked")
                if current_tile:
                    test += current_tile.get_tiles_only()
                    current_tile = block_factory(random.choice(LAYOUTS), test)

        # Click inputs
        if current_tile:
            if Input.is_just_pressed("A_LEFT"):
                p_timer = player_move_delay
                current_tile.grid_pos.x -= 1
            if Input.is_just_pressed("A_RIGHT"):
                p_timer = player_move_delay
                current_tile.grid_pos.x += 1
            if Input.is_just_pressed("A_DOWN"):
                p_timer = player_move_delay
                current_tile.grid_pos.y += 1
            # Quick drop
            if Input.is_just_pressed("A_UP"):
                while current_tile.falling:
                    current_tile.grid_pos.y += 1
                    current_tile.update(delta_t, window, False)
                hard_dropped = True

        # Handle events (old form)
        tps_timer += delta_t
        if tps_timer >= 1/tps:
            tps_timer = 0

            g_timer -= 1
            p_timer -= 1
            if g_timer <= 0:
                g_timer = gravity
                if current_tile:
                    current_tile.grid_pos.y += 1

            p_timer -= 1
            if p_timer <= 0 and current_tile and not hard_dropped:
                p_timer = player_move

                if Input.is_held("A_LEFT"):
                    current_tile.grid_pos.x -= 1
                if Input.is_held("A_RIGHT"):
                    current_tile.grid_pos.x += 1
                if Input.is_held("A_DOWN"):
                    g_timer = 1
        

        # Draw
        window.fill(BK)

        # draw grid
        pygame.draw.rect(window, W, grid)
        # draw square
        if current_tile:
            current_tile.update(delta_t, window)

        test.draw(window)

        master_window.blit(pygame.transform.scale(window, master_window.get_rect().size), (0, 0))
        pygame.display.update()

    return 0 # All good, exit game

main()
