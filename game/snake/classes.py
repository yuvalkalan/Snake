import pygame.draw
from font import *
from .constants import *
from queue import Queue


class Eye(CircleObject):
    def __init__(self, target, pos, radius, screen):
        super(Eye, self).__init__(pos, radius, WHITE)
        self._target = target
        w, h = screen.get_size()
        self._screen_radius = (w**2 + h**2) ** 0.5

    @property
    def distance(self):
        return distance(self._pos, self._target)

    @property
    def _eye_radius(self):
        return max(min(self._radius * (1 - self.distance / self._screen_radius)**5, self._radius*0.8), 3)

    def _closest(self, pos):
        x1, y1 = pos
        x2, y2 = self.rect.center
        angle = math.atan2((y1 - y2), (x1 - x2))
        x = math.cos(angle) * (self._radius - self._eye_radius) + x2
        y = math.sin(angle) * (self._radius - self._eye_radius) + y2
        return round(x), round(y)

    def draw(self, screen):
        super(Eye, self).draw(screen)
        pygame.draw.circle(screen, GREEN, self._closest(self._target), self._eye_radius)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value


class SnakeEyes:
    def __init__(self, head, target, screen):
        self._head = head
        x, y = self._head.rect.midleft
        radius = (self._head.rect.centerx - x) // 2
        self._left_eye = Eye(target, (x + radius, y), radius, screen)
        x, y = self._head.rect.midright
        self._right_eye = Eye(target, (x - radius, y), radius, screen)

    def update(self, target):
        x, y = self._head.rect.midleft
        radius = (self._head.rect.centerx - x) // 2
        if self._head.direction in [0, 180]:
            self._left_eye.pos = (x + radius, y)
            x, y = self._head.rect.midright
            self._right_eye.pos = (x - radius, y)
        else:
            x, y = self._head.rect.midtop
            self._left_eye.pos = (x, y + radius)
            x, y = self._head.rect.midbottom
            self._right_eye.pos = (x, y - radius)
        self._left_eye.target = target
        self._right_eye.target = target

    def draw(self, screen, target):
        self.update(target)
        self._left_eye.draw(screen)
        self._right_eye.draw(screen)


