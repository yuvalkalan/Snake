import random
from queue import Queue
from classes import *


class GameObject:
    def __init__(self, pos: POSITION, size: POSITION):
        self._pos = pos
        self._size = size

    @property
    def pos(self):
        return self._pos

    @property
    def size(self):
        return self._size

    @property
    def rect(self):
        return pygame.Rect(self._pos, self._size)

    def is_touch(self, other: {rect}):
        return self.rect.colliderect(other.rect)

    def draw(self, screen: pygame.Surface):
        pass

    def delete(self, screen):
        screen.fill(settings.background_color, self.rect)


class BlockObject(GameObject):
    def __init__(self, pos: POSITION, size: POSITION, color):
        super(BlockObject, self).__init__(pos, size)
        self._color = color

    def draw(self, screen):
        screen.fill(self._color, self.rect)


class ImageObject(GameObject):
    def __init__(self, pos, img_name, direction=0, color_key=WHITE):
        self._image = pygame.image.load(img_name).convert()
        self._image.set_colorkey(color_key)
        w, h = self._image.get_size()
        new_w = int(w / 19 * settings.block_size)
        new_h = int(w / 19 * settings.block_size)
        self._image = pygame.transform.scale(self._image, (new_w, new_h))
        super(ImageObject, self).__init__(pos, self._image.get_size())
        self._direction = direction

    @property
    def _display_image(self):
        return pygame.transform.rotate(self._image, self._direction)

    def draw(self, screen):
        screen.blit(self._display_image, self._pos)

    def repos(self, pos, direction=None):
        self._pos = pos
        if direction is not None:
            self._direction = direction


class GifObject(GameObject):
    def __init__(self, pos, folder, direction=0):
        self._images = []
        images = sorted([img for img in os.listdir(folder)], key=lambda f: int(f[:f.index('.')]))
        size = settings.delta_size
        for image in images:
            image = pygame.image.load(fr'{folder}\{image}')
            width, height = image.get_size()
            self._images.append(pygame.transform.scale(image, (int(width * size), int(height * size))))
        self._index = 0
        self._direction = direction
        super(GifObject, self).__init__(pos, self._images[0].get_size())

    @property
    def _display_image(self):
        img = pygame.transform.rotate(self._images[self._index], self._direction)
        self._index = (self._index + 1) % len(self._images)
        return img

    def draw(self, screen):
        screen.blit(self._display_image, self._pos)

    def repos(self, pos, direction=None):
        self._pos = pos
        if direction is not None:
            self._direction = direction


class Eye:
    def __init__(self, target, center, radius, screen):
        self._target = target
        self._center = center
        self._radius = radius
        w, h = screen.get_size()
        self._screen_radius = (w**2 + h**2) ** 0.5

    @property
    def distance(self):
        x1, y1 = self._center
        x2, y2 = self._target
        return ((x2-x1)**2 + (y1-y2)**2) ** 0.5

    @property
    def _eye_radius(self):
        return max(min(self._radius * (1 - self.distance / self._screen_radius)**5, self._radius*0.8), 3)

    def _closest(self, pos):
        x1, y1 = pos
        x2, y2 = self._center
        angle = math.atan2((y1 - y2), (x1 - x2))
        x = math.cos(angle) * (self._radius - self._eye_radius) + x2
        y = math.sin(angle) * (self._radius - self._eye_radius) + y2
        return round(x), round(y)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self._center, self._radius)
        pygame.draw.circle(screen, GREEN, self._closest(self._target), self._eye_radius)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center):
        self._center = center


class SnakeEyes:
    def __init__(self, head, target, screen):
        self._head = head
        x, y = self._head.rect.midleft
        radius = (self._head.rect.centerx - x) // 2
        self._left_eye = Eye(target, (x + radius, y), radius, screen)
        x, y = self._head.rect.midright
        self._right_eye = Eye(target, (x - radius, y), radius, screen)

    def set_target(self, target):
        x, y = self._head.rect.midleft
        radius = (self._head.rect.centerx - x) // 2
        self._left_eye.center = (x + radius, y)
        x, y = self._head.rect.midright
        self._right_eye.center = (x - radius, y)
        self._left_eye.target = target
        self._right_eye.target = target

    def draw(self, screen, target):
        self.set_target(target)
        self._left_eye.draw(screen)
        self._right_eye.draw(screen)


