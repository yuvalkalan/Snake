import math
import pygame
import os  # שימוש: עבודה עם קבצים
from constants import *

pygame.font.init()


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class Settings:
    def __init__(self):
        try:
            my_file = open(SETTING_FILE, 'r')
            content = my_file.read().split('\n')
            res, block_size, speed, text_size = int(content[0]), int(content[1]), int(content[2]), int(content[3])
            my_file.close()
        except (FileNotFoundError, ValueError):
            res, block_size, speed, text_size = 480, 19, 15, 20
        self._resolution: int = res
        self._base_block_size: int = block_size
        self._refresh_rate: int = speed
        self._base_text_size: int = text_size
        self._has_change = False

    @property
    def resolution(self):
        return self._resolution

    @property
    def base_block_size(self):
        return self._base_block_size

    @property
    def refresh_rate(self):
        return self._refresh_rate

    @property
    def base_text_size(self):
        return self._base_text_size

    @property
    def delta_size(self):
        return self._resolution / BASE_RESOLUTION

    @property
    def dot_radius(self):
        return int(8 * self.text_size / 20)

    @property
    def scale_bar_width(self):
        return int(3 * self.text_size / 20)

    @property
    def block_size(self):
        return int(self.delta_size * self._base_block_size)

    @property
    def base_snake_speed(self):
        return self._base_block_size + 1

    @property
    def snake_speed(self):
        return self.block_size + 1

    @property
    def text_size(self):
        return int(self.delta_size * self._base_text_size)

    def reset(self):
        try:
            my_file = open(SETTING_FILE, 'r')
            content = my_file.read().split('\n')
            res, block_size, speed, text_size = int(content[0]), int(content[1]), int(content[2]), int(content[3])
            my_file.close()
        except (FileNotFoundError, ValueError):
            res, block_size, speed, text_size = 480, 19, 15, 20
        self._resolution: int = res
        self._base_block_size: int = block_size
        self._refresh_rate: int = speed
        self._base_text_size: int = text_size
        self._has_change = True

    @property
    def has_change(self):
        change = self._has_change
        self._has_change = False
        return change


settings = Settings()


class Message:
    """
    מחלקה האחראית על יצירת אובייקטים של טקסט הניתן להציגם למסך
    """

    def __init__(self, pos: POSITION, text: str, size: int, color: COLOR, position_at: str = TOPLEFT, title=False):

        self._text = text
        self._color = color
        # יוצר אובייקט פונט
        self._text_font = pygame.font.Font(TITLE_FONT if title else TEXT_FONT, size)
        # יוצר אובייקט טקסט מאובייקט הפונט
        self._text_surf = self._text_font.render(text, True, color)
        self._rect = self._text_surf.get_rect()
        self._position_at = position_at
        self.pos = pos

    def __str__(self):
        return self._text

    def draw(self, screen: pygame.Surface, pos=None):
        if pos:
            screen.blit(self._text_surf, pos)
        else:
            screen.blit(self._text_surf, self._rect.topleft)

    @property
    def size(self):
        return self._rect.size

    @property
    def rect(self):
        return pygame.Rect.copy(self._rect)

    @property
    def text(self):
        return self._text

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self._text_surf = self._text_font.render(self._text, True, self._color)

    @property
    def text_surf(self):
        return self._text_surf

    @text.setter
    def text(self, text: str):
        if not self._text == text:
            self._text = text
            self._text_surf = self._text_font.render(text, True, self._color)
            top_left = self._rect.topleft
            self._rect = self._text_surf.get_rect()
            self._rect.topleft = top_left

    @property
    def pos(self):
        return self.rect.topleft

    @pos.setter
    def pos(self, pos):
        if self._position_at == TOPLEFT:
            self._rect.topleft = pos
        elif self._position_at == CENTER:
            self._rect.center = pos
        elif self._position_at == TOPRIGHT:
            self._rect.topright = pos
        elif self._position_at == BOTTOMLEFT:
            self._rect.bottomleft = pos
        elif self._position_at == BOTTOMRIGHT:
            self._rect.bottomright = pos
        else:
            raise ValueError


