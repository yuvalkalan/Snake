from typing import *

import pygame

COLOR = Tuple[int, int, int]
POSITION = Tuple[int, int]

# colors: --------------------------------------------------------------------------------------------------------------
BLACK: COLOR = (0, 0, 0)             # black
RED: COLOR = (255, 0, 0)             # red
GREEN: COLOR = (0, 255, 0)           # green
WHITE: COLOR = (255, 255, 255)       # white
YELLOW: COLOR = (255, 255, 0)        # yellow
BLUE: COLOR = (0, 0, 255)            # blue
PURPLE: COLOR = (102, 51, 153)       # purple
PINK: COLOR = (255, 183, 197)        # pink
ORANGE: COLOR = (255, 125, 0)        # orange
GRAY: COLOR = (169, 169, 169)        # gray

COLORS_NAME = {'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'WHITE': WHITE, 'YELLOW': YELLOW, 'BLUE': BLUE,
               'PURPLE': PURPLE, 'PINK': PINK, 'ORANGE': ORANGE, 'GRAY': GRAY}
COLORS: List[COLOR] = list(COLORS_NAME.values())

SHIFTED_NUMBERS: Dict[str, str] = {'1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*',
                                   '9': '(', '0': ')'}
SPECIAL_CHARS: Dict[int, str] = {39: "'", 44: ',', 45: '-', 46: '.', 47: r'/', 59: ';', 61: '=', 91: '[', 92: '\\',
                                 93: ']', 96: '`'}
SHIFTED_SPECIAL_CHARS: Dict[int, str] = {39: '"', 44: '<', 45: '_', 46: '>', 47: '?', 59: ':', 61: '+', 91: '{',
                                         92: '|', 93: '}', 96: '~'}

TITLE_FONT: str = r'files\fonts\title_font.ttf'
TEXT_FONT: str = r'files\fonts\text_font.ttf'
SETTING_FILE = r'settings.txt'
BACKGROUND_IMG = r'files\lobby.png'

TOPLEFT: str = 'topleft'
CENTER: str = 'center'
TOPRIGHT: str = 'topright'
BOTTOMLEFT: str = 'bottomleft'
BOTTOMRIGHT: str = 'bottomright'

MOUSE_LEFT: int = 1
MOUSE_SCROLL: int = 2
MOUSE_RIGHT: int = 3
MOUSE_SCROLL_UP: int = 4
MOUSE_SCROLL_DOWN: int = 5

#VOLUME_POS: POSITION = (955, 370)
VOLUME_IMAGES: List[str] = [r'files\buttons\volume0.png', r'files\buttons\volume1.png', r'files\buttons\volume2.png',
                            r'files\buttons\volume3.png']

WINDOW_TITLE: str = 'Snake'

DIR_UP: int = 0
DIR_DOWN: int = 1
DIR_LEFT: int = 2
DIR_RIGHT: int = 3

RESOLUTION_RATIO: float = 9/16
BASE_RESOLUTION = 720

STARTER_SIZE: int = 4

DATA_ZONE_SIZE: float = 0.2

ERROR_SOUND = r'files\error.ogg'
TEMP_MSG_CHANNEL = 0

LOBBY_REFRESH_RATE = 30

P2_CVT_KEYS = {pygame.K_w: pygame.K_UP,
               pygame.K_s: pygame.K_DOWN,
               pygame.K_d: pygame.K_RIGHT,
               pygame.K_a: pygame.K_LEFT}

BATTLE_TIMER = 60
SURVIVAL_TIMER = 20

BASE_OBSTACLE_SPEED = 20