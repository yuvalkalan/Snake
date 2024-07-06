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

P2_CVT_KEYS = {pygame.K_w: pygame.K_UP,
               pygame.K_s: pygame.K_DOWN,
               pygame.K_d: pygame.K_RIGHT,
               pygame.K_a: pygame.K_LEFT}

TEMP_MSG_CHANNEL = 0
BUTTON_CHANNEL = 1
SNAKE_CHANNEL = 2
FOOD_CHANNEL = 3

DEFAULT_BLOCK_SIZE = 19