class DataMessage(Message):
    """
    מחלקה האחראית על יצירת הודעות עם תוכן משתנה
    """

    def __init__(self, pos: POSITION, text: str, size: int, color: COLOR, position_at=TOPLEFT,
                 value=None, func: Callable = lambda v: v, title=False):
        """
        הפעולה הבונה
        :param pos: ראה במחלקת האב
        :param text: הטקסט להציג למסך, מיקום הפרמטרים אותם רוצים להציג למסך יהיה בסוגריים מסולסלים
        :param size: ראה במחלקת האב
        :param color: ראה במחלקת האב
        :param position_at: ראה במחלקת האב
        :param value: הערך שאותו רוצים להציג
        :param func: הפונקציה שרוצים להפעיל על הערך (ערך התחלתי-ללא)
        :param title: ראה במחלקת האב
        """
        super(DataMessage, self).__init__(pos, text, size, color, position_at, title)
        self._value = value
        self._func = func
        self._base_text = text

    def __add__(self, other):
        return self._value + other

    def __sub__(self, other):
        return self._value - other

    def __iadd__(self, other):
        self._value += other
        return self

    def __isub__(self, other):
        self._value -= other
        return self

    def __str__(self):
        return f"text:'{self._text}' value:{self._value}"

    def __mod__(self, other):
        return self._value % other

    def __imod__(self, other):
        self._value %= other
        return self

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def base_and_value(self) -> str:
        """
        הפעולה לוקחת את טקסט הבסיס, הערך והפונקציה שהוכנסו ומחזירה את ההטקסט שצריך להיות מוצג למסך
        :return: המחרוזת שצריכה להיות מוצגת למסך
        """
        if isinstance(self._func(self._value), tuple):
            return self._base_text.format(*self._func(self._value))
        return self._base_text.format(self._func(self._value))

    def update_text(self):
        """
        הפעולה מעדכנת את ההודעה לטקסט החדש שלה אם יש צורך בכך
        :return: None
        """
        if self.base_and_value != self._text:
            self._text = self.base_and_value
            self._text_surf = self._text_font.render(self._text, True, self._color)
            top_left = self._rect.topleft
            self._rect = self._text_surf.get_rect()
            self._rect.topleft = top_left

    def draw(self, screen: pygame.Surface, pos=None):
        self.update_text()
        if pos:
            screen.blit(self._text_surf, pos)
        else:
            screen.blit(self._text_surf, self._rect.topleft)


