from .snake import *
from .food import *


class Obstacle(GameBlock):
    def __init__(self, snake: Snake, data_zone: BlockObject, screen: pygame.Surface):
        super(Obstacle, self).__init__((0, 0), (settings.block_size, settings.block_size), RED)
        self._direction = 0
        self._under_me = None
        self._snake_pointer = snake
        self._speed = settings.obstacle_speed // MOVEMENT_COUNTER
        self._super_mode = False
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
        self._super_mode = False
        self._color = RED

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
            self._super_mode = True
            self._color = PURPLE

    def update(self, screen, food, data_zone):
        if self._super_mode:
            self.redirect()
        self.delete(screen)
        x, y = self._pos
        x -= math.cos(self._direction) * self._speed
        y -= math.sin(self._direction) * self._speed
        self._pos = (x, y)
        if self._is_dead(screen, data_zone):
            self.start(screen, data_zone)
        self.check_food(screen, food)
        self.draw(screen)


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