class SnakeBody(ImageObject):
    def __init__(self, head: ImageObject):
        self._head = head
        self._queue = Queue()
        super(SnakeBody, self).__init__((-100, -100), BODY_IMAGE)

    def draw(self, screen):
        screen.blit(self._image, self._pos)

    def delete(self, screen):
        x, y = self._queue.get()
        screen.fill(settings.background_color, (x, y, settings.block_size, settings.block_size))

    def add(self, value=1):
        value *= MOVEMENT_COUNTER
        while value:
            self._queue.put((-100, -100))
            value -= 1

    def repos(self, *_):
        self._queue.put(self._pos)
        self._pos = self._head.pos

    def reset(self):
        self._queue = Queue()
        self._pos = (-100, -100)

    def __len__(self):
        return self._queue.qsize() // MOVEMENT_COUNTER


class Snake(GameObject):
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
        self._head = ImageObject(self._pos, HEAD_IMAGE)
        self._eyes = SnakeEyes(self._head, (0, 0), screen)
        self._body = SnakeBody(self._head)
        self._volume = data.volume
        self.add(STARTER_SIZE - 1)
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
    def _front_pos(self):
        if self._direction == DIR_UP:
            return self.rect.midtop
        elif self._direction == DIR_RIGHT:
            x, y = self.rect.midright
            return x-1, y
        elif self._direction == DIR_DOWN:
            x, y = self.rect.midbottom
            return x, y-1
        return self.rect.midleft

    def _is_disqualified(self, screen: pygame.Surface, data_zone):
        if self.is_touch(data_zone):
            return not self._teleport
        try:
            color = screen.get_at(self._front_pos)[:-1]
            return color != settings.background_color and color != settings.food_color
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
        self._head.repos(self._pos)
        self._body.repos()
        self._body.draw(screen)
        if self.on_grid:
            if self._got_dir is not False:
                self._direction = self._got_dir
                self._got_dir = False
        self._pos = self._next_pos
        self.delete(screen)
        self._dsq = self._is_disqualified(screen, data_zone)
        self._check_food(food, screen)
        self._head.repos(self._pos, HEAD_DIRECTIONS[self._direction])
        self._head.draw(screen)
        self._eyes.draw(screen, food.pos)
        return self._dsq

    def delete(self, screen):
        self._body.delete(screen)

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

    def __len__(self):
        return len(self._body) + 1

    def reset(self, screen):
        self.set_starter_pos(screen)
        self._direction = DIR_UP
        self._body.reset()
        self.add(STARTER_SIZE - 1)
        self.draw(screen)


class BattleSnake(Snake):
    def __init__(self, screen: pygame.Surface, data, boundary_line: pygame.Rect, index: int = 0, players: int = 2):
        super(BattleSnake, self).__init__(screen, data, index, players)
        self._boundary_line = boundary_line

    def _is_disqualified(self, screen: pygame.Surface, data_zone):
        if self.is_touch(data_zone) or self._boundary_line.colliderect(self.rect):
            return not self._teleport
        try:
            color = screen.get_at(self._front_pos)[:-1]
            return color != settings.background_color and color != settings.food_color
        except IndexError:
            return not self._teleport

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


class Food(BlockObject):
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


class Obstacle(BlockObject):
    def __init__(self, snake: Snake, data_zone: BlockObject, screen: pygame.Surface):
        super(Obstacle, self).__init__((0, 0), (settings.block_size, settings.block_size), settings.body_color)
        self._direction = 0
        self._under_me = None
        self._snake_pointer = snake
        self._speed = settings.obstacle_speed // MOVEMENT_COUNTER
        self.start(screen, data_zone)

    def reset_pos(self, screen: pygame.Surface, data_zone):
        num = random.randint(0, 3)
        w = screen.get_rect().width - settings.block_size - 1
        h = screen.get_rect().height - data_zone.rect.height - settings.block_size
        if num == 0:
            pos = (random.randint(0, w), 0)
        elif num == 1:
            pos = (w, random.randint(0, h))
        elif num == 2:
            pos = (random.randint(0, w), h)
        else:
            pos = (0, random.randint(0, h))
        self._pos = pos

    def start(self, screen: pygame.Surface, data_zone):
        self.reset_pos(screen, data_zone)
        while self._is_dead(screen, data_zone):
            self.reset_pos(screen, data_zone)
        self.redirect()

    def redirect(self):
        x, y = self._pos
        snake_x, snake_y = self._snake_pointer.rect.center
        self._direction = math.atan2(y - snake_y, x - snake_x)

    def _is_dead(self, screen: pygame.Surface, data_zone):
        head = self.rect
        if self.is_touch(data_zone):
            return True
        poses = [head.topleft, head.topright, head.bottomleft, head.bottomright]
        try:
            for pos in poses:
                if screen.get_at(pos)[:-1] not in [settings.food_color, settings.background_color]:
                    return True
            return False
        except IndexError:
            return True

    def check_food(self, screen, food: Food):
        if self.is_touch(food):
            food.replace(screen)

    def update(self, screen, food, data_zone):
        self.delete(screen)
        x, y = self._pos
        x -= math.cos(self._direction) * self._speed
        y -= math.sin(self._direction) * self._speed
        self._pos = (x, y)
        if self._is_dead(screen, data_zone):
            self.start(screen, data_zone)
        self.check_food(screen, food)
        self.draw(screen)


