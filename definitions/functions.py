from .constants import *
import keyboard
import win32api
import win32con


def distance(obj1, obj2) -> float:
    """
     בודק מרחק בין 2 אובייקטים או נקודות
    :param obj1: אובייקט 1
    :param obj2: אובייקט 2
    :return: המרחק בין 2 האובייקטים
    """
    if isinstance(obj1, pygame.Rect) and isinstance(obj2, pygame.Rect):
        x1, y1 = obj1.center
        x2, y2 = obj2.center
    elif isinstance(obj1, tuple) and isinstance(obj2, tuple):
        x1, y1 = obj1
        x2, y2 = obj2
    else:
        raise ValueError
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def next_pos(start_pos: POSITION, change: POSITION):
    x, y = start_pos
    c_x, c_y = change
    while True:
        yield int(x), int(y)
        x += c_x
        y += c_y


def play_sound(channel_number: int, sound_file: str, volume: float):
    channel = pygame.mixer.Channel(channel_number)
    channel.set_volume(volume)
    channel.play(pygame.mixer.Sound(sound_file))


def get_caps_lock_status():
    status = win32api.GetKeyState(win32con.VK_CAPITAL)
    if status == -127 or status == 1:
        return True
    return False


def get_shift_status():
    return keyboard.is_pressed('shift')


def big_letter():
    return get_shift_status() ^ get_caps_lock_status()
