import random

import pygame
from queue import Queue

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BlUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
COLORS = [BLACK, RED, GREEN, BlUE, WHITE, YELLOW, ORANGE, PURPLE, PINK]

RESOLUTION_RATIO = 9/16
RESOLUTION = 480
REFRESH_RATE = 10

WINDOW_TITLE = 'Snake'

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
BLOCK_SIZE = 10

SNAKE_SPEED = BLOCK_SIZE + 1
STARTER_SIZE = 1


class BlockObject:
    def __init__(self, pos, size, color):
        self._pos = pos
        self._size = size
        self._color = color

    def draw(self, screen):
        screen.fill(self._color, self.rect)

    def delete(self, screen):
        screen.fill(BLACK, self.rect)

    @property
    def rect(self):
        return pygame.Rect(self._pos, (self._size, self._size))

    def is_touch(self, other):
        return self.rect.colliderect(other.rect)


class Snake(BlockObject):
    def __init__(self, screen: pygame.Surface):
        super(Snake, self).__init__(round_to_grid(screen.get_rect().center), BLOCK_SIZE, RED)
        self._direction = UP
        self._speed = SNAKE_SPEED
        self._queue = Queue()
        self.add(STARTER_SIZE-1)

    def _is_disqualified(self, screen: pygame.Surface):
        head = self.rect
        top_left = head.topleft
        top_right = head.topright
        bottom_left = head.bottomleft
        bottom_right = head.bottomright
        try:
            return RED in [screen.get_at(top_left),
                           screen.get_at(top_right),
                           screen.get_at(bottom_left),
                           screen.get_at(bottom_right)]
        except IndexError:
            return True

    @property
    def _next_pos(self):
        x, y = self._pos
        if self._direction == UP:
            y -= self._speed
        elif self._direction == DOWN:
            y += self._speed
        elif self._direction == RIGHT:
            x += self._speed
        else:
            x -= self._speed
        return x, y

    def update(self, screen: pygame.Surface, food):
        self._queue.put(self._pos)
        self._color = RED
        self.draw(screen)
        self._pos = self._next_pos
        self.delete(screen)
        dsq = self._is_disqualified(screen)
        self._check_food(food, screen)
        self._color = BlUE
        self.draw(screen)
        return dsq

    def delete(self, screen):
        x, y = self._queue.get()
        screen.fill(BLACK, pygame.Rect(x, y, self._size, self._size))

    def set_direction(self, button):
        if button == pygame.K_UP and self._direction not in [UP, DOWN]:
            self._direction = UP
        elif button == pygame.K_DOWN and self._direction not in [UP, DOWN]:
            self._direction = DOWN
        elif button == pygame.K_RIGHT and self._direction not in [RIGHT, LEFT]:
            self._direction = RIGHT
        elif button == pygame.K_LEFT and self._direction not in [RIGHT, LEFT]:
            self._direction = LEFT

    def add(self, value=1):
        while value:
            self._queue.put((-100, -100))
            value -= 1

    def _check_food(self, food, screen):
        check = self.is_touch(food)
        if check:
            food.delete(screen)
            food.gen_pos(screen)
            self.add(1)

    def __len__(self):
        return self._queue.qsize() + 1


class Food(BlockObject):
    def __init__(self, screen: pygame.Surface):
        super(Food, self).__init__((0, 0), BLOCK_SIZE, YELLOW)
        self.gen_pos(screen)

    def _pos_ok(self, screen: pygame.Surface):
        head = self.rect
        try:
            top_left = screen.get_at(head.topleft)
            top_right = screen.get_at(head.topright)
            bottom_left = screen.get_at(head.bottomleft)
            bottom_right = screen.get_at(head.bottomright)
            return BLACK == top_left and BLACK == top_right and BLACK == bottom_left and BLACK == bottom_right
        except IndexError:
            return False

    def gen_pos(self, screen: pygame.Surface):
        width, height = screen.get_size()
        self._pos = round_to_grid((random.randint(0, width), random.randint(0, height)))
        while not self._pos_ok(screen):
            self._pos = round_to_grid((random.randint(0, width), random.randint(0, height)))


def round_to_grid(pos):
    x, y = pos
    x = x - x % SNAKE_SPEED
    y = y - y % SNAKE_SPEED
    return x, y


def resolution(res):
    return round_to_grid((int(res/RESOLUTION_RATIO), res))


def main():
    pygame.init()
    screen = pygame.display.set_mode(resolution(RESOLUTION))
    print(screen.get_rect())
    pygame.display.set_caption(WINDOW_TITLE)
    snake = Snake(screen)
    food = Food(screen)
    running = True
    clock = pygame.time.Clock()
    while running:
        new_dir = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT] and not new_dir:
                    new_dir = event.key
        if new_dir:
            snake.set_direction(new_dir)
        running = not snake.update(screen, food) and running
        food.draw(screen)
        pygame.display.flip()
        clock.tick(REFRESH_RATE)
    print(len(snake))


if __name__ == '__main__':
    main()