class Error(Exception):
    """Base class for other exceptions"""
    pass


class EscPressed(Error):
    """Raised when the user press esc"""
    pass


class QuitPressed(Error):
    """Raised when the user close the pygame window"""
    pass


class UserDsq(Error):
    """Raised when the game end"""
    pass


class SettingsChanged(Error):
    """Raised when the user change the settings"""
    pass


class Timer:
    def __init__(self):
        self._value = 0

    def reset(self):
        self._value = 0

    def update(self):
        self._value += 1

    @property
    def value(self):
        return self._value

    def __str__(self):
        v = self._value // settings.refresh_rate
        h = int(v // 3600)
        m = (v - h * 3600) // 60
        s = v - h * 3600 - m * 60
        return f'{h:02}:{m:02}:{s:02}'


class DataZone(BlockObject):
    def __init__(self, screen: pygame.Surface, data, snakes: List[Snake]):
        x, y = screen_grids(screen)
        y = int(y - y * DATA_ZONE_SIZE) * settings.snake_speed
        w, h = screen.get_size()
        super(DataZone, self).__init__((0, y), (w, h - y), WHITE)
        self._snakes = snakes
        self._pause = True
        self._pause_msg = Message(self.rect.center, 'game paused!, click space to continue', settings.text_size, BLACK,
                                  CENTER)
        self._pos_gen = self.pos_generator()
        self._switcher = Switcher(self.text_pos, data)
        self._timer = Timer()
        self._msgs = [DataMessage(self.text_pos, 'score p{}: {}', settings.text_size, BLACK, value=snake,
                                  func=lambda s: (s.index+1, len(s))) for snake in snakes]
        self._msgs.append(DataMessage(self.text_pos, 'timer: {}', settings.text_size, BLACK, value=self._timer,
                                      func=lambda t: str(t)))
        self.draw(screen)

    @property
    def pause(self):
        return self._pause

    def draw(self, screen):
        self.delete(screen)
        super(DataZone, self).draw(screen)
        self._switcher.draw(screen)
        if self._switcher:
            for msg in self._msgs:
                msg.draw(screen)
        if self._pause:
            self._pause_msg.draw(screen)
        else:
            self._timer.update()

    def pos_generator(self):
        x, y = self._pos
        while True:
            yield x, y
            y += settings.text_size

    @property
    def text_pos(self):
        return next(self._pos_gen)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if self._switcher.is_touch_mouse():
                        self._switcher.change_mode()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._pause = not self._pause

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect)

    def reset(self, screen):
        self._pause = True
        self.draw(screen)
        self._timer.reset()

    @property
    def timer(self):
        return self._timer.value

    @property
    def timer_str(self):
        return str(self._timer)


def round_to_grid(pos):
    x, y = pos
    x = x - x % settings.snake_speed
    y = y - y % settings.snake_speed
    return x, y


def grid_to_pos(grid_pos):
    x, y = grid_pos
    return x * settings.snake_speed, y * settings.snake_speed


