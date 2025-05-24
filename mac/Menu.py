import pygame
from utilities import *


class Menu:
    def __init__(self,options, pos, font, anti_alias=True, padding=0, bg_colour=(0,0,0)):
        self.cursor_img = pygame.image.load(ASSETS_PATH+"cursor.png").convert_alpha()
        self.receiver_img = pygame.image.load(ASSETS_PATH+"cursor_receive.png").convert_alpha()

        # Menu options and text style
        self.options = options
        self.font = font
        self.anti_alias = anti_alias
        self.padding = padding
        self.bg_colour = bg_colour

        self.options_texts = [
                self.font.render(option["name"],
                    self.anti_alias,
                    option["colour"])
            for option in self.options]

        # Selection cursor
        scale_value = self.options_texts[0].get_height()/self.cursor_img.get_height()
        self.cursor_img = pygame.transform.scale_by(self.cursor_img, scale_value)
        self.cursor_rect = self.cursor_img.get_rect()

        self.receiver_img = pygame.transform.scale_by(self.receiver_img, scale_value)
        self.rec_rect = self.receiver_img.get_rect()

        self.cursor_size = self.rec_rect.width+self.cursor_rect.width

        # Menu Bounding Surface
        self.size = Vector2()
        for font in self.options_texts:
            self.size.x = max(self.size.x, font.get_width()+self.cursor_size+self.padding)
            self.size.y += font.get_height()+self.padding
        self.size.x += 2*self.padding
        self.size.y += self.padding

        self.surf = pygame.Surface(tuple(self.size))
        if pos == "CENTERED":
            self.menu_pos = (Vector2(point=pygame.display.get_window_size())-self.size)*0.5
        else:
            self.menu_pos = pos

        # helpful values
        self.text_size = Vector2(
            self.size.x-self.cursor_size-2*padding,
            self.options_texts[0].get_height())

        # Cursor
        self.selected = 0
        self.rec_rect.left = self.text_size.x+self.padding
        self.cursor_rect.left = self.rec_rect.right

        # Cursor Animation
        self.cursor_tween = Tween(
            Vector2(self.rec_rect.right, 0), # start
            Vector2(self.rec_rect.right-self.cursor_rect.width/2-1,0), # end
            1, True) # fps, as_tuple
        self.cursor_anim = Animation(self.cursor_rect, "topleft", self.cursor_tween, 120)

        self.set_cursor_pos()
    
    def enter(self):
        self.selected = 0
        self.cursor_anim.reset(True)
        self.set_cursor_pos()

    def set_cursor_pos(self):
        self.cursor_rect.top = self.selected*(self.text_size.y+self.padding)+self.padding
        self.cursor_tween.start.y = self.cursor_rect.top
        self.cursor_tween.end.y = self.cursor_rect.top
        self.cursor_tween.update()

    def draw(self, window):
        # Background
        #pygame.draw.rect(self.window, (40,95,20), self.bg["rect"])
        self.surf.fill(self.bg_colour)

        # Options
        for i in range(len(self.options)):
            blit_pos_y = i*(self.text_size.y+self.padding)+self.padding
            self.surf.blit(
                self.options_texts[i],
                (self.padding, blit_pos_y))

        # Cursor
        self.surf.blit(
            self.receiver_img,
            (self.rec_rect.left, self.cursor_rect.top))
        self.surf.blit(self.cursor_img, self.cursor_rect)

        # Menu to Window
        window.blit(self.surf, tuple(self.menu_pos))

    def update(self, delta_t, window, events, redraw=True):

        # Input
        if self.cursor_anim.status == Animation.STOPPED:
            print(Input.is_just_pressed("A_DOWN"))
            if Input.is_just_pressed("A_UP"):
                self.selected = max(0,self.selected-1)
                self.set_cursor_pos()
            elif Input.is_just_pressed("A_DOWN"):
                print("down")
                self.selected = min(len(self.options)-1,self.selected+1)
                self.set_cursor_pos()

            elif Input.is_just_pressed("UI_CANCEL"):
                self.selected = 0
                self.set_cursor_pos()
                return {"id": 3}

            elif Input.is_just_pressed("UI_SELECT"):
                # Starts select animation
                self.cursor_anim.play()

        # Option selected
        elif self.cursor_anim.status == Animation.FINISHED:
            self.cursor_anim.update(delta_t,window)
            selected = self.options[self.selected]
            self.cursor_anim.reset(True)
            if selected["on_select"] == "scene":
                return selected["select_args"]

            elif callable(selected["on_select"]):
                # Calls the option's "on_select" function
                selected["on_select"](*selected.get("select_args", ()))

                return 0

        self.cursor_anim.update(delta_t,window)

        # Draw

        if redraw:
            self.draw(window)

        return 0


