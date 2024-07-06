from constants import *
import pygame
import math


EYE_RADIUS = 0.7


class Circle:
    def __init__(self, center, radius):
        self._center = center
        self._radius = radius


class Eye:
    def __init__(self, target, center, radius):
        self._target = target
        self._center = center
        self._radius = radius
        self._eye_radius = self._radius*EYE_RADIUS

    def _closest(self, pos):
        x1, y1 = pos
        x2, y2 = self._center
        angle = math.atan2((y1 - y2), (x1 - x2))
        x = math.cos(angle) * (self._radius - self._eye_radius) + x2
        y = math.sin(angle) * (self._radius - self._eye_radius) + y2
        return x, y

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self._center, self._radius)
        pygame.draw.circle(screen, GREEN, self._closest(self._target), self._eye_radius)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target


class Eyes:
    def __init__(self, target, rect: pygame.Rect):
        x, y = rect.midleft
        radius = rect.centerx - x
        self._left_eye = Eye(target, (x + radius, y), radius)
        x, y = rect.midleft
        self._right_eye = Eye(target, (x - radius, y), radius)

    def set_target(self, target):
        self._left_eye.target = target
        self._right_eye.target = target

    def draw(self, screen):
        self._left_eye.draw(screen)
        self._right_eye.draw(screen)


def main():
    screen = pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    running = True
    eye = Eyes(pygame.mouse.get_pos(), pygame.Rect((100, 100, 50, 50)))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        eye.set_target(pygame.mouse.get_pos())
        eye.draw(screen)
        pygame.display.flip()
        clock.tick(30)
        screen.fill(BLACK)


if __name__ == '__main__':
    main()
