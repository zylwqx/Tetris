import pygame
import random

def main():
    x = 800
    y = 900

    #display
    pygame.init()
    size = (x, y)
    window = pygame.display.set_mode(size)

    BK = (0, 0, 0)
    W = (255, 255, 255)
    PY = (253, 253, 150)
    PB = (167, 199, 231)


    #game loop
    running = True

    #game grid
    grid = pygame.Rect(200, 50, 400, 800)
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


    #different pieces
    square = pygame.Rect(360, 50, 40, 40)
    square_speed = 40

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
                square.x -= square_speed
                if square.x <= 200:
                    square.x = 200
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                square.x += square_speed
                if square.x >= 560:
                    square.x = 560
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                square.y += square_speed
                if square.y >= 810:
                    square.y = 810

        window.fill(BK)

        #draw player square
        pygame.draw.rect(window, W, grid)
        
        #pygame.draw.rect(window, PB, I)
        pygame.draw.rect(window, PY, square)

        pygame.display.update()
        pygame.time.delay(50)

main()