import random
from queue import Queue
from classes import *


class BlockObject:
    def __init__(self, pos, size: Tuple[int, int], color):
        self._pos = pos
        self._size = size
        self._color = color

    def draw(self, screen):
        screen.fill(self._color, self.rect)

    def delete(self, screen):
        screen.fill(settings.background_color, self.rect)

    @property
    def rect(self):
        return pygame.Rect(self._pos, (self._size[0], self._size[1]))

    def is_touch(self, other):
        return self.rect.colliderect(other.rect)


class Snake(BlockObject):
    def __init__(self, screen: pygame.Surface, index: int = 0, players: int = 1):
        super(Snake, self).__init__((0, 0), (settings.block_size, settings.block_size),
                                    settings.head_color)
        self._index = index
        self._players = players
        self._got_dir = True
        self._dsq = False
        self._direction = DIR_UP
        self._speed = settings.snake_speed
        self._queue = Queue()
        width, height = screen_grids(screen)
        height = int(height - height * DATA_ZONE_SIZE)
        self._grid_width = width
        self._grid_height = height
        self._teleport = settings.teleport
        self.set_starter_pos(screen)
        self.add(STARTER_SIZE - 1)
        self.draw(screen)

    def set_starter_pos(self, screen):
        x, y = screen.get_size()
        x = x // (self._players + 1) * (self._index + 1)
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

    def _is_disqualified(self, screen: pygame.Surface, data_zone):
        head = self.rect
        if self.is_touch(data_zone):
            return True
        top_left = head.topleft
        top_right = head.topright
        bottom_left = head.bottomleft
        bottom_right = head.bottomright
        try:
            dsq = False
            for color in [settings.head_color, settings.body_color]:
                dsq = dsq or color in [screen.get_at(top_left)[:-1], screen.get_at(top_right)[:-1],
                                       screen.get_at(bottom_left)[:-1],
                                       screen.get_at(bottom_right)[:-1]]
            return dsq
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

    @property
    def index(self):
        return self._index

    @property
    def dsq(self):
        return self._dsq

    def update(self, screen: pygame.Surface, food, data_zone):
        self._got_dir = False
        self._queue.put(self._pos)
        self._color = settings.body_color
        self.draw(screen)
        self._pos = self._next_pos
        self.delete(screen)
        self._dsq = self._is_disqualified(screen, data_zone)
        self._check_food(food, screen)
        self._color = settings.head_color
        self.draw(screen)
        return self._dsq

    def delete(self, screen):
        x, y = self._queue.get()
        if not x < 0 or y < 0:
            screen.fill(settings.background_color, pygame.Rect(x, y, self._size[0], self._size[1]))

    def set_direction(self, button):
        if not self._got_dir:
            if button in P2_CVT_KEYS:
                button = P2_CVT_KEYS[button]
            if button == pygame.K_UP and self._direction not in [DIR_UP, DIR_DOWN]:
                self._direction = DIR_UP
                self._got_dir = True
            elif button == pygame.K_DOWN and self._direction not in [DIR_UP, DIR_DOWN]:
                self._direction = DIR_DOWN
                self._got_dir = True
            elif button == pygame.K_RIGHT and self._direction not in [DIR_RIGHT, DIR_LEFT]:
                self._direction = DIR_RIGHT
                self._got_dir = True
            elif button == pygame.K_LEFT and self._direction not in [DIR_RIGHT, DIR_LEFT]:
                self._direction = DIR_LEFT
                self._got_dir = True

    @property
    def optional_arrows(self):
        if self._direction in [DIR_UP, DIR_DOWN]:
            return [pygame.K_RIGHT, pygame.K_LEFT]
        return [pygame.K_UP, pygame.K_DOWN]

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
        self.set_starter_pos(screen)
        self._direction = DIR_UP
        self._queue = Queue()
        self.add(STARTER_SIZE - 1)
        self.draw(screen)


