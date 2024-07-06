import os
from game import *
from paint import *


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


def edit_skin(screen: pygame.Surface, data: DataManager) -> List[ImageObject]:
    pos = next_pos((100 * settings.delta_size, 100 * settings.delta_size), (0, settings.block_size * 2.5))
    paint_bar = PaintBar(pos, data)
    x, y = next(pos)
    snake2_pos = next_pos((x + settings.block_size * 2.5, y), (0, settings.block_size * 2.5))
    image_editors = [ImageEditor((x, y), settings.head1_image, paint_bar),
                     ImageEditor(next(snake2_pos), settings.head2_image, paint_bar),
                     ImageEditor(next(pos), settings.body1_image, paint_bar),
                     ImageEditor(next(snake2_pos), settings.body2_image, paint_bar)]
    save_button = Button(next(pos), 'save changes!', YELLOW, '', settings.text_size, data)
    reset_button = Button(next(pos), 'reset', RED, '', settings.text_size, data)
    while data.running:
        events = pygame.event.get()
        data.handle_events(events)
        paint_bar.active(events)
        for image in image_editors:
            image.active(events)
        for event in events:
            if event.type == pygame.QUIT:
                data.running = False
                raise QuitPressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise EscPressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if save_button.is_touch_mouse():
                        return image_editors
                    elif reset_button.is_touch_mouse():
                        return [ImageEditor((x, y), HEAD_IMAGE, paint_bar),
                                ImageEditor(next(snake2_pos), HEAD_IMAGE, paint_bar),
                                ImageEditor(next(pos), BODY_IMAGE, paint_bar),
                                ImageEditor(next(snake2_pos), BODY_IMAGE, paint_bar)]
        save_button.draw(screen)
        reset_button.draw(screen)
        for image in image_editors:
            image.draw(screen)
        paint_bar.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)


def edit_settings(screen: pygame.Surface, data: DataManager):
    bar_length = (1080 - 480) // 5
    pos = next_pos((100 * settings.delta_size, 100 * settings.delta_size), (0, settings.text_size * 2))
    conf_bars = [ScaleBar(next(pos), 'resolution', bar_length, data, settings.resolution, 480, 1080),
                 ScaleBar(next(pos), 'block size', bar_length, data, settings.base_block_size, 2, 50),
                 ScaleBar(next(pos), 'game speed', bar_length, data, settings.refresh_rate, 1, 50),
                 ScaleBar(next(pos), 'text size', bar_length, data, settings.base_text_size, 10, 40)]
    buttons = {Button(next(pos), 'edit skin', RED, '', settings.text_size, data): edit_skin}
    image_obj: List[ImageObject] = []
    conf_colors = [ColorSelector(next(pos), 'background color', settings.background_color, settings.text_size, data,
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
                            submit_settings(data, conf_bars, conf_colors, teleport_button, image_obj)
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
                        for button in buttons:
                            if button.is_touch_mouse():
                                try:
                                    image_obj = buttons[button](screen, data)
                                except EscPressed:
                                    pass
                elif event.button == MOUSE_RIGHT:
                    for color in conf_colors:
                        if color.is_touch_mouse():
                            color.change_color(False)
                            break
        for bar in conf_bars:
            bar.draw(screen)
        for button in buttons:
            button.draw(screen)
        for color in conf_colors:
            color.draw(screen)
        teleport_button.draw(screen)
        submit_button.draw(screen)
        reset_button.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)


def lobby(data: DataManager):
    screen = pygame.display.set_mode(get_resolution())
    pygame.display.set_caption(WINDOW_TITLE)
    data.reset(screen)

    start_button = Button((screen.get_rect().centerx, settings.text_size * 5), 'start game!', RED,
                          'click here to start game!', settings.text_size * 2, data, CENTER)
    settings_button = Button((screen.get_rect().centerx, settings.text_size * 12), 'settings', RED,
                             'click here to change settings!', settings.text_size * 2, data, CENTER)
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


def check_details(boxes, is_login):
    values = boxes.value
    if is_login:
        username, password = values
        index = db.user_id(username)
        if index == -1:
            raise LoginError('username not exist in the database!')
        if db.users_password[index] != password:
            raise LoginError("username and password don't match!")
        settings.set_username(username)
    else:
        username, password, confirm = values
        index = db.user_id(username)
        if index != -1:
            raise LoginError('username already exist in the database!')
        if password != confirm:
            raise LoginError("passwords don't match!")
        db.add_user(username, password)
        settings.set_username(username)


def log_in(data: DataManager):
    screen = pygame.display.set_mode(get_resolution())
    pygame.display.set_caption(WINDOW_TITLE)
    data.reset(screen)
    pos = (settings.text_size * 5, settings.text_size * 5)
    is_login = True
    login_boxes = Inputs(pos, [('username', False), ('password', True)])
    register_boxes = Inputs(pos, [('username', False), ('password', True), ('confirm password', True)])
    log_in_button = Button(screen.get_rect().center, 'already have an account? log in here!',
                           RED, '', settings.text_size, data, CENTER)
    register_button = Button(screen.get_rect().center, "don't have an account? register here!",
                             RED, '', settings.text_size, data, CENTER)
    while data.running:
        button = register_button if is_login else log_in_button
        boxes = login_boxes if is_login else register_boxes
        events = pygame.event.get()
        data.handle_events(events)
        boxes.active(events)
        for event in events:
            if event.type == pygame.QUIT:
                data.running = False
                raise QuitPressed
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if button.is_touch_mouse():
                        is_login = not is_login
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        check_details(boxes, is_login)
                        return
                    except LoginError as error:
                        data += str(error)
        boxes.draw(screen)
        button.draw(screen)
        data.draw(screen)
        pygame.display.flip()
        clock.tick(LOBBY_REFRESH_RATE)
        data.delete(screen)


def main():
    pygame.init()
    data = DataManager()
    try:
        log_in(data)
        while True:
            try:
                lobby(data)
            except SettingsChanged:
                pass
    except QuitPressed:
        settings.write_volume(data.volume.value)
    pygame.quit()
    db.close()


if __name__ == '__main__':
    main()