class LoadingMessage(DataMessage):
    """
    המחלקה האחראית על יצירת הודעות המראות על טעינה
    """

    def __init__(self, pos: POSITION, text: str, size: int, color: COLOR, position_at=TOPLEFT):
        """
        הפעולה הבונה
        :param pos: ראה במחלקת האב
        :param text: הטקסט שרוצים לראות טוען על המסך
        :param size: ראה במחלקת האב
        :param color: ראה במחלקת האב
        :param position_at: ראה במחלקת האב
        """
        super(LoadingMessage, self).__init__(pos, text + '{}', size, color, position_at, 0,
                                             lambda v: 2 * v // settings.refresh_rate % 4 * '.')

    def draw(self, screen: pygame.Surface, pos=None):
        self._value += 1
        self.update_text()
        if pos:
            screen.blit(self._text_surf, pos)
        else:
            screen.blit(self._text_surf, self._rect.topleft)


# class TempMsg(Message):
#     """
#     המחלקה האחראית על הצגת הודעות זמניות
#     """
#
#     def __init__(self, text: str, color: COLOR = WHITE, play_error_sound: bool = True, volume: int = 1):
#         """
#         הפעולה הבונה
#         :param text: ראה במחלקת האב
#         :param color: הצבע ההתחלתי של ההודעה
#         :param play_error_sound: האם להפעיל סאונד של שגיאה או לא
#         :param volume: עוצמת הווליום של סאונד השגיאה (מספר בין 0 ל-1)
#         """
#         super(TempMsg, self).__init__(SCREEN_CENTER, text, 20, color, CENTER)
#         # if play_error_sound:
#         #     channel = pygame.mixer.Channel(TEMP_MSG_CHANNEL)
#         #     channel.set_volume(volume)
#         #     channel.play(pygame.mixer.Sound(ERROR_SOUND))
#         self._existence_time = 4
#         self._time_counter = self._existence_time * settings.refresh_rate
#
#     def draw(self, screen: pygame.Surface, pos=None, reverse=False) -> bool:
#         """
#         מצייר את ההודעה אל המסך
#         :param screen: אובייקט המסך
#         :param pos: מיקום לצייר בו את ההודעה
#         :param reverse: האם לצייר את ההודעה עם דהייה לבהיר או לכהה
#         :return: True - אם זמן ההודעה פג וצריך להוריד אותה
#                  False - אחרת
#         """
#         self._time_counter -= 1
#         self.fade_in() if reverse else self.fade_out()
#         screen.blit(self._text_surf, pos) if pos else screen.blit(self._text_surf, self.current_pos)
#         if self._time_counter == 0:
#             return True
#         return False
#
#     def fade_out(self) -> NoReturn:
#         """
#         משנה את הצבע של ההודעה לבהיר יותר
#         :return: None
#         """
#         color = [int(self._time_counter / settings.refresh_rate / self._existence_time * item) for item in self._color]
#         self._text_surf = self._text_font.render(self._text, True, color)
#
#     def fade_in(self) -> NoReturn:
#         """
#         משנה את הצבע של ההודעה לכהה יותר
#         :return: None
#         """
#         color = [255 - int(self._time_counter / settings.refresh_rate / self._existence_time * item) for item in self._color]
#         self._text_surf = self._text_font.render(self._text, True, color)
#
#     @property
#     def current_pos(self) -> POSITION:
#         """
#         מחזיר את המיקום החדש של ההודעה
#         :return: מיקום חדש
#         """
#         x, y = self._rect.topleft
#         y = int(self._rect.centery * self._time_counter / settings.refresh_rate / self._existence_time)
#         return x, y


class Button:
    """
    המחלקה האחראית על הודעות הניתן ללחוץ עליהן
    """

    def __init__(self, pos: POSITION, text: str, color: COLOR, description: str, size: int, position_at: str = TOPLEFT):
        """
        הפעולה הבונה
        :param pos: מיקום
        :param text: טקסט להציג
        :param color: צבע
        :param description: טקסט תיאור
        :param size: גודל
        :param position_at: איפה המיקום שהוכנס ביחס להודעה
        """
        self._text = Message(pos, text, size, color, position_at)
        self._description = Message((0, 0), description, size, RED, position_at)
        self._color = color

    def __str__(self):
        return self._text.text

    @property
    def pos(self):
        return self._text.pos

    @pos.setter
    def pos(self, pos: POSITION):
        self._text.pos = pos

    def draw(self, screen: pygame.Surface, draw_description: bool = True):
        if self.is_touch_mouse():
            self.colored()
        else:
            self.normal()
        self._text.draw(screen)
        if draw_description and self.is_touch_mouse():
            self.draw_description(screen, pygame.mouse.get_pos())

    def draw_description(self, screen: pygame.Surface, pos: POSITION):
        x, y = pos
        x += 15
        y += 15
        self._description.pos = pos
        self._description.draw(screen)

    @property
    def rect(self):
        return self._text.rect

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect)

    def colored(self):
        if self._text.color != GREEN:
            self._text.color = GREEN

    def normal(self):
        if self._text.color != self._color:
            self._text.color = self._color

    @property
    def description(self):
        return self._description.text

    @description.setter
    def description(self, description: str):
        self._description.text = description

    @property
    def text(self):
        return self._text.text

    def is_touch(self, obj):
        return self.rect.colliderect(obj.rect)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color: COLOR):
        self._color = color
        self._text.color = color


class Switcher:
    """
    המחלקה האחראית על כפתור סוגר ופותח
    """

    def __init__(self, pos: POSITION):
        """
        הפעולה הבונה
        :param pos: מיקום הכפתור
        """
        self._plus_button = Button(pos, '[+]', RED, '', settings.text_size, TOPLEFT)
        self._minus_button = Button(pos, '[-]', RED, '', settings.text_size, TOPLEFT)
        self._is_plus = False

    def draw(self, screen: pygame.Surface):
        if self._is_plus:
            self._plus_button.draw(screen)
        else:
            self._minus_button.draw(screen)

    def is_touch_mouse(self):
        if self._is_plus:
            return self._plus_button.is_touch_mouse()
        return self._minus_button.is_touch_mouse()

    def change_mode(self):
        self._is_plus = not self._is_plus

    def __bool__(self):
        return not self._is_plus