class MainMenu(Menu):
    def __init__(self):
        options = [
            {"name": "Play", "colour": G,
             "on_select": "scene", "select_args": {"id": 1, "scene": "Tetris"}},
            {"name": "Adjust Screen", "colour": W,
             "on_select": "scene", "select_args": {"id": 2, "scene": "ScreenAdjust"}},
            {"name": "QUIT", "colour": R,
             "on_select": "scene", "select_args": {"id":-1}},
        ]
        super().__init__(
            options,
            "CENTERED",
            pygame.font.SysFont("Impact", 42),
            True,
            10,
            BK)

        self.title = pygame.image.load(ASSETS_PATH+"title.png").convert_alpha()
        self.title_rect = self.title.get_rect()
        self.title_rect.center = pygame.display.get_surface().get_rect().center
        self.title_rect.top = pygame.display.get_window_size()[1]*0.15

    def draw(self, window):
        window.fill(BK)
        super().draw(window)
        window.blit(self.title, self.title_rect)


class PauseMenu(Menu):
    def __init__(self, ):
        options = [
            {"name": "RESUME", "colour": PY,
             "on_select": "scene", "select_args": {"id": 3}},
            {"name": "Adjust Screen", "colour": W,
             "on_select": "scene", "select_args": {"id": 2, "scene": "ScreenAdjust"}},
            {"name": "Main Menu", "colour": PB,
             "on_select": "scene", "select_args": {"id": 1, "scene": "Main"}},
            {"name": "QUIT", "colour": R,
             "on_select": "scene", "select_args": {"id":-1}},
        ]
        super().__init__(
            options,
            "CENTERED",
            pygame.font.SysFont("Impact", 32),
            True,
            10,
            (0,0,0))


class GameOverMenu(Menu):
    def __init__(self, game):
        options = [
            {"name": "RESTART", "colour": PY,
             "on_select": "scene", "select_args": {"id": 1, "scene": "Tetris"}},
            {"name": "Main Menu", "colour": PB,
             "on_select": "scene", "select_args": {"id": 1, "scene": "Main"}},
            {"name": "QUIT", "colour": R,
             "on_select": "scene", "select_args": {"id":-1}},
        ]
        super().__init__(
            options,
            "CENTERED",
            pygame.font.SysFont("Impact", 32),
            True,
            10,
            (100,20,1))

        self.bg = pygame.display.get_surface().copy()
        self.bg.set_alpha(40)
        self.bg.fill(R)
        self.title_font = pygame.font.SysFont("Ink free", 60)

        self.game = game

    def enter(self):
        super().enter()
        self.texts = (
            self.font.render("Highscore: "+str(self.game.highscore), True, BK),
            self.font.render("Score: "+str(self.game.points), True, BK),
            self.title_font.render("GAME OVER", True, (25,0,10)))

    def draw(self, window):
        window.blit(self.bg,(0,0))

        for i in range(len(self.texts)):
            window.blit(self.texts[i],
                (self.menu_pos.x-(self.texts[i].get_width()-self.surf.get_width())/2,
                 self.menu_pos.y-(i+1)*self.texts[i].get_height()))

        super().draw(window)



class ScreenAdjust:
    def __init__(self, master_window, window):
        self.master_window = master_window
        self.font = pygame.font.SysFont('Impact', 40)

        self.bg = master_window.copy()
        self.bg.fill(BK)
        self.bg.set_alpha(160)

        self.text = self.font.render("Adjust Screen (Press [ESCAPE] when done)", True, W)
        self.subtext = self.font.render("Window resize unavailable on mac", True, W)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = master_window.get_rect().center

    def enter(self):
        print("adjusting screen")
        self.master_window = pygame.display.set_mode(self.master_window.get_size(),VIDEO_FLAGS)

    def draw(self, window):
        window.blit(self.bg, (0,0))
        window.blit(self.text, self.text_rect)
        window.blit(self.subtext, (self.text_rect.left, self.text_rect.bottom))

    def update(self, delta_t, window, events, redraw=True):
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                size = list(event.size)
                size[0] = size[1]*window.get_width()/window.get_height()
                self.master_window = pygame.display.set_mode(size, VIDEO_FLAGS | pygame.RESIZABLE)
        if Input.is_just_pressed("UI_CANCEL"):
            self.master_window = pygame.display.set_mode(self.master_window.get_size(),VIDEO_FLAGS | pygame.NOFRAME)
            return {"id": 3}

        if redraw:
            self.draw(window)


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((900,400))
    options = [
            {"name": "HELLO", "colour": BK, "on_select": quit, "select_args": ["Hello, World"]},
            {"name": "WATER", "colour": BK, "on_select": quit, "select_args": ["GLUG GLUG GLUG"]},
            {"name": "BYE", "colour": BK, "on_select": print, "select_args": ["Bye, World"]},
        ]
    m = Menu(options,
             Vector2(9,9),
             pygame.font.SysFont("Impact", 32, bold=True),
             True,
             10,
             (0,0,0,10)
             )
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60)/1000
    
        # Input hold times
        for key in held_keys_duration:
            held_keys_duration[key] += dt
    
        if pygame.event.peek(pygame.QUIT):
            running = False
    
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Game Input
                if event.key not in held_keys_duration:
                    held_keys_duration[event.key] = 0
            if event.type == pygame.KEYUP:
                # Game Input
                held_keys_duration.pop(event.key)
    
        if m.update(dt, window, events) == -1:
            m.enter()
