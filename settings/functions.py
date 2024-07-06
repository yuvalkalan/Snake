from .classes import *


def round_to_grid(pos):
    x, y = pos
    x = x - x % settings.snake_speed
    y = y - y % settings.snake_speed
    return x, y


def resolution() -> POSITION:
    width, height = (int(BASE_RESOLUTION / RESOLUTION_RATIO), BASE_RESOLUTION)
    width = width - width % settings.base_snake_speed
    height = height - height % settings.base_snake_speed
    grid_w, grid_h = int(width // settings.base_snake_speed), int(height // settings.base_snake_speed)
    return grid_w * settings.snake_speed, grid_h * settings.snake_speed


def submit_settings(data, conf_bars, conf_colors, teleport_button, image_obj: List[ImageObject]):
    lst = [bar.real_value for bar in conf_bars]
    if image_obj:
        lst += [img.to_bytes() for img in image_obj]
    else:
        lst += [pygame.surfarray.array3d(settings.head1_image),
                pygame.surfarray.array3d(settings.head2_image),
                pygame.surfarray.array3d(settings.body1_image),
                pygame.surfarray.array3d(settings.body2_image)]
    lst += [color.real_value for color in conf_colors]
    lst += [teleport_button.real_value]
    lst += [data.volume.value]
    settings.set_params(lst)
    settings.rewrite()
    raise SettingsChanged


def check_settings(conf_bars, conf_colors, teleport_button, data):
    colors = [color.real_value for color in conf_colors]
    if len(colors) != len(set(colors)):
        data += 'colors must be unique!'
        return False
    return True
