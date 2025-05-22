import pygame
import time

from utilities import *
from Layouts import *
from Tetris import *
from Menu import *


pygame.init()

# Settings
font = pygame.font.SysFont('arial', 40)

class Game:
    def __init__(self):
        # Display
        self.master_window = pygame.display.set_mode(tuple(wind_size), VIDEO_FLAGS | pygame.NOFRAME)
        self.window = self.master_window.copy()

        self.scenes = {
            "Main": MainMenu(),
            "Tetris": TetrisGame(self.window,"CENTERED"),
            "Pause": PauseMenu(),
            "ScreenAdjust": ScreenAdjust(self.master_window, self.window),}
        self.scenes["GameOver"]=  GameOverMenu(self.scenes["Tetris"])

        self.active_scenes = [self.scenes["Main"]]

    def switch_scene(self, new_scene):
        if new_scene in self.scenes:
            #TODO self.active_scenes[-1].exit()
            self.active_scenes.clear()
            self.active_scenes.append(self.scenes[new_scene])
            self.active_scenes[-1].enter()

    def popup_scene(self, new_scene):
        self.active_scenes.append(self.scenes[new_scene])
        self.active_scenes[-1].enter()

    def close_scene(self, amount=1):
        for _ in range(min(amount, len(self.active_scenes)-1)):
            #TODO self.active_scenes[-1].exit()
            self.active_scenes.pop()

    def start(self):
        self.running = True

        curr_time = time.time()
        prev_time = curr_time

        clock = pygame.time.Clock()

        self.active_scenes[-1].enter()
        while self.running:
            clock.tick(30)
            # Delta time
            delta_t = curr_time - prev_time
            prev_time = curr_time
            curr_time = time.time()
    
            if pygame.event.peek(pygame.QUIT):
                self.running = False
    
            # Input hold times
            for key in held_keys_duration:
                held_keys_duration[key] += delta_t
    
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # Game Input
                    if event.key not in held_keys_duration:
                        held_keys_duration[event.key] = 0
                if event.type == pygame.KEYUP:
                    # Game Input
                    held_keys_duration.pop(event.key)
        
            scene_status = self.active_scenes[-1].update(delta_t, self.window, events)
            if scene_status:
                match scene_status["id"]:
                    case -1:
                        self.running = False
                    case 1:
                        self.switch_scene(scene_status["scene"])
                    case 2:
                        self.popup_scene(scene_status["scene"])
                    case 3:
                        self.close_scene()

            for s in self.active_scenes:
                s.draw(self.window)

            self.master_window.blit(pygame.transform.scale(self.window, self.master_window.get_size()), (0, 0))
            pygame.display.update()

def main():
<<<<<<< Updated upstream
    game = Game()
    game.start()
=======
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

    tile_sprite = pygame.image.load("tile.png").convert_alpha()

    points = 0

    grid_bg = pygame.Surface(list(GRID_DIMS*tile_size))
    grid_bg.fill(W)
    for y in range(GRID_DIMS.y):
        for x in range(GRID_DIMS.x):
            grid_bg.blit(tile_sprite, (x*tile_size,y*tile_size))
    #grid_bg.set_alpha(100)

    block_queue = [random.choice(LAYOUTS) for _ in range(4)]
    #block_queue = [LAYOUTS[0] for _ in range(40)]
    test = TileList()
    current_tile = block_factory(block_queue.pop(0), test)

    hard_dropped = False

    clock = pygame.time.Clock()
    while running:
        clock.tick(60)
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


            if event.type == pygame.KEYUP:
                # Game Input
                held_keys_duration.pop(event.key)

            # Timers

            # Block locks
            if event.type == lock_delay_timer or hard_dropped:
                hard_dropped = False
                pygame.time.set_timer(lock_delay_timer, 0)
                print("locked")
                if current_tile:
                    if current_tile.grid_pos.y == 0:
                        running = False
                        break
                    test += current_tile.get_tiles_only()
                    points += len(check_clear_lines(test, window,start=current_tile.grid_pos.y,amount=len(current_tile.tiles)))
                    print(points)
                    current_tile = block_factory(block_queue.pop(0), test)
                    block_queue.append(random.choice(LAYOUTS))


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
        
        # Update grid map
        update_grid_map()

        # Draw
        window.fill(BK)

        # draw grid
        pygame.draw.rect(window, (255,255,255), grid)
        # window.blit(grid_bg,(grid.x,grid.y))

        # draw square
        if current_tile:
            current_tile.update(delta_t, window)

        test.draw(window)

        master_window.blit(pygame.transform.scale(window, master_window.get_rect().size), (0, 0))
        pygame.display.update()

    return 0 # All good, exit game
>>>>>>> Stashed changes

try:
    main()
finally:
    pygame.quit()
    input("\033[31m(Enter)")