class Clicker:
    """
    המחלקה האחראית על הצגת כפתוריי תמונה
    """

    def __init__(self, image: str, pos: POSITION = (0, 0), center: bool = True, size=-1):
        """
        הפעולה הבונה
        :param image: מיקום ההודעה במחשב
        :param pos: מיקום הכפתור על המסך
        :param center: האם המיקום הוא עבור מרכז ההודעה או עבור הפינה השמאלית עליונה
        """
        if size == -1:
            size = settings.delta_size
        self._image = pygame.image.load(image)
        self._image.set_colorkey(WHITE)
        new_size = int(self._image.get_rect().width * size), int(self._image.get_rect().height * size)
        self._image = pygame.transform.scale(self._image, new_size)
        self._rect = pygame.Rect(pos, self._image.get_rect().size)
        if center:
            self._rect.center = pos

    def draw(self, screen: pygame.Surface):
        screen.blit(self._image, self._rect.topleft)

    def is_touch_mouse(self):
        mouse = pygame.mouse.get_pos()
        x1, y1 = mouse
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self._rect)

    @property
    def rect(self):
        return self._rect

    @property
    def pos(self):
        return self._rect.topleft

    @pos.setter
    def pos(self, pos: POSITION):
        self._rect.topleft = pos


class GIF:
    """
    המחלקה האחראית על הצגת סרטוני גיף למסך
    """

    def __init__(self, src: str, speed: float, pos: POSITION, center: bool = True, max_time: int = -1, size: float = 1):
        """
        הפעולה הבונה
        :param src: התיקייה שמכילה את התמונות של הגיף
        :param speed: מהירות ההפעלה (כמות חזרות של הגיף בשנייה)
        :param pos: מיקום על המסך
        :param center: האם המיקום הוא ביחס למרכז הצורה או הפינה השמאלית עליונה
        :param max_time: מספר החזרות המקסימלי של הגיף. מינוס 1 לחזרה אינסופית
        :param size: גודל התמונות ביחס לגודל האמיתי
        """
        # טוען את כל התמונות של הגיף
        self._images = []
        images = sorted([img for img in os.listdir(src)], key=lambda f: int(f[:f.index('.')]))
        for image in images:
            image = pygame.image.load(fr'{src}\{image}')
            width, height = image.get_size()
            self._images.append(pygame.transform.scale(image, (int(width * size), int(height * size))))
        self._counter = 0
        self._image_index = 0
        self._speed = speed
        self._rect = self._images[self._image_index].get_rect()
        self._center = center
        self.pos = pos
        self._max_time = int(settings.refresh_rate / self._speed * max_time)

    def draw(self, screen):
        """
        מדפיס את האובייקט למסך
        :param screen: אובייקט המסך
        :return: האם צריך להרוג את הגיף או לא
        """
        self._counter += 1
        if self._speed * self._counter / settings.refresh_rate >= 1 / len(self._images):
            self._counter = 0
            self._image_index = (self._image_index + 1) % len(self._images)
        screen.blit(self._images[self._image_index], self._rect.topleft)
        self._max_time -= 1 if self._max_time > 0 else 0
        return self._max_time == 0

    @property
    def pos(self):
        return self._rect.topleft

    @pos.setter
    def pos(self, pos):
        if self._center:
            self._rect.center = pos
        else:
            self._rect.topleft = pos


