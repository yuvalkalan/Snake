import random
from queue import Queue

import pygame.event

from classes import *


class BlockObject:
    def __init__(self, pos, size: Tuple[int, int], color):
        self._pos = pos
        self._size = size
        self._color = color

    def draw(self, screen):
        screen.fill(self._color, self.rect)

    def delete(self, screen):
        screen.fill(BACKGROUND_COLOR, self.rect)

    @property
    def rect(self):
        return pygame.Rect(self._pos, (self._size[0], self._size[1]))

    def is_touch(self, other):
        return self.rect.colliderect(other.rect)


class Snake(BlockObject):
    def __init__(self, screen: pygame.Surface):
        super(Snake, self).__init__(round_to_grid(screen.get_rect().center), (settings.block_size, settings.block_size),
                                    HEAD_COLOR)
        self._direction = DIR_UP
        self._speed = settings.snake_speed
        self._queue = Queue()
        width, height = screen_grids(screen)
        height = int(height - height * DATA_ZONE_SIZE)
        self._grid_width = width
        self._grid_height = height
        self._teleport = TELEPORT
        self.add(STARTER_SIZE-1)
        self.draw(screen)

    @property
    def _grid_size(self):
        return self._grid_width * self._grid_height

    @property
    def _max_x(self):
        return (self._grid_width - 1) * settings.snake_speed

    @property
    def _max_y(self):
        return (self._grid_height - 1) * settings.snake_speed

    def _is_disqualified(self, screen: pygame.Surface, data_zone):
        head = self.rect
        if self.is_touch(data_zone):
            return True
        top_left = head.topleft
        top_right = head.topright
        bottom_left = head.bottomleft
        bottom_right = head.bottomright
        try:
            return BODY_COLOR in [screen.get_at(top_left)[:-1],
                                  screen.get_at(top_right)[:-1],
                                  screen.get_at(bottom_left)[:-1],
                                  screen.get_at(bottom_right)[:-1]]
        except IndexError:
            return True

    @property
    def _next_pos(self):
        x, y = self._pos
        if self._direction == DIR_UP:
            y -= self._speed
        elif self._direction == DIR_DOWN:
            y += self._speed
        elif self._direction == DIR_RIGHT:
            x += self._speed
        else:
            x -= self._speed
        if self._teleport:
            if x < 0:
                x = (self._grid_width - 1) * settings.snake_speed
            elif x > self._max_x:
                x = 0
            elif y < 0:
                y = (self._grid_height - 1) * settings.snake_speed
            elif y > self._max_y:
                y = 0
        return x, y

    def update(self, screen: pygame.Surface, food, data_zone):
        self._queue.put(self._pos)
        self._color = BODY_COLOR
        self.draw(screen)
        self._pos = self._next_pos
        self.delete(screen)
        dsq = self._is_disqualified(screen, data_zone)
        self._check_food(food, screen)
        self._color = HEAD_COLOR
        self.draw(screen)
        return dsq

    def delete(self, screen):
        x, y = self._queue.get()
        if not x < 0 or y < 0:
            screen.fill(BACKGROUND_COLOR, pygame.Rect(x, y, self._size[0], self._size[1]))

    def set_direction(self, button):
        if button == pygame.K_UP and self._direction not in [DIR_UP, DIR_DOWN]:
            self._direction = DIR_UP
        elif button == pygame.K_DOWN and self._direction not in [DIR_UP, DIR_DOWN]:
            self._direction = DIR_DOWN
        elif button == pygame.K_RIGHT and self._direction not in [DIR_RIGHT, DIR_LEFT]:
            self._direction = DIR_RIGHT
        elif button == pygame.K_LEFT and self._direction not in [DIR_RIGHT, DIR_LEFT]:
            self._direction = DIR_LEFT

    def add(self, value=1):
        while value:
            self._queue.put((-100, -100))
            value -= 1

    def _check_food(self, food, screen):
        check = self.is_touch(food)
        if check:
            food.delete(screen)
            food.gen_pos(screen)
            food.draw(screen)
            self.add(1)

    def __len__(self):
        return self._queue.qsize() + 1

    def reset(self, screen):
        self._pos = round_to_grid(screen.get_rect().center)
        self._direction = DIR_UP
        self._queue = Queue()
        self.add(STARTER_SIZE - 1)
        self.draw(screen)