class SnakeBody(ImageObject):
    def __init__(self, snake, index):
        self._snake = snake
        self._queue = Queue()
        self._movement_counter = 0
        super(SnakeBody, self).__init__((-100, -100), settings.body1_image if index == 0 else settings.body2_image,
                                        settings.snake_size)
        self._current_block = None
        self._last_block = None
        self._tail_image = Clicker((0, 0), TAIL_IMAGE, 0, 0).copy_color(BLACK, settings.background_color)
        self.reset()

    def draw(self, screen):
        (x, y), direction = self._pos, self.direction
        movement_delta = cal_movement()
        pos_delta = movement_delta * self._movement_counter
        if self._movement_counter == MOVEMENT_COUNTER - 1:
            movement_delta = settings.block_size - movement_delta * self._movement_counter
        if direction == DIR_DOWN:
            y += pos_delta
            del_size = (settings.block_size, movement_delta)
        elif direction == DIR_UP:
            y += settings.block_size - pos_delta - movement_delta
            del_size = (settings.block_size, movement_delta)
        elif direction == DIR_LEFT:
            x += settings.block_size - pos_delta - movement_delta
            del_size = (movement_delta, settings.block_size)
        else:
            x += pos_delta
            del_size = (movement_delta, settings.block_size)
        s_x, s_y = self._pos
        screen.blit(self._image.subsurface(((x - s_x, y - s_y) + del_size)), (x, y))

    def round_tail(self, screen):
        counter = self._movement_counter + 1
        if counter == MOVEMENT_COUNTER:
            (x, y), direction = self._current_block
            counter = 0
        else:
            (x, y), direction = self._last_block
        movement_delta = cal_movement()
        pos_delta = movement_delta * counter
        if counter == MOVEMENT_COUNTER - 1:
            movement_delta = settings.block_size - movement_delta * counter
        if direction == DIR_DOWN:
            y += pos_delta
            del_size = (settings.block_size, movement_delta)
        elif direction == DIR_UP:
            y += settings.block_size - pos_delta - movement_delta
            del_size = (settings.block_size, movement_delta)
        elif direction == DIR_LEFT:
            x += settings.block_size - pos_delta - movement_delta
            del_size = (movement_delta, settings.block_size)
        else:
            x += pos_delta
            del_size = (movement_delta, settings.block_size)
        image = self._tail_image.copy()
        image.repos((x, y), HEAD_DIRECTIONS[direction])
        image.size = sorted(del_size, reverse=True)
        image.draw(screen)

    def delete(self, screen):
        (x, y), direction = self._last_block
        movement_delta = cal_movement()
        pos_delta = movement_delta * self._movement_counter
        if self._movement_counter == MOVEMENT_COUNTER - 1:
            movement_delta = settings.block_size - movement_delta * self._movement_counter + 1
        if direction == DIR_DOWN:
            y += pos_delta
            del_size = (settings.block_size, movement_delta)
        elif direction == DIR_UP:
            y += settings.block_size - pos_delta - movement_delta
            del_size = (settings.block_size, movement_delta)
        elif direction == DIR_LEFT:
            x += settings.block_size - pos_delta - movement_delta
            del_size = (movement_delta, settings.block_size)
        else:
            x += pos_delta
            del_size = (movement_delta, settings.block_size)
        screen.fill(settings.background_color, (x, y) + del_size)

    def add(self, value=1):
        for _ in range(value):
            self._queue.put((self._pos, self.direction))

    def repos(self, pos, _=None):
        self._pos = pos
        self._queue.put((self._pos, self.direction))

    def update(self, pos, screen):
        if self._movement_counter == 0:
            self.repos(pos)
            self._last_block = self._current_block
            self._current_block = self._queue.get()
            if self._current_block[0] == self._last_block[0]:
                self._current_block = self._last_block
        self.draw(screen)
        if self._current_block[0] != self._last_block[0]:
            self.delete(screen)
            self.round_tail(screen)
        self._movement_counter = (self._movement_counter + 1) % MOVEMENT_COUNTER

    def reset(self):
        self._queue = Queue()
        self._pos = (-100, -100)
        self.add(STARTER_SIZE)
        self._movement_counter = 0
        self._current_block = self._queue.get()
        self._last_block = None

    def __len__(self):
        return self._queue.qsize()

    @property
    def direction(self):
        return self._snake.direction