class ScaleBar:
    """
    המחלקה האחראית על הצגת פס קנה מידה
    """

    def __init__(self, pos: POSITION, title: str, length: int, starter_value: int = 1, min_value: int = 0,
                 max_value: int = 1):
        """
        הפעולה הבונה
        :param pos: מיקום על המסך
        :param title: כותרת הפס. הכותרת יכולה להיות מחרוזת (ולהפוך לכפתור) או להיות רשימת כפתורים או קליקרים
        :param length: אורך הפס
        :param starter_value: הערך ההתחלתי של הפס
        """
        self._title = Button(pos, title, RED, '', settings.text_size)
        x, y = self._rect.midright
        self._dot: Tuple[float, float] = (x + 10, y)
        self._max_value = max_value
        self._min_value = min_value
        self._line_rect = pygame.Rect(self._dot, (length, settings.scale_bar_width))
        x, y = self._dot
        self._value_des = DataMessage((int(x), int(y)), '{}', settings.text_size, RED, TOPLEFT, self,
                                      lambda s: min_value + int(s.value * (max_value - min_value)))
        self._mouse_down = False
        self._is_active = False
        self.value = (starter_value-self._min_value)/(self._max_value-self._min_value)

    @property
    def real_value(self):
        return self._min_value + int(self.value * (self._max_value - self._min_value))

    @property
    def _rect(self):
        return self._title.rect

    def draw(self, screen):
        if self._is_active:
            # הצבע בין אדום לירוק כאשר אדום מתקבל כאשר הערך 0 והירוק כאשר הערך 1
            color = (int((1 - self.value) * 255), int(self.value * 255), 0)
            # מייצר את הפס
            pygame.draw.rect(screen, color, self._line_rect)
            # מצייר את הנקודה
            pygame.draw.circle(screen, color, self._dot, settings.dot_radius)
            x, y = self._dot
            self._value_des.pos = (x, y + settings.dot_radius)
            self._value_des.draw(screen)
        self._title.draw(screen)

    @property
    def value(self):
        """
        ערך ה-value מוגדר להיות מספר בין 0 ל-1. 0 מתקבל כאשר הנקודה הכי קרוב לכותרת, ו1 מתקבל כאשר הנקודה בקצה השני
        :return: ערך הפס
        """
        dot_x, _ = self._dot
        right, left = self._line_rect.right, self._line_rect.left
        return (dot_x - left) / (right - left)

    @value.setter
    def value(self, value):
        right, left = self._line_rect.right, self._line_rect.left
        dot_x = (right - left) * value + left
        self._dot = dot_x, self._dot[1]

    def is_touch_mouse(self):
        mouse = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mouse, (5, 5))
        return mouse_rect.colliderect(self._line_rect) or distance(self._dot, mouse) <= settings.dot_radius

    def active(self, events):
        """
        מפעיל את המד
        :param events: רשימת אירועים שביצע המשתמש
        :return: True - אם ערך המד שונה
                 False - אחרת
        """
        started_value = self.value
        for event in events:
            x, y = self._dot
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if self._is_active and self.is_touch_mouse():
                        self._mouse_down = True
                        self._dot = (pygame.mouse.get_pos()[0], y)
                    elif self._title.is_touch_mouse():
                        self._is_active = not self._is_active
                    else:
                        self._is_active = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_down = False
            elif event.type == pygame.MOUSEMOTION and self._mouse_down and self._is_active:
                self._dot = (pygame.mouse.get_pos()[0], y)
            elif event.type == pygame.KEYDOWN and self._is_active:
                if event.key == pygame.K_RIGHT:
                    self._dot = (x+1, y)
                elif event.key == pygame.K_LEFT:
                    self._dot = (x-1, y)
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        return started_value != self.value