def resolution() -> POSITION:
    width, height = (int(BASE_RESOLUTION / RESOLUTION_RATIO), BASE_RESOLUTION)
    width = width - width % settings.base_snake_speed
    height = height - height % settings.base_snake_speed
    grid_w, grid_h = int(width // settings.base_snake_speed), int(height // settings.base_snake_speed)
    return grid_w * settings.snake_speed, grid_h * settings.snake_speed


def reset_game(screen: pygame.Surface, data: DataManager, snakes: List[Snake], foods: List[Food], data_zone: DataZone):
    restart_button = Button(screen.get_rect().center, 'game over! restart here', RED, 'click here to restart game',
                            settings.text_size, data, CENTER)
    restart = False
    data.delete(screen)
    while data.running and not restart:
        events = pygame.event.get()
        data.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                data.running = False
                raise QuitPressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if restart_button.is_touch_mouse():
                        restart = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise EscPressed
        restart_button.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)
    screen.fill(settings.background_color)
    for snake in snakes:
        snake.reset(screen)
    for food in foods:
        food.reset(screen)
    data_zone.reset(screen)
    data.empty()


def check_game_events(data: DataManager, data_zone: DataZone, snakes: List[Snake]):
    events = pygame.event.get()
    data.handle_events(events)
    data_zone.handle_events(events)
    for event in events:
        if event.type == pygame.QUIT:
            data.running = False
            raise QuitPressed
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT] and not data_zone.pause:
                snakes[0].set_direction(event.key)
            elif event.key in [pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a] and not data_zone.pause:
                snakes[len(snakes) - 1].set_direction(event.key)
            elif event.key == pygame.K_ESCAPE:
                raise EscPressed


def update_game(screen: pygame.Surface, data_zone: DataZone, snakes: List[Snake], foods: List[Food]):
    if not data_zone.pause:
        dsq = False
        for i, snake in enumerate(snakes):
            dsq = snake.update(screen, foods[i], data_zone) or dsq
        if dsq:
            raise UserDsq


def update_obstacles(screen: pygame.Surface, data_zone: DataZone, food: Food, snakes: List[Snake],
                     obstacles: List[Obstacle], obstacle_counter: int):
    if not data_zone.pause:
        for obstacle in obstacles:
            obstacle.update(screen, food, data_zone)
        obstacle_counter += 1
        if obstacle_counter >= 60 * MOVEMENT_COUNTER:
            obstacles.append(Obstacle(snakes[0], data_zone, screen))
            obstacle_counter = 0
    return obstacle_counter


def draw_game(screen: pygame.Surface, data: DataManager, data_zone: DataZone):
    data_zone.draw(screen)
    data.draw(screen)
    pygame.display.flip()
    clock.tick(settings.refresh_rate)


def get_battle_line(screen: pygame.Surface):
    grid_x, _ = screen_grids(screen)
    w, h = screen.get_size()
    x, y = screen.get_rect().center
    line_rect = pygame.Rect(0, 0, settings.snake_speed * 2 - 1 if grid_x % 2 == 0 else settings.block_size, h)
    line_rect.center = (x, y)
    line_rect.topleft = round_to_grid(line_rect.topleft)
    return line_rect


def snake_classic(screen: pygame.Surface, data: DataManager):
    screen.fill(settings.background_color)
    snakes = [Snake(screen, data)]
    food = Food(screen)
    data_zone = DataZone(screen, data, snakes)
    while data.running:
        try:
            while True:
                check_game_events(data, data_zone, snakes)
                update_game(screen, data_zone, snakes, [food])
                draw_game(screen, data, data_zone)
        except UserDsq:
            data += f'total score: {sum([len(snake) for snake in snakes])}'
            reset_game(screen, data, snakes, [food], data_zone)


def snake_obstacles(screen: pygame.Surface, data: DataManager):
    screen.fill(settings.background_color)
    snakes = [Snake(screen, data)]
    food = Food(screen)
    data_zone = DataZone(screen, data, snakes)
    while data.running:
        obstacle_counter = 0
        obstacles = [Obstacle(snakes[0], data_zone, screen)]
        try:
            while True:
                check_game_events(data, data_zone, snakes)
                update_game(screen, data_zone, snakes, [food])
                obstacle_counter = update_obstacles(screen, data_zone, food, snakes, obstacles, obstacle_counter)
                draw_game(screen, data, data_zone)
        except UserDsq:
            data += f'total score: {sum([len(snake) for snake in snakes])}'
            reset_game(screen, data, snakes, [food], data_zone)


