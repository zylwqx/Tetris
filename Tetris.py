import pygame
import random

from utilities import *
LTI = LootTableItem
from Layouts import *

# SETTINGS
wind_size = Vector2(800, 900)
GRID_DIMS = Vector2(10,20)

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
grid_drop_pos = Vector2(5,-1)

# Game grid
grid = pygame.Rect((wind_size.x-grid_size.x)/2, (wind_size.y-grid_size.y)/2,
                    grid_size.x, grid_size.y)



class Grid:
    def __init__(self, window, pos, dims, colour=(255,255,255)):
        self.dims = dims
        self.size = dims*tile_size

        self.map = [[0 for i in range(dims.x)] for i in range(dims.y)]

        self.bg = pygame.Surface(tuple(self.size))
        if pos == "CENTERED":
            self.pos = (Vector2(point=window.get_size())-self.size)*0.5
        else:
            self.pos = pos

        self.tile_sprite = pygame.image.load(ASSETS_PATH+"tile.png").convert_alpha()

        self.colour = colour
        self.bg.fill(colour)
        for y in range(dims.y):
            for x in range(dims.x):
                self.bg.blit(tile_sprite, (x*tile_size,y*tile_size))

    def reset(self):
        self.map = [[0 for i in range(self.dims.x)] for i in range(self.dims.y)]

    def __str__(self):
        return('\n'.join(map(lambda x: ''.join(map(str,x)),self.map)))

    def grid_pos_to_coord(self, grid_pos):
        return (self.pos.x+grid_pos.x*tile_size, self.pos.y+grid_pos.y*tile_size)

    def update_tile(self, prev_pos, new_pos):
        if new_pos.y >-1:
            self.map[new_pos.y][new_pos.x] = 2
        if self.map[prev_pos.y][prev_pos.x] != 2 and prev_pos.y > -1:
            self.map[prev_pos.y][prev_pos.x] = 0

    def update_map(self):
        self.map = list(map(
            lambda x: list(map(
                lambda y: int(bool(y)), x)), self.map))

    def draw(self, window):
        pygame.draw.rect(window, self.colour)
        for y in range(self.dims.y):
            for x in range(self.dims.x):
                window.blit(tile_sprite, (self.pos.x+x*tile_size,self.pos.y+y*tile_size))


    def clear_lines(self, tiles, window, start=0,end=None,amount=1):
        cleared = []
        for i in range(amount):
            row = start+i
            if all(self.map[row]):
                cleared.append(row)
    
        for row in sorted(cleared):
            del self.map[row]
            self.map.insert(0, [0 for _ in range(self.dims.x)])
            tile = 0
            while tile < len(tiles):
                if tiles[tile].grid_pos.y == row:
                    del tiles[tile]
                    tile -= 1
                elif tiles[tile].grid_pos.y < row:
                    tiles[tile].grid_pos.y += 1
                    tiles[tile].update(1, window)
                tile += 1
        return cleared

    def invert_grid(self, tiles, window):
        self.map = self.map[::-1]
    
        row = 0
        start = 0
        while row < self.dims.y:
            if not any(self.map[row]):
                self.map.insert(0,self.map.pop(row))
                start += 1
            row += 1
    
        for tile in tiles:
            tile.grid_pos.y = start+self.dims.y-tile.grid_pos.y-1
            tile.update(1, window, update_grid=False)

    def scroll_grid(self, tiles, window, direction):
        if direction == None:
            direction = random.randint(0,1)*2-1
    
        d = (self.dims.x - direction) % self.dims.x
        for row in range(len(self.map)):
            self.map[row] = self.map[row][d:] + self.map[row][:d]
    
        for tile in tiles:
            tile.grid_pos.x += direction
            if not -1 < tile.grid_pos.x < self.dims.x:
                tile.grid_pos.x = (tile.grid_pos.x + self.dims.x) % self.dims.x
            tile.update(1, window, update_grid=False)


