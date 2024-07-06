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
        self._left_eye.pos = (x + radius, y)
        x, y = self._head.rect.midright
        self._right_eye.pos = (x - radius, y)
        self._left_eye.target = target
        self._right_eye.target = target

    def draw(self, screen, target):
        self.update(target)
        self._left_eye.draw(screen)
        self._right_eye.draw(screen)


class SnakeBody(ImageObject):
    def __init__(self, head: ImageObject, index):
        self._head = head
        self._queue = Queue()
        super(SnakeBody, self).__init__((-100, -100), settings.body1_image if index == 0 else settings.body2_image,
                                        settings.snake_size)
        self.add(STARTER_SIZE - 1)

    def draw(self, screen):
        screen.blit(self._image, self._pos)

    def delete(self, screen):
        x, y = self._queue.get()
        screen.fill(settings.background_color, (x, y, settings.block_size, settings.block_size))

    def add(self, value=1):
        value *= MOVEMENT_COUNTER
        for _ in range(value):
            self._queue.put((-100, -100))

    def repos(self, *_):
        self._pos = self._head.pos
        self._queue.put(self._pos)

    def reset(self):
        self._queue = Queue()
        self._pos = (-100, -100)
        self.add(STARTER_SIZE - 1)

    def __len__(self):
        return self._queue.qsize() // MOVEMENT_COUNTER


class Snake(ScreenObject):
    def __init__(self, screen: pygame.Surface, data, index: int = 0, players: int = 1):
        super(Snake, self).__init__((0, 0), (settings.block_size, settings.block_size))
        self._index = index
        self._players = players
        self._got_dir = False
        self._dsq = False
        self._direction = DIR_UP
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
        self._body = SnakeBody(self._head, self._index)
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
        movement = self._speed / MOVEMENT_COUNTER
        if self._direction == DIR_UP:
            y -= movement
        elif self._direction == DIR_DOWN:
            y += movement
        elif self._direction == DIR_RIGHT:
            x += movement
        else:
            x -= movement
        if self._teleport and self.on_grid:
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

    def _play_redirect(self):
        channel = pygame.mixer.Channel(SNAKE_CHANNEL)
        channel.set_volume(self._volume.value)
        channel.play(pygame.mixer.Sound(REDIRECT_SOUND))

    def _play_eat(self):
        channel = pygame.mixer.Channel(FOOD_CHANNEL)
        channel.set_volume(self._volume.value)
        channel.play(pygame.mixer.Sound(EAT_SOUND))

    def update(self, screen: pygame.Surface, food, data_zone):
        if self.on_grid:
            if self._got_dir is not False:
                self._direction = self._got_dir
                self._got_dir = False
        self._pos = self._next_pos
        if not self._check_food(food, screen):
            self._dsq = self._is_disqualified(screen, data_zone)
        self._body.repos()
        self._body.delete(screen)
        self._head.repos(self._pos, HEAD_DIRECTIONS[self._direction])
        self._body.draw(screen)
        self._head.draw(screen)
        self._eyes.draw(screen, food.pos)
        return self._dsq

    def set_direction(self, button):
        last_dir = self._got_dir
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
        if last_dir is not self._got_dir:
            self._play_redirect()

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