class Food(BlockObject):
    def __init__(self, screen: pygame.Surface):
        super(Food, self).__init__((0, 0), (settings.block_size, settings.block_size), YELLOW)
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
            return [top_left, top_right, bottom_left, bottom_right].count(BACKGROUND_COLOR) == 4
        except IndexError:
            return False

    def gen_pos(self, screen: pygame.Surface):
        width, height = screen_grids(screen)
        height = int(height - height * DATA_ZONE_SIZE-1)
        last_pos = self._pos
        self._pos = (random.randint(0, width) * settings.snake_speed, random.randint(0, height) * settings.snake_speed)
        while not self._pos_ok(screen, last_pos):
            self._pos = (random.randint(0, width) * settings.snake_speed,
                         random.randint(0, height) * settings.snake_speed)

    def reset(self, screen):
        self.gen_pos(screen)
        self.draw(screen)


class DataZone(BlockObject):
    def __init__(self, screen: pygame.Surface, snake: Snake, food: Food):
        x, y = screen_grids(screen)
        y = int(y - y * DATA_ZONE_SIZE) * settings.snake_speed
        w, h = screen.get_size()
        super(DataZone, self).__init__((0, y), (w, h-y), WHITE)
        self._snake = snake
        self._food = food
        self._pause = True
        self._pause_msg = Message(self.rect.center, 'game paused!, click space to continue', settings.text_size, BLACK,
                                  CENTER)
        self._pos_gen = self.pos_generator()
        self._switcher = Switcher(self.text_pos)
        x1, y1 = self.rect.topright
        x2, y2 = self.rect.bottomright
        self._volume = VolumeBar((x1-50 * settings.delta_size, y1), y2 - y1, 0)
        self._msgs = [DataMessage(self.text_pos, 'score: {}', settings.text_size, BLACK, value=self._snake,
                                  func=lambda s: len(s)),
                      DataMessage(self.text_pos, 'food pos: ({}, {})', settings.text_size, BLACK, value=self._food,
                                  func=lambda f: f.rect.topleft),
                      DataMessage(self.text_pos, 'snake pos: ({}, {})', settings.text_size, BLACK, value=self._snake,
                                  func=lambda s: s.rect.topleft)
                      ]
        self.draw(screen)

    @property
    def pause(self):
        return self._pause

    def draw(self, screen):
        self.delete(screen)
        super(DataZone, self).draw(screen)
        self._switcher.draw(screen)
        self._volume.draw(screen)
        if self._switcher:
            for msg in self._msgs:
                msg.draw(screen)
        if self._pause:
            self._pause_msg.draw(screen)

    def pos_generator(self):
        x, y = self._pos
        while True:
            yield x, y
            y += settings.text_size

    @property
    def text_pos(self):
        return next(self._pos_gen)

    def handle_events(self, events):
        self._volume.active(events)
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


def round_to_grid(pos):
    x, y = pos
    x = x - x % settings.snake_speed
    y = y - y % settings.snake_speed
    return x, y


def screen_grids(screen: pygame.Surface):
    width, height = screen.get_size()
    return width // settings.snake_speed, height // settings.snake_speed


def grid_to_pos(grid_pos):
    x, y = grid_pos
    return x*settings.snake_speed, y*settings.snake_speed


def resolution() -> POSITION:
    width, height = (int(BASE_RESOLUTION/RESOLUTION_RATIO), BASE_RESOLUTION)
    width = width - width % settings.base_snake_speed
    height = height - height % settings.base_snake_speed
    grid_w, grid_h = int(width // settings.base_snake_speed), int(height // settings.base_snake_speed)
    return grid_w * settings.snake_speed, grid_h * settings.snake_speed


def reset_game(screen, running, snake, food, data_zone):
    restart_button = Button(screen.get_rect().center, 'game over! restart here', RED, 'click here to restart game',
                            settings.text_size, CENTER)
    restart = False
    esc_pressed = False
    while running and not restart:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if restart_button.is_touch_mouse():
                        restart = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    esc_pressed = True
        if esc_pressed:
            break
        screen.fill(BACKGROUND_COLOR)
        restart_button.draw(screen)
        pygame.display.flip()
    screen.fill(BACKGROUND_COLOR)
    snake.reset(screen)
    food.reset(screen)
    data_zone.reset(screen)
    return running, esc_pressed


def snake_game(screen, running):
    screen.fill(BACKGROUND_COLOR)
    snake = Snake(screen)
    food = Food(screen)
    data_zone = DataZone(screen, snake, food)
    clock = pygame.time.Clock()
    esc_pressed = False
    while running:
        while running:
            new_dir = []
            next_dir = None
            events = pygame.event.get()
            data_zone.handle_events(events)
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT] and not data_zone.pause:
                        new_dir.append(event)
                    elif event.key == pygame.K_a:
                        snake.add(1)
                    elif event.key == pygame.K_ESCAPE:
                        esc_pressed = True
            if esc_pressed:
                break
            if new_dir:
                snake.set_direction(new_dir[0].key)
                if len(new_dir) > 1:
                    next_dir = new_dir[1]
            if not data_zone.pause:
                dsq = snake.update(screen, food, data_zone)
                if dsq:
                    print(len(snake))
                    break
            data_zone.draw(screen)
            pygame.display.flip()
            clock.tick(settings.refresh_rate)
            if next_dir:
                snake.set_direction(next_dir.key)
        if esc_pressed:
            break
        running, esc_pressed = reset_game(screen, running, snake, food, data_zone)
        if esc_pressed:
            break
    return running