class VolumeBar:
    """
    המחלקה האחראית על הצגת פס קנה מידה
    """

    def __init__(self, pos: POSITION, length: int, starter_value: int = 1):
        """
        הפעולה הבונה
        :param pos: מיקום על המסך
        :param length: אורך הפס
        :param starter_value: הערך ההתחלתי של הפס
        """
        self._title = [Clicker(img) for img in VOLUME_IMAGES]
        for item in self._title:
            item.pos = pos
        x, y = self._rect.midbottom
        self._dot = (x, int(y + 5 * settings.delta_size))
        self._line_rect = pygame.Rect(self._dot, (settings.scale_bar_width, length - self._rect.height - 15))
        self._mouse_down = False
        self._is_active = False
        self.value = starter_value

    @property
    def _rect(self):
        return self._title[0].rect

    def draw(self, screen):
        if self._is_active:
            # הצבע בין אדום לירוק כאשר אדום מתקבל כאשר הערך 0 והירוק כאשר הערך 1
            color = (int((1 - self.value) * 255), int(self.value * 255), 0)
            # מייצר את הפס
            pygame.draw.line(screen, color, self._line_rect.topleft, self._line_rect.bottomleft, self._line_rect.width)
            # מצייר את הנקודה
            pygame.draw.circle(screen, color, self._dot, settings.dot_radius)
        self.this_title.draw(screen)

    @property
    def value(self):
        """
        ערך ה-value מוגדר להיות מספר בין 0 ל-1. 0 מתקבל כאשר הנקודה הכי קרוב לכותרת, ו1 מתקבל כאשר הנקודה בקצה השני
        :return: ערך הפס
        """
        _, dot_y = self._dot
        top, bottom = self._line_rect.top, self._line_rect.bottom
        return (dot_y - top) / (bottom - top)

    @property
    def this_title(self):
        """
        הכותרת הנוכחית מוגדרת להיות כך שאם value=0 אז יוחזר הכותרת הראשונה ברשימה
        כל שאר הכותרות יתחלקו באופן שווה באחוזים
        לדוגמה: עבור 4 כותרות, כותרת 1 תוחזר כאשר value=0
        כותרת 2 תוחזר כאשר value מעל 0 ומתחת או שווה לשליש
        כותרת 3 תוחזר כאשר value מעל שליש ומתחת או שווה לשני שליש
        כותרת 4 תוחזר כאשר value מעל שני שליש ומתחת או שווה ל1
        """
        return self._title[math.ceil(self.value * (len(self._title) - 1))]

    @value.setter
    def value(self, value):
        top, bottom = self._line_rect.top, self._line_rect.bottom
        dot_y = (bottom - top) * value + top
        self._dot = self._dot[0], dot_y

    def is_touch_mouse(self):
        mouse = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mouse, (5, 5))
        return mouse_rect.colliderect(self._line_rect) or distance(self._dot, mouse) <= settings.dot_radius

    def active(self, events):
        """
        מפעיל את המד
        :param events: רשימת אירועים שביצע המשתמש
        :return: True - אם ערך המד שונה
                 False - אחרת
        """
        started_value = self.value
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if self._is_active and self.is_touch_mouse():
                        self._mouse_down = True
                        self._dot = (self._dot[0], pygame.mouse.get_pos()[1])
                    elif self.this_title.is_touch_mouse():
                        self._is_active = not self._is_active
                    else:
                        self._is_active = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_down = False
            elif event.type == pygame.MOUSEMOTION and self._mouse_down and self._is_active:
                self._dot = (self._dot[0], pygame.mouse.get_pos()[1])
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        return started_value != self.value


class SelectionButton(Message):
    def __init__(self, pos: POSITION, text: str, mode: bool, size: int, position_at: str = TOPLEFT):
        self._mode = mode
        super(SelectionButton, self).__init__(pos, text, size, GREEN if self._mode else RED, position_at)

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect)

    def change_mode(self):
        self._mode = not self._mode
        self.color = GREEN if self._mode else RED


class ColorSelector(Message):
    def __init__(self, pos: POSITION, text: str, color: COLOR, size: int, position_at: str = TOPLEFT,
                 allow_black=False):
        self._color_index = COLORS.index(color)
        self._allow_black = allow_black
        super(ColorSelector, self).__init__(pos, text, size, color, position_at)

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect)

    def change_color(self, forward=True):
        delta = 1 if forward else -1
        self._color_index = (self._color_index + delta) % len(COLORS)
        if not self._allow_black and COLORS[self._color_index] == BLACK:
            self._color_index = (self._color_index + delta) % len(COLORS)
        self.color = COLORS[self._color_index]


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


# def update_temp_msgs(temp_msgs: List[TempMsg], screen: pygame.Surface, reverse: bool = False) -> NoReturn:
#     """
#     מעדכן את ההודעות הזמניות
#     :param temp_msgs: רשימת הודעות זמניות
#     :param screen: אובייקט המסך
#     :param reverse: האם לצייר על צבע שחור או לבן
#     :return: None
#     """
#     to_remove = [msg for msg in temp_msgs if msg.draw(screen, reverse=reverse)]
#     for msg in to_remove:
#         temp_msgs.remove(msg)


def next_pos(start_pos: POSITION, change: POSITION):
    x, y = start_pos
    c_x, c_y = change
    while True:
        yield int(x), int(y)
        x += c_x
        y += c_y