class Tile(pygame.Rect):
    def __init__(self, grid, colour, grid_pos=Vector2(5,0), collision_list=None):
        super().__init__(0, 0, tile_size, tile_size)
        self.sprite = pygame.image.load(ASSETS_PATH+"tile.png").convert_alpha()
        self.colour = colour
        self.hide = False

        self.grid = grid
        self.collision_list = collision_list

        self.grid_pos = grid_pos
        self.prev_grid_pos = self.grid_pos
        self.falling = True

    def draw(self, window):
        if self.hide:
            return
        pygame.draw.rect(window,self.colour,self)
        window.blit(self.sprite, self)

    def update(self, delta_t, window, redraw=True, update_grid=True):
        # Set position
        prev_pos = self.topleft
        self.topleft = self.grid.grid_pos_to_coord(self.grid_pos)

        if update_grid and self.grid_pos != self.prev_grid_pos:
            self.grid.update_tile(self.prev_grid_pos, self.grid_pos)
        self.prev_grid_pos = self.grid_pos.copy()

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
    def __init__(self, grid, layout, colour, collision_list):
        self.layout = layout
        self.colour = colour

        convert = layout.split()

        self._grid_pos = grid_drop_pos.copy()
        self._grid_pos.x -= len(convert[0])//2
        self._grid_pos.y -= len(convert)-1

        self._bin_grid_pos = None
        self.grid_pos_updated = False
        
        self.grid = grid
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
                        Tile(self.grid, colour, drop_pos, collision_list))
                else:
                    self.tiles[row].append(None)
        self.icon_surf = pygame.Surface((tile_size*len(self.tiles[0]),tile_size*len(self.tiles)))
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                if not self.tiles[y][x]:
                    continue
                tile = self.tiles[y][x]
                tile.topleft = (x*tile_size, y*tile_size)
                tile.draw(self.icon_surf)
    
    @staticmethod
    def factory(layout, grid, collision_list):
        colour = [random.randint(0,255) for i in range(3)]
        if sum(colour)/3 > 200:
            colour = list(map(lambda x: int(x*0.8), colour))
        return Block(grid, layout, colour, collision_list)

    def spawn(self):
        for tile in self.get_tiles_only():
            self.grid.map[tile.grid_pos.y][tile.grid_pos.x] = 1


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
        if not self._bin_grid_pos:
            self._bin_grid_pos = self._grid_pos.copy()
        print(self._grid_pos, self._bin_grid_pos)
        return self._bin_grid_pos

    @grid_pos.setter
    def grid_pos(self, new_value):
        displacement = new_value-self._grid_pos
        print(displacement)
        move_hor = True if displacement.x else False
        move_ver = True if displacement.y else False

        if not (move_hor or move_ver):
            return
        dx = 0 if displacement.x < 0 else -1
        falls = displacement.y+1

        for row in range(len(self.tiles)):
            r = list(filter(lambda x: x is not None, self.tiles[row]))

            if move_hor:
                if not(0 <= r[dx].grid_pos.x+displacement.x <= self.grid.dims.x-1) or (
                        r[dx].grid_pos.y > -1 and self.grid.map[r[dx].grid_pos.y][r[dx].grid_pos.x+displacement.x]):
                    move_hor = False

            if move_ver:
                for tile in r:
                    #print(Vector2(tile.grid_pos.y+displacement.y,tile.grid_pos.x))
                    if (not tile.grid_pos.y+displacement.y <= self.grid.dims.y-1) or (
                            tile.grid_pos.y+displacement.y > -1 and self.grid.map[tile.grid_pos.y+displacement.y][tile.grid_pos.x]):
                        if -1<row+displacement.y<len(self.tiles) and self.tiles[row+displacement.y][self.tiles[row].index(tile)]:
                            continue
                        move_ver = False
                        if self.falling:
                            self.falling = False
                            print("locking")
                            pygame.time.set_timer(lock_delay_timer, int(1000*lock_delay/tps))
                        break

        if not (move_hor or move_ver):
            return

        self.falling = True
        pygame.time.set_timer(lock_delay_timer, int(1000*lock_delay/tps))
        displacement.x *= move_hor
        displacement.y *= move_ver
        self._grid_pos += displacement
        for tile in self.get_tiles_only():
            tile.grid_pos += displacement
            self.grid.update_tile(tile.prev_grid_pos, tile.grid_pos)
        self.grid.update_map()
        print()
        print(self.grid)
        print()

    def draw(self, window, surf=None, pos=(0,0)):
        window.blit(pygame.transform.scale(self.icon_surf, list(Vector2(point=self.icon_surf.get_size())*(surf.get_height()/tile_size))),pos)

    def update(self, delta_t, window, redraw=True):
        if self.grid_pos_updated:
            self.grid_pos_updated = False
            #print ("bin "+ str(self._bin_grid_pos))
            self.grid_pos = self._bin_grid_pos
            self._bin_grid_pos = None
        for tile in self.get_tiles_only():
            tile.update(delta_t,window,redraw)


