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
    grid = pygame.Rect(250, 150, 300, 600)

    #different pieces
    L = pygame.Rect(0, 0, 30, 120)
    J = 1
    I = pygame.Rect(0, 0, 30, 120)
    T = 1
    O = pygame.Rect(30, 0, 60, 60)
    S = 1
    Z = 1

    while running:
        #player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()

        window.fill(BK)

        #draw player square
        pygame.draw.rect(window, W, grid)
        
        pygame.draw.rect(window, PB, I)
        pygame.draw.rect(window, PY, O)

        pygame.display.update()
        pygame.time.delay(20)

main()