class Snake(ScreenObject):
    def __init__(self, screen: pygame.Surface, data, index: int = 0, players: int = 1):
        super(Snake, self).__init__((0, 0), (settings.block_size, settings.block_size))
        self._index = index
        self._players = players
        self._got_dir = False
        self._dsq = False
        self._direction = DIR_UP
        self._movement_counter = 0
        self._speed = settings.snake_speed
        width, height = screen_grids(screen)
        height = int(height - height * DATA_ZONE_SIZE)
        self._grid_width = width
        self._grid_height = height
        self._teleport = settings.teleport
        self.set_starter_pos(screen)
        self._head = ImageObject(self._pos, settings.head1_image if self._index == 0 else settings.head2_image,
                                 settings.snake_size)
        self._eyes = SnakeEyes(self._head, (0, 0), screen)
        self._body = SnakeBody(self, self._index)
        self._volume = data.volume
        self.draw(screen)

    def set_starter_pos(self, screen):
        x, y = screen.get_size()
        x = x // (self._players + 1) * (self._players - self._index)
        y = y // 2
        self._pos = round_to_grid((x, y))

    @property
    def _grid_size(self):
        return self._grid_width * self._grid_height

    @property
    def _max_x(self):
        return (self._grid_width - 1) * settings.snake_speed

    @property
    def _max_y(self):
        return (self._grid_height - 1) * settings.snake_speed

    @property
    def _front_line(self):
        length = self._size[0]
        if self._direction == DIR_UP:
            x, y = self.rect.topleft
            return [(x + i, y) for i in range(length)]
        elif self._direction == DIR_RIGHT:
            x, y = self.rect.topright
            return [(x - 1, y + i) for i in range(length)]
        elif self._direction == DIR_DOWN:
            x, y = self.rect.bottomleft
            return [(x + i, y-1) for i in range(length)]
        x, y = self.rect.topleft
        return [(x, y + i) for i in range(length)]

    def _is_disqualified(self, screen: pygame.Surface, data_zone):
        if self.is_touch(data_zone):
            return not self._teleport
        try:
            for pos in self._front_line:
                if screen.get_at(pos)[:-1] != settings.background_color:
                    return True
            return False
        except IndexError:
            return not self._teleport

    @property
    def _next_pos(self):
        x, y = self._pos
        movement = self._speed
        if self._direction == DIR_UP:
            y -= movement
        elif self._direction == DIR_DOWN:
            y += movement
        elif self._direction == DIR_RIGHT:
            x += movement
        else:
            x -= movement
        if self._teleport:
            x, y = self._cal_teleport((x, y))
        return x, y

    def _cal_teleport(self, pos):
        x, y = pos
        if x < 0:
            x = (self._grid_width - 1) * settings.snake_speed
        elif x > self._max_x:
            x = 0
        elif y < 0:
            y = (self._grid_height - 1) * settings.snake_speed
        elif y > self._max_y:
            y = 0
        return x, y

    @property
    def index(self):
        return self._index

    @property
    def dsq(self):
        return self._dsq

    @property
    def on_grid(self):
        x, y = self._pos
        if x % settings.snake_speed == 0 and y % settings.snake_speed == 0:
            return True
        return False

    @property
    def _timer_delta(self):
        return SURVIVAL_TIMER * MOVEMENT_COUNTER * self._grid_size / 1792

    @property
    def direction(self):
        return self._direction

    def _play_redirect(self):
        play_sound(SNAKE_CHANNEL, REDIRECT_SOUND, self._volume.value)

    def _play_eat(self):
        play_sound(FOOD_CHANNEL, EAT_SOUND, self._volume.value)

    def update_head(self, screen, food):
        x, y = self._head.pos
        movement = cal_movement()
        if self._movement_counter == MOVEMENT_COUNTER - 1:
            movement = settings.block_size - movement * self._movement_counter
        if self._direction == DIR_UP:
            y -= movement
        elif self._direction == DIR_DOWN:
            y += movement
        elif self._direction == DIR_RIGHT:
            x += movement
        else:
            x -= movement
        self._head.repos((x, y), HEAD_DIRECTIONS[self._direction])
        self._head.draw(screen)
        self._eyes.draw(screen, food.pos)

    def update(self, screen: pygame.Surface, food, data_zone):
        if self._movement_counter == 0:
            if self._got_dir is not False:
                self._direction = self._got_dir
                self._got_dir = False
                self._play_redirect()
            current_pos = self._pos
            self._pos = self._next_pos
            if not self._check_food(food, screen):
                self._dsq = self._is_disqualified(screen, data_zone)
            self._head.repos(current_pos, HEAD_DIRECTIONS[self._direction])
            self._head.draw(screen)
            self._eyes.draw(screen, food.pos)
            self._body.update(current_pos, screen)
            self.update_head(screen, food)
        else:
            self.update_head(screen, food)
            self._body.update(self._pos, screen)
        self._movement_counter = (self._movement_counter + 1) % MOVEMENT_COUNTER
        return self._dsq

    def set_direction(self, button):
        if self._got_dir is False:
            if button in P2_CVT_KEYS:
                button = P2_CVT_KEYS[button]
            if button == pygame.K_UP and self._direction not in [DIR_UP, DIR_DOWN]:
                self._got_dir = DIR_UP
            elif button == pygame.K_DOWN and self._direction not in [DIR_UP, DIR_DOWN]:
                self._got_dir = DIR_DOWN
            elif button == pygame.K_RIGHT and self._direction not in [DIR_RIGHT, DIR_LEFT]:
                self._got_dir = DIR_RIGHT
            elif button == pygame.K_LEFT and self._direction not in [DIR_RIGHT, DIR_LEFT]:
                self._got_dir = DIR_LEFT

    @property
    def optional_arrows(self):
        if self._direction in [DIR_UP, DIR_DOWN]:
            return [pygame.K_RIGHT, pygame.K_LEFT]
        return [pygame.K_UP, pygame.K_DOWN]

    def add(self, value=1):
        self._body.add(value)

    def _check_food(self, food, screen):
        check = self.is_touch(food)
        if check:
            food.replace(screen)
            self._play_eat()
            self.add(1)
        return check

    def __len__(self):
        return len(self._body) + 1

    def reset(self, screen):
        self.set_starter_pos(screen)
        self._direction = DIR_UP
        self._movement_counter = 0
        self._head.repos(self._pos)
        self._body.reset()
        self.draw(screen)


