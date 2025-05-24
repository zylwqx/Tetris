import pygame
import time

from utilities import *
from Layouts import *
from Tetris import *
from Menu import *


pygame.init()

# Settings
bg_music = pygame.mixer.Sound(ASSETS_PATH+"game-over-danijel-zambo-main-version-1394-02-03.mp3")

class Game:
    def __init__(self):
        # Display
        self.master_window = pygame.display.set_mode(tuple(wind_size), VIDEO_FLAGS | pygame.NOFRAME)
        self.window = self.master_window.copy()

        self.scenes = {
            "Main": MainMenu(),
            "Tetris": TetrisGame(self.window,"CENTERED"),
            "Pause": PauseMenu(),
            "Credits": Credits(),
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
        bg_music.play(-1)
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
        
            scene_status = self.active_scenes[-1].update(delta_t, self.master_window, events)
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

            pygame.display.update()

def main():
    game = Game()
    game.start()

try:
    main()
finally:
    pygame.quit()