def snake_battle(screen: pygame.Surface, data: DataManager):
    screen.fill(settings.background_color)
    line_rect = get_battle_line(screen)
    snakes = [BattleSnake(screen, data, line_rect, index, 2) for index in range(2)]
    foods = [BattleFood(screen, line_rect, index) for index in range(2)]
    data_zone = DataZone(screen, data, snakes)
    while data.running:
        try:
            while True:
                check_game_events(data, data_zone, snakes)
                update_game(screen, data_zone, snakes, foods)
                if data_zone.timer > BATTLE_TIMER * settings.refresh_rate:
                    raise UserDsq
                pygame.draw.rect(screen, settings.body_color, line_rect)
                draw_game(screen, data, data_zone)
        except UserDsq:
            winner_index = 1 + max(snakes, key=lambda s: (not s.dsq, len(s))).index
            data += f'p{winner_index} win! total score: {sum([len(snake) for snake in snakes])}'
            reset_game(screen, data, snakes, foods, data_zone)


def snake_coop(screen: pygame.Surface, data: DataManager):
    screen.fill(settings.background_color)
    snakes = [Snake(screen, data, index, 2) for index in range(2)]
    food = Food(screen)
    data_zone = DataZone(screen, data, snakes)
    while data.running:
        try:
            while True:
                check_game_events(data, data_zone, snakes)
                update_game(screen, data_zone, snakes, [food, food])
                draw_game(screen, data, data_zone)
        except UserDsq:
            data += f'total score: {sum([len(snake) for snake in snakes])}'
            reset_game(screen, data, snakes, [food], data_zone)


def snake_survival(screen: pygame.Surface, data: DataManager):
    screen.fill(settings.background_color)
    snakes = [SurvivalSnake(screen, data)]
    food = Food(screen)
    data_zone = DataZone(screen, data, snakes)
    while data.running:
        try:
            while True:
                check_game_events(data, data_zone, snakes)
                update_game(screen, data_zone, snakes, [food])
                draw_game(screen, data, data_zone)
        except UserDsq:
            data += f'total time: {data_zone.timer_str}'
            reset_game(screen, data, snakes, [food], data_zone)


def snake_survival_battle(screen: pygame.Surface, data: DataManager):
    screen.fill(settings.background_color)
    line_rect = get_battle_line(screen)
    snakes = [SurvivalBattleSnake(screen, data, line_rect, index, 2) for index in range(2)]
    foods = [BattleFood(screen, line_rect, index) for index in range(2)]
    data_zone = DataZone(screen, data, snakes)
    while data.running:
        try:
            while True:
                check_game_events(data, data_zone, snakes)
                update_game(screen, data_zone, snakes, foods)
                pygame.draw.rect(screen, settings.body_color, line_rect)
                draw_game(screen, data, data_zone)
        except UserDsq:
            winner_index = 1 + max(snakes, key=lambda s: (not s.dsq, len(s))).index
            data += f'p{winner_index} win! total time: {data_zone.timer_str}'
            reset_game(screen, data, snakes, foods, data_zone)


def pick_gameplay(screen, data: DataManager):
    data.delete(screen)
    pos = next_pos((100 * settings.delta_size, 100 * settings.delta_size), (0, settings.text_size * 2))
    buttons = {Button(next(pos), 'classic', RED, 'one player, until disqualified', settings.text_size,
                      data): snake_classic,
               Button(next(pos), 'obstacles', RED, 'one player, avoid obstacles', settings.text_size,
                      data): snake_obstacles,
               Button(next(pos), 'battle', RED, 'two players against each other', settings.text_size,
                      data): snake_battle,
               Button(next(pos), 'cooperation', RED, 'two players, together', settings.text_size,
                      data): snake_coop,
               Button(next(pos), 'survival', RED, 'eat food keep you small', settings.text_size,
                      data): snake_survival,
               Button(next(pos), 'survival battle', RED, '1v1 survival', settings.text_size,
                      data): snake_survival_battle}
    while data.running:
        events = pygame.event.get()
        data.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                data.running = False
                raise QuitPressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    for button in buttons:
                        if button.is_touch_mouse():
                            data.empty()
                            try:
                                buttons[button](screen, data)
                            except EscPressed:
                                pass
                            data.delete(screen)
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise EscPressed
        for button in buttons:
            button.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)