class TetrisGame:
    def __init__(self, window, pos):
        # Scene Size
        self.size = wind_size
        self.surf = pygame.Surface(tuple(self.size))
        if pos == "CENTERED":
            self.pos = (Vector2(point=pygame.display.get_window_size())-self.size)*0.5
        else:
            self.pos = pos

        # Font
        self.font = pygame.font.SysFont('arial', 40)

        # Game Grid
        self.grid = Grid(window, "CENTERED", GRID_DIMS)

        # Tiles init
        self.tiles = TileList()

        # Warning zone
        self.danger_rect = pygame.Rect(
            (self.grid.pos.x,self.grid.pos.y-2*tile_size),
            (self.grid.dims.x*tile_size, 2*tile_size))
        self.bs = pygame.Surface(self.danger_rect.size)
        self.bs.set_alpha(100)
        self.bs.fill((255,50,50))

        # Loot tables
        self.LAYOUTS = LootTable(
            LTI(DONUT,1),
            LTI(O, 7),
            LTI(T, 5/3), LTI(T1, 5/3), LTI(T2, 5/3),LTI(T3, 5/3),
            LTI(L, 5/2), LTI(L1, 5/2), LTI(L2, 5/2), LTI(L3, 5/2),
            LTI(I, 5), LTI(I1, 5),
            LTI(Z, 5/3), LTI(Z1, 5/3),
            LTI(S, 5/3), LTI(S1, 5/3),
            LTI(SLASH, 5), LTI(SLASH1, 5),
            LTI(FISH, 1/4), LTI(FISH1, 1/4), LTI(FISH2, 1/4), LTI(FISH3, 1/4),
            LTI(BOW, 1),
            )

        self.GRID_EVENTS = LootTable(
            LootTableItem({"id": 0, "function": self.grid.invert_grid,
                           "args": [self.tiles, self.surf]}, 10),
            LootTableItem({"id": 1, "function": self.grid.scroll_grid,
                           "args": [self.tiles, self.surf, -1]},20),
            LootTableItem({"id": 2, "function": self.grid.scroll_grid,
                           "args": [self.tiles, self.surf, 1]}, 20),
            LootTableItem({"id": 3, "function": self.extend_queue, "args": []},2),
            LootTableItem({"id": 4, "function": self.shorten_queue, "args": []},2),
            LootTableItem({"id": 5, "function": self.gravity_up, "args": [1.4]},5),
            )

        # Spritesheets
        invert_event_spritesheet = SpriteSheet(ASSETS_PATH+"invert_anim.png")
        shift_event_spritesheet = SpriteSheet(ASSETS_PATH+"shift_anim.png")
        queue_change_event_spritesheet = SpriteSheet(ASSETS_PATH+"queue_change_anim.png")

        # Animations
        scale_grid_event = 4
        event_sprites = [
            list(map(
                lambda x: pygame.transform.scale_by(x, scale_grid_event),
                invert_event_spritesheet.load_strip((0,0,32,32),3))),
            list(map(
                lambda x: pygame.transform.scale_by(x, scale_grid_event),
                shift_event_spritesheet.images_at(
                    ((0,0,32,32),(48,0,32,32))))),
            list(map(
                lambda x: pygame.transform.scale_by(x, scale_grid_event),
                shift_event_spritesheet.images_at(
                ((64,0,32,32),(16,0,32,32))))),
            list(map(
                lambda x: pygame.transform.scale_by(x, scale_grid_event),
                queue_change_event_spritesheet.load_strip((0,0,32,32),3))),
            list(map(
                lambda x: pygame.transform.scale_by(x, scale_grid_event),
                queue_change_event_spritesheet.load_strip((0,32,32,32),3))),
            list(map(
                lambda x: pygame.transform.scale_by(x, scale_grid_event),
                shift_event_spritesheet.load_strip((0,32,32,32),2))),
            ]

        self.curr_grid_event_sprite = None
        self.grid_event_anims = list(map(
            lambda x: Animation(self, "curr_grid_event_sprite", x, len(x), True),
            event_sprites))

        # Reset game values
        self.reset()
        self.highscore = 0

    def enter(self):
        self.reset()
        try:
            with open ("highscore.txt",'r') as f:
                self.highscore = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            print("File corrupted. Creating new savefile...")
            with open("highscore.txt", 'w') as f:
                f.write('0')

    def reset(self):
        # Timers
        self.tps_timer = 0
        self.gravity = gravity
        self.g_timer = self.gravity
        self.p_timer = player_move
    
        self.event_distance = 15
        self.event_countdown = self.event_distance
        # Event
        self.countdown_text = self.font.render("Next: "+str(self.event_countdown), False, W)
        self.grid_event = self.GRID_EVENTS.random_item()
        
        for anim in self.grid_event_anims:
            anim.stop()
        self.grid_event_anims[self.grid_event["id"]].play()

        # Game
        self.grid.reset()

        self.points = 0
        self.cleared_lines_text = self.font.render("Cleared:", True, W)
        self.points_text = self.font.render(str(self.points), False, W)

        self.tiles.clear()

        self.block_queue = [
                Block.factory(self.LAYOUTS.random_item(),self.grid, self.tiles)
            for _ in range(4)]
        self.current_tile = self.block_queue.pop(0)
    
        self.surface_queue = [pygame.Surface((20,20)) for _ in self.block_queue]
    
        self.hard_dropped = False

    def gravity_up(self, modifier=1.15):
        self.gravity = max(1, self.gravity/modifier)

    def extend_queue(self, amount=1):
        if amount < 0:
            raise ValueError("expected: 0 <= int(amount); received "+str(amount))
        for i in range(amount):
            self.block_queue.append(
                Block.factory(self.LAYOUTS.random_item(),self.grid, self.tiles))
            self.surface_queue.append(self.surface_queue[0].copy())

    def shorten_queue(self, amount=1):
        if amount < 0:
            raise ValueError("expected: 0 <= int(amount); received "+str(amount))
        for i in range(amount):
            if len(self.block_queue) <= 1:
                break
            self.block_queue.pop()
            self.surface_queue.pop()

    def draw(self, window):
        window.blit(self.surf, tuple(self.pos))

    def update(self, delta_t, window, events, redraw=True):

        # Event loop
        for event in events:

            # Timers

            # Block locks
            if event.type == lock_delay_timer or self.hard_dropped:
                self.hard_dropped = False
                pygame.time.set_timer(lock_delay_timer, 0)
                print("locked")
                if self.current_tile:
                    # GameOver 
                    if self.current_tile.grid_pos.y <= -1:
                        if self.points > self.highscore:
                            self.highscore = self.points
                            with open ("highscore.txt", 'w') as f:
                                f.write(str(self.highscore))

                        return {"id": 1, "scene": "GameOver"}

                    # Points/clear tiles
                    self.tiles += self.current_tile.get_tiles_only()
                    self.points += len(
                        self.grid.clear_lines(
                            self.tiles, window,
                            start=self.current_tile.grid_pos.y,
                            amount=len(self.current_tile.tiles)))
                    self.points_text = self.font.render(str(self.points), False, W)

                    # Game Events
                    print(self.event_countdown)
                    self.event_countdown -= 1
                    if self.event_countdown < 1:
                        # Switch event and decrease time till next event
                        self.event_distance = max(1, 0.9*self.event_distance)
                        self.event_countdown = round(self.event_distance)

                        # Call event function
                        self.grid_event["function"](*self.grid_event["args"])

                        self.grid_event_anims[self.grid_event["id"]].stop()
                        self.grid_event = self.GRID_EVENTS.random_item()
                        self.grid_event_anims[self.grid_event["id"]].play()

                    self.countdown_text = self.font.render("Next: "+str(self.event_countdown), False, W)

                    self.current_tile = self.block_queue.pop(0)
                    self.block_queue.append(Block.factory(self.LAYOUTS.random_item(), self.grid, self.tiles))


        # Click inputs
        if Input.is_just_pressed("UI_CANCEL"):
            #TODO kinda shoddy temp fix for pausing the timer
            # Might have to revert to old form
            pygame.time.set_timer(lock_delay_timer, 0)
            return {"id": 2, "scene": "Pause"}

        if self.current_tile:
            if Input.is_just_pressed("A_LEFT"):
                self.p_timer = player_move_delay
                self.current_tile.grid_pos.x -= 1
            if Input.is_just_pressed("A_RIGHT"):
                self.p_timer = player_move_delay
                self.current_tile.grid_pos.x += 1
            if Input.is_just_pressed("A_DOWN"):
                self.p_timer = player_move_delay
                self.current_tile.grid_pos.y += 1
            # Quick drop
            if Input.is_just_pressed("A_UP"):
                while self.current_tile.falling:
                    self.current_tile.grid_pos.y += 1
                    self.current_tile.update(delta_t, window, False)
                    self.grid.update_map()
                self.hard_dropped = True

        # Handle events (old form)
        self.tps_timer += delta_t
        if self.tps_timer >= 1/tps:
            self.tps_timer = 0

            self.g_timer -= 1
            self.p_timer -= 1
            if self.g_timer <= 0:
                self.g_timer = self.gravity
                if self.current_tile:
                    self.current_tile.grid_pos.y += 1

            self.p_timer -= 1
            if self.p_timer <= 0 and self.current_tile and not self.hard_dropped:
                self.p_timer = player_move
                if Input.is_held("A_LEFT"):
                    self.current_tile.grid_pos.x -= 1
                if Input.is_held("A_RIGHT"):
                    self.current_tile.grid_pos.x += 1
                if Input.is_held("A_DOWN"):
                    self.g_timer = 1
        
        # Next event
        self.grid_event_anims[self.grid_event["id"]].update(delta_t, window)
        
        # Update grid map
        self.grid.update_map()

        # Draw
        window.fill(BK)

        self.grid.draw(window)

        # draw grid
        window.blit(self.grid.bg, tuple(self.grid.pos))

        # update current_tile
        if self.current_tile:
            self.current_tile.update(delta_t, window)

        # Draw idle tiles
        self.tiles.draw(window)

        # Block Queue
        temp_height = 50
        #window.blit(self.)
        for i in range(len(self.block_queue)):
            self.block_queue[i].draw(window, self.surface_queue[i], (50,temp_height))
            temp_height += self.block_queue[i].icon_surf.get_height()*(windowace_queue[i].get_height()/tile_size) + 20

        # Event Countdown
        window.blit(self.countdown_text, (wind_size.x*0.8,wind_size.y*0.7))
        window.blit(self.curr_grid_event_sprite, (wind_size.x*0.8,wind_size.y*0.75))

        # Points
        window.blit(self.cleared_lines_text, (wind_size.x*0.8,wind_size.y*0.1))
        window.blit(self.points_text, (wind_size.x*0.8,wind_size.y*0.15))

        # Danger zone
        window.blit(self.bs, self.danger_rect)

#        if redraw:
#            self.draw(window)

        return 0

