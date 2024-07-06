import random
from settings import *


class Food(GameBlock):
    def __init__(self, screen: pygame.Surface):
        super(Food, self).__init__((0, 0), (settings.block_size, settings.block_size), settings.food_color)
        self.gen_pos(screen)
        self.draw(screen)

    def _pos_ok(self, screen: pygame.Surface, last_pos):
        head = self.rect
        if last_pos == self._pos:
            return False
        try:
            top_left = screen.get_at(head.topleft)[:-1]
            top_right = screen.get_at(head.topright)[:-1]
            bottom_left = screen.get_at(head.bottomleft)[:-1]
            bottom_right = screen.get_at(head.bottomright)[:-1]
            return [top_left, top_right, bottom_left, bottom_right].count(settings.background_color) == 4
        except IndexError:
            return False

    def gen_pos(self, screen: pygame.Surface):
        width, height = screen_grids(screen)
        height = int(height - height * DATA_ZONE_SIZE - 1)
        last_pos = self._pos
        self._pos = (random.randint(0, width) * settings.snake_speed, random.randint(0, height) * settings.snake_speed)
        while not self._pos_ok(screen, last_pos):
            self._pos = (random.randint(0, width) * settings.snake_speed,
                         random.randint(0, height) * settings.snake_speed)

    def reset(self, screen):
        self.gen_pos(screen)
        self.draw(screen)

    def replace(self, screen):
        self.delete(screen)
        self.gen_pos(screen)
        self.draw(screen)


class BattleFood(Food):
    def __init__(self, screen, boundary_line: pygame.Rect, index):
        self._index = index
        self._boundary_line = boundary_line
        super(BattleFood, self).__init__(screen)

    def _pos_ok(self, screen: pygame.Surface, last_pos):
        return super(BattleFood, self)._pos_ok(screen, last_pos) and not self.rect.colliderect(self._boundary_line)

    def gen_pos(self, screen: pygame.Surface):
        width, height = screen_grids(screen)
        height = int(height - height * DATA_ZONE_SIZE - 1)
        last_pos = self._pos
        if self._index == 0:
            w_rnd = random.randint(width // 2, width) * settings.snake_speed
        else:
            w_rnd = random.randint(0, width // 2) * settings.snake_speed
        h_rnd = random.randint(0, height) * settings.snake_speed
        self._pos = (w_rnd, h_rnd)
        while not self._pos_ok(screen, last_pos):
            if self._index == 0:
                w_rnd = random.randint(width // 2, width) * settings.snake_speed
            else:
                w_rnd = random.randint(0, width // 2) * settings.snake_speed
            h_rnd = random.randint(0, height) * settings.snake_speed
            self._pos = (w_rnd, h_rnd)
