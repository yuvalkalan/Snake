from .classes import *


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
                pygame.draw.rect(screen, RED, line_rect)
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
                pygame.draw.rect(screen, RED, line_rect)
                draw_game(screen, data, data_zone)
        except UserDsq:
            winner_index = 1 + max(snakes, key=lambda s: (not s.dsq, len(s))).index
            data += f'p{winner_index} win! total time: {data_zone.timer_str}'
            reset_game(screen, data, snakes, foods, data_zone)
