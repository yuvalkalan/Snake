from .constants import *
from settings import *


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
        self.text = self.base_and_value

    def draw(self, screen: pygame.Surface):
        self.update_text()
        super(DataMessage, self).draw(screen)


class Button(Message):
    def __init__(self, pos: POSITION, text: str, color: COLOR, description: str, size: int, data: DataManager,
                 position_at: str = TOPLEFT):
        super(Button, self).__init__(pos, text, size, color, position_at)
        self._description = Message((0, 0), description, size, RED, TOPLEFT)
        self._played_sound = False
        self._base_color = color
        self._volume = data.volume

    def _play_sound(self):
        super(Button, self)._play_sound()
        play_sound(BUTTON_CHANNEL, BUTTON_SOUND, self._volume.value)

    def draw(self, screen: pygame.Surface):
        if self.is_touch_mouse():
            self.colored()
            self.draw_description(screen, pygame.mouse.get_pos())
            if not self._played_sound:
                self._play_sound()
        else:
            self._played_sound = False
            self.normal()
        super(Button, self).draw(screen)

    def draw_description(self, screen: pygame.Surface, pos: POSITION):
        x, y = pos
        x += 40
        y += 40
        self._description.pos = pos
        self._description.draw(screen)

    def colored(self):
        if self.color != GREEN:
            self.color = GREEN

    def normal(self):
        if self.color != self._base_color:
            self.color = self._base_color

    @property
    def description(self):
        return self._description.text

    @description.setter
    def description(self, description: str):
        self._description.text = description


class Switcher(Button):
    """
    המחלקה האחראית על כפתור סוגר ופותח
    """
    def __init__(self, pos: POSITION, data: DataManager):
        """
        הפעולה הבונה
        :param pos: מיקום הכפתור
        """
        super(Switcher, self).__init__(pos, '[-]', RED, '', settings.text_size, data, TOPLEFT)
        self._is_plus = False

    def change_mode(self):
        self._is_plus = not self._is_plus
        self.text = f"[{'+' if self._is_plus else '-'}]"

    def __bool__(self):
        return not self._is_plus


class ScaleBar:
    def __init__(self, pos: POSITION, title: str, length: int, data: DataManager, starter_value: int = 1,
                 min_value: int = 0, max_value: int = 1):
        self._title = Button(pos, title, RED, '', settings.text_size, data)
        x, y = self._title.rect.midright
        self._dot = (x + 10, y)
        self._max_value = max_value
        self._min_value = min_value
        self._line_rect = pygame.Rect(self._dot, (length, settings.scale_bar_width))
        x, y = self._dot
        self._value_des = DataMessage((int(x), int(y)), '{}', settings.text_size, RED, TOPLEFT, self,
                                      lambda s: s.real_value)
        self._mouse_down = False
        self._is_active = False
        self.real_value = starter_value

    @property
    def real_value(self):
        return round(self._min_value + self.value * (self._max_value - self._min_value))

    @real_value.setter
    def real_value(self, value):
        self.value = (value-self._min_value) / (self._max_value - self._min_value)

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
        mouse_rect = pygame.Rect(mouse, (1, 1))
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
                    self.real_value += 1
                elif event.key == pygame.K_LEFT:
                    self.real_value -= 1
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        return started_value != self.value

    def title_is_touch_mouse(self):
        return self.is_touch_mouse() or self._title.is_touch_mouse()


class SelectionButton(Message):
    def __init__(self, pos: POSITION, text: str, mode: bool, size: int, data: DataManager, position_at: str = TOPLEFT):
        self._mode = mode
        self._volume = data.volume
        super(SelectionButton, self).__init__(pos, text, size, GREEN if self._mode else RED, position_at)

    def _play_sound(self):
        super(SelectionButton, self)._play_sound()
        play_sound(BUTTON_CHANNEL, BUTTON_SOUND, self._volume.value)

    def change_mode(self):
        self._mode = not self._mode
        self.color = GREEN if self._mode else RED

    @property
    def real_value(self):
        return self._mode


class ColorSelector(Message):
    def __init__(self, pos: POSITION, text: str, color: COLOR, size: int, data: DataManager, position_at: str = TOPLEFT,
                 allow_black=False):
        self._color_index = COLORS.index(color)
        self._allow_black = allow_black
        self._volume = data.volume
        super(ColorSelector, self).__init__(pos, text, size, color, position_at)

    def _play_sound(self):
        super(ColorSelector, self)._play_sound()
        play_sound(BUTTON_CHANNEL, BUTTON_SOUND, self._volume.value)

    def change_color(self, forward=True):
        delta = 1 if forward else -1
        self._color_index = (self._color_index + delta) % len(COLORS)
        if not self._allow_black and COLORS[self._color_index] == BLACK:
            self._color_index = (self._color_index + delta) % len(COLORS)
        self.color = COLORS[self._color_index]

    @property
    def real_value(self):
        return self.color


clock = pygame.time.Clock()