def submit_settings(conf_bars, conf_colors, teleport_button):
    with open(SETTING_FILE, 'wb+') as my_file:
        lst = [bar.real_value for bar in conf_bars]
        lst += [color.real_value for color in conf_colors]
        lst += [teleport_button.real_value]
        my_file.write(pickle.dumps(lst))
    settings.reset()
    raise SettingsChanged


def check_settings(conf_bars, conf_colors, teleport_button, data):
    colors = [color.real_value for color in conf_colors]
    if len(colors) != len(set(colors)):
        data += 'colors must be unique!'
        return False
    return True


def edit_settings(screen, data):
    bar_length = (1080 - 480) // 5
    pos = next_pos((100 * settings.delta_size, 100 * settings.delta_size), (0, settings.text_size * 2))
    conf_bars = [ScaleBar(next(pos), 'resolution', bar_length, data, settings.resolution, 480, 1080),
                 ScaleBar(next(pos), 'block size', bar_length, data, settings.base_block_size, 2, 50),
                 ScaleBar(next(pos), 'game speed', bar_length, data, settings.refresh_rate, 1, 50),
                 ScaleBar(next(pos), 'text size', bar_length, data, settings.base_text_size, 10, 40)]
    conf_colors = [ColorSelector(next(pos), 'head color', settings.head_color, settings.text_size, data),
                   ColorSelector(next(pos), 'body color', settings.body_color, settings.text_size, data),
                   ColorSelector(next(pos), 'background color', settings.background_color, settings.text_size, data,
                                 allow_black=True),
                   ColorSelector(next(pos), 'food color', settings.food_color, settings.text_size, data)]
    teleport_button = SelectionButton(next(pos), 'teleport', settings.teleport, settings.text_size, data)
    submit_button = Button(next(pos), 'submit!', YELLOW, 'click here to submit!', settings.text_size, data)
    reset_button = Button(next(pos), 'reset', RED, 'reset to default', settings.text_size, data)
    while data.running:
        events = pygame.event.get()
        data.handle_events(events)
        for bar in conf_bars:
            bar.active(events)
        for event in events:
            if event.type == pygame.QUIT:
                data.running = False
                raise QuitPressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise EscPressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if teleport_button.is_touch_mouse():
                        teleport_button.change_mode()
                    elif submit_button.is_touch_mouse():
                        if check_settings(conf_bars, conf_colors, teleport_button, data):
                            submit_settings(conf_bars, conf_colors, teleport_button)
                            raise SettingsChanged
                    elif reset_button.is_touch_mouse():
                        try:
                            os.remove(SETTING_FILE)
                            settings.reset()
                        except FileNotFoundError:
                            pass
                        raise SettingsChanged
                    else:
                        for color in conf_colors:
                            if color.is_touch_mouse():
                                color.change_color()
                                break
                elif event.button == MOUSE_RIGHT:
                    for color in conf_colors:
                        if color.is_touch_mouse():
                            color.change_color(False)
                            break
        for bar in conf_bars:
            bar.draw(screen)
        for color in conf_colors:
            color.draw(screen)
        teleport_button.draw(screen)
        submit_button.draw(screen)
        reset_button.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)


def lobby():
    screen = pygame.display.set_mode(resolution())
    pygame.display.set_caption(WINDOW_TITLE)

    data = DataManager(screen)

    start_button = Button((screen.get_rect().centerx, settings.text_size * 5), 'start game!', RED,
                          'click here to start game!', settings.text_size * 2, data, CENTER)
    settings_button = Button((screen.get_rect().centerx, settings.text_size * 12), 'settings', RED,
                             'click here to change settings!', settings.text_size * 2, data, CENTER)
    pygame.mixer.music.load(BACKGROUND_SOUND)
    pygame.mixer.music.play(-1)
    while data.running:
        events = pygame.event.get()
        data.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                data.running = False
                raise QuitPressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if start_button.is_touch_mouse():
                        try:
                            pick_gameplay(screen, data)
                        except EscPressed:
                            pass
                    elif settings_button.is_touch_mouse():
                        try:
                            edit_settings(screen, data)
                        except EscPressed:
                            pass
        start_button.draw(screen)
        settings_button.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)


def main():
    pygame.init()
    try:
        while True:
            try:
                lobby()
            except SettingsChanged:
                pass
    except QuitPressed:
        pass
    pygame.quit()


if __name__ == '__main__':
    main()