class BattleSnake(Snake):
    def __init__(self, screen: pygame.Surface, boundary_line: pygame.Rect, index: int = 0, players: int = 2):
        super(BattleSnake, self).__init__(screen, index, players)
        self._boundary_line = boundary_line

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
                x = self._boundary_line.left - settings.snake_speed
            elif x > self._boundary_line.left - settings.snake_speed and self._index == 0:
                x = 0
            elif x < self._boundary_line.right and self.index == 1:
                x = self._max_x
            elif x > self._max_x:
                x = self._boundary_line.right
            elif y < 0:
                y = (self._grid_height - 1) * settings.snake_speed
            elif y > self._max_y:
                y = 0
        return x, y


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
            w_rnd = random.randint(0, width // 2) * settings.snake_speed
        else:
            w_rnd = random.randint(width // 2, width) * settings.snake_speed
        h_rnd = random.randint(0, height) * settings.snake_speed
        self._pos = (w_rnd, h_rnd)
        while not self._pos_ok(screen, last_pos):
            if self._index == 0:
                w_rnd = random.randint(0, width // 2) * settings.snake_speed
            else:
                w_rnd = random.randint(width // 2, width) * settings.snake_speed
            h_rnd = random.randint(0, height) * settings.snake_speed
            self._pos = (w_rnd, h_rnd)


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
    def __init__(self, screen: pygame.Surface, snakes: List[Snake]):
        x, y = screen_grids(screen)
        y = int(y - y * DATA_ZONE_SIZE) * settings.snake_speed
        w, h = screen.get_size()
        super(DataZone, self).__init__((0, y), (w, h - y), WHITE)
        self._snakes = snakes
        self._pause = True
        self._pause_msg = Message(self.rect.center, 'game paused!, click space to continue', settings.text_size, BLACK,
                                  CENTER)

        self._pos_gen = self.pos_generator()
        self._switcher = Switcher(self.text_pos)
        self._timer = Timer()
        self._msgs = [DataMessage(self.text_pos, 'score p{}: {}', settings.text_size, BLACK, value=snake,
                                  func=lambda s: (s.index+1, len(s))) for snake in snakes]
        self._msgs.append(DataMessage(self.text_pos, 'timer: {}', settings.text_size, BLACK, value=self._timer,
                                      func=lambda t: str(t)))
        x1, y1 = self.rect.topright
        x2, y2 = self.rect.bottomright
        self._volume = VolumeBar((x1 - 50 * settings.delta_size, y1), y2 - y1, 0)

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
        if self._volume.active(events):
            pygame.mixer.music.set_volume(self._volume.value)
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
    return x * settings.snake_speed, y * settings.snake_speed


def resolution() -> POSITION:
    width, height = (int(BASE_RESOLUTION / RESOLUTION_RATIO), BASE_RESOLUTION)
    width = width - width % settings.base_snake_speed
    height = height - height % settings.base_snake_speed
    grid_w, grid_h = int(width // settings.base_snake_speed), int(height // settings.base_snake_speed)
    return grid_w * settings.snake_speed, grid_h * settings.snake_speed


def reset_game(screen, running, snakes, foods: List[Food], data_zone, temp_msgs):
    restart_button = Button(screen.get_rect().center, 'game over! restart here', RED, 'click here to restart game',
                            settings.text_size, CENTER)
    restart = False
    esc_pressed = False
    background_img = pygame.transform.scale(pygame.image.load(BACKGROUND_IMG), screen.get_size())
    screen.blit(background_img, (0, 0))
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
        restart_button.draw(screen)
        temp_msgs.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        screen.blit(background_img, (0, 0))
    screen.fill(settings.background_color)
    for snake in snakes:
        snake.reset(screen)
    for food in foods:
        food.reset(screen)
    data_zone.reset(screen)
    return running, esc_pressed


def snake_classic(screen, running, temp_msgs):
    screen.fill(settings.background_color)
    snakes = [Snake(screen)]
    food = Food(screen)
    data_zone = DataZone(screen, snakes)
    esc_pressed = False
    while running:
        temp_msgs.empty()
        while running:
            events = pygame.event.get()
            data_zone.handle_events(events)
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT] and not data_zone.pause:
                        snakes[0].set_direction(event.key)
                    elif event.key == pygame.K_ESCAPE:
                        esc_pressed = True
            if esc_pressed:
                break
            if not data_zone.pause:
                dsq = False
                for snake in snakes:
                    dsq = snake.update(screen, food, data_zone) or dsq
                if dsq:
                    break
            data_zone.draw(screen)
            pygame.display.flip()
            clock.tick(settings.refresh_rate)
        if esc_pressed:
            break
        temp_msgs += TempMsg(f'total score: {sum([len(snake) for snake in snakes])}')
        running, esc_pressed = reset_game(screen, running, snakes, [food], data_zone, temp_msgs)
        if esc_pressed:
            break
    return running


def snake_obstacles(screen, running, temp_msgs):
    return running


def snake_battle(screen, running, temp_msgs):
    screen.fill(settings.background_color)
    width, height = screen_grids(screen)
    x, y = round_to_grid(screen.get_rect().midtop)
    line_start = (x if width % 2 == 1 else x - settings.block_size, y)
    x, y = round_to_grid(screen.get_rect().midbottom)
    line_size = (settings.block_size if width % 2 == 1 else settings.block_size*2, y)
    line_rect = pygame.Rect(line_start + line_size)
    snakes = [BattleSnake(screen, line_rect, index, 2) for index in range(2)]
    foods = [BattleFood(screen, line_rect, index) for index in range(2)]
    data_zone = DataZone(screen, snakes)
    esc_pressed = False
    while running:
        pygame.draw.rect(screen, settings.body_color, line_rect)
        temp_msgs.empty()
        while running:
            events = pygame.event.get()
            data_zone.handle_events(events)
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT] and not data_zone.pause:
                        snakes[0].set_direction(event.key)
                    elif event.key in [pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a] and not data_zone.pause:
                        snakes[1].set_direction(event.key)
                    elif event.key == pygame.K_ESCAPE:
                        esc_pressed = True
                    elif event.key == pygame.K_z:
                        for snake in snakes:
                            snake.add(1)
            if esc_pressed:
                break
            if not data_zone.pause:
                dsq = False
                for i, snake in enumerate(snakes):
                    dsq = snake.update(screen, foods[i], data_zone) or dsq
                if dsq:
                    break
            if data_zone.timer > BATTLE_TIMER * settings.refresh_rate:
                break
            data_zone.draw(screen)
            pygame.display.flip()
            clock.tick(settings.refresh_rate)
        if esc_pressed:
            break
        winner_index = 1 + max(snakes, key=lambda s: (not s.dsq, len(s))).index
        temp_msgs += TempMsg(f'p{winner_index} win! total score: {sum([len(snake) for snake in snakes])}')
        running, esc_pressed = reset_game(screen, running, snakes, foods, data_zone, temp_msgs)
        if esc_pressed:
            break
    return running


def snake_coop(screen: pygame.Surface, running, temp_msgs):
    screen.fill(settings.background_color)
    snakes = [Snake(screen, index, 2) for index in range(2)]
    food = Food(screen)
    data_zone = DataZone(screen, snakes)
    esc_pressed = False
    while running:
        temp_msgs.empty()
        while running:
            events = pygame.event.get()
            data_zone.handle_events(events)
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT] and not data_zone.pause:
                        snakes[0].set_direction(event.key)
                    elif event.key in [pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a] and not data_zone.pause:
                        snakes[1].set_direction(event.key)
                    elif event.key == pygame.K_ESCAPE:
                        esc_pressed = True
                    elif event.key == pygame.K_z:
                        for snake in snakes:
                            snake.add(1)
            if esc_pressed:
                break
            if not data_zone.pause:
                dsq = False
                for snake in snakes:
                    dsq = snake.update(screen, food, data_zone) or dsq
                if dsq:
                    break
            data_zone.draw(screen)
            pygame.display.flip()
            clock.tick(settings.refresh_rate)
        if esc_pressed:
            break
        temp_msgs += TempMsg(f'total score: {sum([len(snake) for snake in snakes])}')
        running, esc_pressed = reset_game(screen, running, snakes, [food], data_zone, temp_msgs)
        if esc_pressed:
            break
    return running


def pick_gameplay(screen, running, background_img, temp_msgs):
    screen.blit(background_img, (0, 0))
    pos = next_pos((100 * settings.delta_size, 100 * settings.delta_size), (0, settings.text_size * 2))
    buttons = {Button(next(pos), 'classic', RED, 'one player, until disqualified', settings.text_size): snake_classic,
               Button(next(pos), 'obstacles', RED, 'one player, avoid obstacles', settings.text_size): snake_obstacles,
               Button(next(pos), 'battle', RED, 'two players against each other', settings.text_size): snake_battle,
               Button(next(pos), 'cooperation', RED, 'two players, together', settings.text_size): snake_coop}
    esc_pressed = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    for button in buttons:
                        if button.is_touch_mouse():
                            running = buttons[button](screen, running, temp_msgs)
                            screen.blit(background_img, (0, 0))
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    esc_pressed = True
        if esc_pressed:
            break
        for button in buttons:
            button.draw(screen)
        temp_msgs.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        screen.blit(background_img, (0, 0))
    return running


def submit_settings(conf_bars, conf_colors, teleport_button, temp_msgs):
    with open(SETTING_FILE, 'wb+') as my_file:
        lst = [bar.real_value for bar in conf_bars]
        lst += [color.real_value for color in conf_colors]
        lst += [teleport_button.real_value]
        my_file.write(pickle.dumps(lst))
    settings.reset()


def check_settings(conf_bars, conf_colors, teleport_button, temp_msgs):
    colors = [color.real_value for color in conf_colors]
    if len(colors) != len(set(colors)):
        temp_msgs += TempMsg('colors must be unique!')
        return False
    return True


def edit_settings(screen, running, background_img, temp_msgs):
    esc_pressed = False
    bar_length = (1080 - 480) // 5
    pos = next_pos((100 * settings.delta_size, 100 * settings.delta_size), (0, settings.text_size * 2))
    conf_bars = [ScaleBar(next(pos), 'resolution', bar_length, settings.resolution, 480, 1080),
                 ScaleBar(next(pos), 'block size', bar_length, settings.base_block_size, 2, 50),
                 ScaleBar(next(pos), 'game speed', bar_length, settings.refresh_rate, 1, 40),
                 ScaleBar(next(pos), 'text size', bar_length, settings.base_text_size, 10, 40)]
    conf_colors = [ColorSelector(next(pos), 'head color', settings.head_color, settings.text_size),
                   ColorSelector(next(pos), 'body color', settings.body_color, settings.text_size),
                   ColorSelector(next(pos), 'background color', settings.background_color, settings.text_size,
                                 allow_black=True),
                   ColorSelector(next(pos), 'food color', settings.food_color, settings.text_size)]
    teleport_button = SelectionButton(next(pos), 'teleport', settings.teleport, settings.text_size)
    submit_button = Button(next(pos), 'submit!', YELLOW, 'click here to submit!', settings.text_size)
    while running:
        events = pygame.event.get()
        for bar in conf_bars:
            bar.active(events)
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
                    elif submit_button.is_touch_mouse():
                        if check_settings(conf_bars, conf_colors, teleport_button, temp_msgs):
                            submit_settings(conf_bars, conf_colors, teleport_button, temp_msgs)
                            esc_pressed = True
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
        if esc_pressed:
            break
        for bar in conf_bars:
            bar.draw(screen)
        for color in conf_colors:
            color.draw(screen)
        teleport_button.draw(screen)
        submit_button.draw(screen)
        temp_msgs.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        screen.blit(background_img, (0, 0))
    return running


def main():
    running = True
    reset = True
    pygame.init()
    while reset and running:
        reset = False
        screen = pygame.display.set_mode(resolution())
        background_img = pygame.transform.scale(pygame.image.load(BACKGROUND_IMG), screen.get_size())
        pygame.display.set_caption(WINDOW_TITLE)
        start_button = Button((screen.get_rect().centerx, settings.text_size * 5), 'start game!', RED,
                              'click here to start game!', settings.text_size * 2, CENTER)
        settings_button = Button((screen.get_rect().centerx, settings.text_size * 12), 'settings', RED,
                                 'click here to change settings!', settings.text_size * 2, CENTER)
        temp_msgs = TempMsgList(screen)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == MOUSE_LEFT:
                        if start_button.is_touch_mouse():
                            running = pick_gameplay(screen, running, background_img, temp_msgs)
                        elif settings_button.is_touch_mouse():
                            running = edit_settings(screen, running, background_img, temp_msgs)
                            if settings.has_change:
                                reset = True
                                break
            if reset:
                break
            start_button.draw(screen)
            settings_button.draw(screen)
            temp_msgs.draw()
            pygame.display.flip()
            clock.tick(LOBBY_REFRESH_RATE)
            screen.blit(background_img, (0, 0))
    pygame.quit()


if __name__ == '__main__':
    main()