def submit_settings(res_bar, block_size_bar, speed_bar, text_size_bar):
    with open(SETTING_FILE, 'w+') as my_file:
        my_file.write(str(res_bar.real_value) + '\n')
        my_file.write(str(block_size_bar.real_value) + '\n')
        my_file.write(str(speed_bar.real_value) + '\n')
        my_file.write(str(text_size_bar.real_value) + '\n')
    settings.reset()


def edit_settings(screen, running):
    screen.fill(BACKGROUND_COLOR)
    esc_pressed = False
    bar_length = (1080-480)//5
    pos = next_pos((100*settings.delta_size, 100*settings.delta_size), (0, settings.text_size * 2))

    res_bar = ScaleBar(next(pos), 'resolution', bar_length, settings.resolution, 480, 1080)
    block_size_bar = ScaleBar(next(pos), 'block size', bar_length, settings.base_block_size, 2, 50)
    speed_bar = ScaleBar(next(pos), 'game speed', bar_length, settings.refresh_rate, 1, 40)
    text_size_bar = ScaleBar(next(pos), 'text size', bar_length, settings.base_text_size, 10, 40)
    teleport_button = SelectionButton(next(pos), 'teleport', TELEPORT, settings.text_size)
    head_color = ColorSelector(next(pos), 'head color', HEAD_COLOR, settings.text_size)
    body_color = ColorSelector(next(pos), 'body color', BODY_COLOR, settings.text_size)
    bg_color = ColorSelector(next(pos), 'background color', BACKGROUND_COLOR, settings.text_size, allow_black=True)

    submit_button = Button(next(pos), 'submit!', YELLOW, 'click here to submit!', settings.text_size)
    while running:
        events = pygame.event.get()
        res_bar.active(events)
        block_size_bar.active(events)
        speed_bar.active(events)
        text_size_bar.active(events)
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    esc_pressed = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if teleport_button.is_touch_mouse():
                        teleport_button.change_mode()
                    elif head_color.is_touch_mouse():
                        head_color.change_color()
                    elif body_color.is_touch_mouse():
                        body_color.change_color()
                    elif bg_color.is_touch_mouse():
                        bg_color.change_color()
                    elif submit_button.is_touch_mouse():
                        submit_settings(res_bar, block_size_bar, speed_bar, text_size_bar)
                        esc_pressed = True
                elif event.button == MOUSE_RIGHT:
                    if head_color.is_touch_mouse():
                        head_color.change_color(False)
                    elif body_color.is_touch_mouse():
                        body_color.change_color(False)
                    elif bg_color.is_touch_mouse():
                        bg_color.change_color(False)
        if esc_pressed:
            break
        res_bar.draw(screen)
        block_size_bar.draw(screen)
        speed_bar.draw(screen)
        text_size_bar.draw(screen)
        teleport_button.draw(screen)
        head_color.draw(screen)
        body_color.draw(screen)
        bg_color.draw(screen)
        submit_button.draw(screen)
        pygame.display.flip()
        screen.fill(BACKGROUND_COLOR)
    return running


def main():
    running = True
    reset = True
    while reset and running:
        reset = False
        pygame.init()
        screen = pygame.display.set_mode(resolution())
        pygame.display.set_caption(WINDOW_TITLE)
        screen.fill(BACKGROUND_COLOR)
        start_button = Button((screen.get_rect().centerx, settings.text_size*5), 'start game!', RED,
                              'click here to start game!', settings.text_size*2, CENTER)
        settings_button = Button((screen.get_rect().centerx, settings.text_size*12), 'settings', RED,
                                 'click here to change settings!', settings.text_size*2, CENTER)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == MOUSE_LEFT:
                        if start_button.is_touch_mouse():
                            running = snake_game(screen, running)
                        elif settings_button.is_touch_mouse():
                            running = edit_settings(screen, running)
                            if settings.has_change:
                                reset = True
                                break
            if reset:
                break
            start_button.draw(screen)
            settings_button.draw(screen)
            pygame.display.flip()
            screen.fill(BACKGROUND_COLOR)
    pygame.quit()


if __name__ == '__main__':
    main()