class BattleSnake(Snake):
    def __init__(self, screen: pygame.Surface, data, boundary_line: pygame.Rect, index: int = 0, players: int = 2):
        super(BattleSnake, self).__init__(screen, data, index, players)
        self._boundary_line = boundary_line

    def _is_disqualified(self, screen: pygame.Surface, data_zone):
        if self._boundary_line.colliderect(self.rect):
            return not self._teleport
        return super(BattleSnake, self)._is_disqualified(screen, data_zone)

    def _cal_teleport(self, pos):
        x, y = pos
        if x < 0:
            x = self._boundary_line.left - settings.snake_speed
        elif x > self._boundary_line.left - settings.snake_speed and self._index == 1:
            x = 0
        elif x < self._boundary_line.right and self.index == 0:
            x = self._max_x
        elif x > self._max_x:
            x = self._boundary_line.right + 1
        elif y < 0:
            y = (self._grid_height - 1) * settings.snake_speed
        elif y > self._max_y:
            y = 0
        return x, y


class SurvivalSnake(Snake):
    def __init__(self, screen: pygame.Surface, data, index: int = 0, players: int = 2):
        super(SurvivalSnake, self).__init__(screen, data, index, players)
        self._timer = 0

    def update(self, screen: pygame.Surface, food, data_zone):
        dsq = super(SurvivalSnake, self).update(screen, food, data_zone)
        self._timer += 1
        if self._timer >= self._timer_delta:
            self.add(1)
            self._timer -= self._timer_delta
        return dsq

    def _check_food(self, food, screen):
        check = self.is_touch(food)
        if check:
            food.replace(screen)
            self._play_eat()
            self._timer -= self._timer_delta
        return check


class SurvivalBattleSnake(BattleSnake):
    def __init__(self, screen: pygame.Surface, data, boundary_line: pygame.Rect, index: int = 0, players: int = 2):
        super(BattleSnake, self).__init__(screen, data, index, players)
        self._boundary_line = boundary_line
        self._timer = 0

    @property
    def _timer_delta(self):
        return super(SurvivalBattleSnake, self)._timer_delta/2

    def update(self, screen: pygame.Surface, food, data_zone):
        dsq = super(SurvivalBattleSnake, self).update(screen, food, data_zone)
        self._timer += 1
        if self._timer >= self._timer_delta:
            self.add(1)
            self._timer -= self._timer_delta
        return dsq

    def _check_food(self, food, screen):
        check = self.is_touch(food)
        if check:
            food.replace(screen)
            self._play_eat()
            self._timer -= self._timer_delta
        return check


def cal_movement():
    return settings.block_size // MOVEMENT_COUNTER
