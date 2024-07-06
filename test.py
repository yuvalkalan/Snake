# import package pygame
import pygame

# Form screen with 400x400 size
# with not resizable
screen = pygame.display.set_mode((400, 400), pygame.RESIZABLE)

# set title
pygame.display.set_caption('Not resizable')

# run window
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# quit pygame after closing window
pygame.quit()