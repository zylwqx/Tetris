import pygame
import random
import time

def main():
    x = 800
    y = 900

    #display
    pygame.init()
    size = (x, y)
    window = pygame.display.set_mode(size, pygame.RESIZABLE)

    BK = (0, 0, 0)
    W = (255, 255, 255)
    PY = (253, 253, 150)
    PB = (167, 199, 231)

    TILE_SIZE = 40


    #game loop
    running = True

    #game grid
    grid = pygame.Rect(200, 50, TILE_SIZE*10,TILE_SIZE*20)
    #slot 1: 200
    #slot 2: 240
    #slot 3: 280
    #slot 4: 320
    #slot 5: 360
    #slot 6: 400
    #slot 7: 440
    #slot 8: 480
    #slot 9: 520
    #slot 10: 560

    tps = 20 
    tps_timer = 0

    #different pieces
    square = pygame.Rect(360, 50, TILE_SIZE, TILE_SIZE)
    square_speed = TILE_SIZE

    # Setup
    gravity = 15
    g_timer = gravity

    player_move = 2
    p_timer = player_move

    curr_time = time.time()
    prev_time = curr_time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Restart game, will probably chnage this later to something less scuffed
                if event.key == pygame.K_r:
                    return main()

        # Delta time
        delta_t = curr_time - prev_time
        prev_time = curr_time
        curr_time = time.time()


        tps_timer += delta_t
        # Handle events
        if tps_timer >= 1/tps:
            tps_timer = 0

            g_timer -= 1
            p_timer -= 1
            if g_timer <= 0:
                square.y += square_speed
                g_timer = gravity

            p_timer -= 1
            if p_timer <= 0:
                p_timer = player_move

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
                    square.x -= square_speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    square.x += square_speed
                if keys[pygame.K_DOWN]  or keys[pygame.K_s]:
                    square.y += square_speed

        

        # wall limits
        if square.x <= 200:
            square.x = 200
        if square.x >= 560:
            square.x = 560
        if square.y >= 810:
            square.y = 810

        window.fill(BK)

        # draw square
        pygame.draw.rect(window, W, grid)
        pygame.draw.rect(window, PY, square)


        pygame.display.update()

    return 0 # All good, exit game

main()
