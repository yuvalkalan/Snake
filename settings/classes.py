from .constants import *
from basicFont import *
import pygame
import math
import pickle
from .database import db


class VolumeBar(ImageObject):
    """
    המחלקה האחראית על הצגת פס קנה מידה
    """
    def __init__(self, screen: pygame.Surface, starter_value: int = 1):
        pos_x, pos_y = screen.get_rect().bottomright
        super(VolumeBar, self).__init__((pos_x - 5, pos_y - 5), VOLUME_IMAGES[0], settings.delta_size,
                                        position_at=BOTTOMRIGHT)
        self._title = [Clicker(self._pos, img, settings.delta_size) for img in VOLUME_IMAGES]
        x, y = self.rect.midtop
        dot_img_distance = 10 * settings.delta_size

        self._dot = (x, int(y - dot_img_distance))

        _, y = screen_grids(screen)
        y = int(y - y * DATA_ZONE_SIZE) * settings.snake_speed
        line_height = self.rect.top - y - dot_img_distance - settings.dot_radius
        self._line_rect = pygame.Rect(self._dot, (settings.scale_bar_width, line_height))
        self._line_rect.midbottom = self._line_rect.midtop

        self._mouse_down = False
        self._is_active = False
        self._is_mute = False
        self.value = starter_value

    @property
    def color(self):
        # הצבע בין אדום לירוק כאשר אדום מתקבל כאשר הערך 0 והירוק כאשר הערך 1
        return int((1 - self.value) * 255), int(self.value * 255), 0

    @property
    def colored_title(self):
        return self.this_title.copy_color(BLACK, self.color)

    def draw(self, screen):
        if self._is_active:
            color = self.color
            # מייצר את הפס
            pygame.draw.line(screen, color, self._line_rect.topleft, self._line_rect.bottomleft, self._line_rect.width)
            # מצייר את הנקודה
            pygame.draw.circle(screen, color, self._dot, settings.dot_radius)
        self.colored_title.draw(screen)

    @property
    def value(self):
        """
        ערך ה-value מוגדר להיות מספר בין 0 ל-1. 0 מתקבל כאשר הנקודה הכי קרוב לכותרת, ו1 מתקבל כאשר הנקודה בקצה השני
        :return: ערך הפס
        """
        if self._is_mute:
            return 0
        _, dot_y = self._dot
        top, bottom = self._line_rect.top, self._line_rect.bottom
        return (dot_y - bottom) / (top - bottom)

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
        dot_y = (top - bottom) * value + bottom
        self._dot = self._dot[0], dot_y
        self._is_mute = False

    def is_touch_mouse(self):
        mouse = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mouse, (1, 1))
        return mouse_rect.colliderect(self._line_rect) or distance(self._dot, mouse) <= settings.dot_radius

    def handle_events(self, events):
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
                    if self.is_touch_mouse() and self._is_active:
                        self._mouse_down = True
                        self._dot = (self._dot[0], pygame.mouse.get_pos()[1])
                    elif self.this_title.is_touch_mouse():
                        if self._is_active:
                            self._is_mute = not self._is_mute
                        else:
                            self._is_active = not self._is_active
                    else:
                        self._is_active = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_down = False
            elif event.type == pygame.MOUSEMOTION and self._mouse_down and self._is_active:
                self._dot = (self._dot[0], pygame.mouse.get_pos()[1])
                self._is_mute = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self._is_mute = not self._is_mute
                elif event.key == pygame.K_UP and self._is_active:
                    self.value += 0.1
                elif event.key == pygame.K_DOWN and self._is_active:
                    self.value -= 0.1
        if self.value < 0:
            self.value = 0
        elif self.value > 1:
            self.value = 1
        return started_value != self.value


class Settings:
    def __init__(self):
        self._resolution = None
        self._base_block_size = None
        self._refresh_rate = None
        self._base_text_size = None
        self._head1_image = self._head2_image = None
        self._body1_image = self._body2_image = None
        self._bg_color = None
        self._food_color = None
        self._teleport = None
        self._has_change = None
        self._last_volume = None
        self._username = None
        self.reset()
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

    @property
    def head1_image(self):
        return pygame.surfarray.make_surface(self._head1_image)

    @property
    def head2_image(self):
        return pygame.surfarray.make_surface(self._head2_image)

    @property
    def body1_image(self):
        return pygame.surfarray.make_surface(self._body1_image)

    @property
    def body2_image(self):
        return pygame.surfarray.make_surface(self._body2_image)

    @property
    def background_color(self):
        return self._bg_color

    @property
    def food_color(self):
        return self._food_color

    @property
    def teleport(self):
        return self._teleport

    @property
    def obstacle_speed(self):
        return BASE_OBSTACLE_SPEED * self.delta_size

    @property
    def pixel_ratio(self):
        return self.block_size/DEFAULT_BLOCK_SIZE

    @property
    def last_volume(self):
        return self._last_volume

    @property
    def snake_size(self):
        return settings.base_block_size / DEFAULT_BLOCK_SIZE * settings.delta_size

    def set_username(self, username):
        self._username = username
        self._head1_image, self._head2_image, self._body1_image, self._body2_image = db.get_skin(self._username)

    def set_params(self, lst):
        lst = iter(lst)
        self._resolution = next(lst)
        self._base_block_size = next(lst)
        self._refresh_rate = next(lst)
        self._base_text_size = next(lst)
        self._bg_color = next(lst)
        self._food_color = next(lst)
        self._teleport = next(lst)
        self._last_volume = next(lst)
        self._head1_image, self._head2_image, self._body1_image, self._body2_image = db.get_skin(self._username)
        self._has_change = True

    def rewrite_skin(self, *skin):
        db.set_skin(self._username, *skin)
        self.reset()

    def rewrite_skin_to_default(self):
        db.set_skin(self._username)
        self.reset()

    def set_default_skin(self):
        self._head1_image, self._head2_image, self._body1_image, self._body2_image = db.get_skin()

    def set_to_default(self):
        self._resolution: int = 710
        self._base_block_size: int = 29
        self._refresh_rate: int = 30
        self._base_text_size: int = 20
        self.set_default_skin()
        self._bg_color = BLACK
        self._food_color = YELLOW
        self._teleport = True
        self._last_volume = 0
        self._has_change = True

    def rewrite(self):
        try:
            with open(SETTING_FILE, 'wb+') as my_file:
                lst = [self._resolution,
                       self._base_block_size,
                       self._refresh_rate,
                       self._base_text_size,
                       self._bg_color,
                       self._food_color,
                       self._teleport,
                       self._last_volume]
                my_file.write(pickle.dumps(lst))
        except Exception as e:
            print(f'can not write settings! {type(e)} -> {e}')
        self.reset()

    def reset(self):
        try:
            with open(SETTING_FILE, 'rb') as my_file:
                content = pickle.loads(my_file.read())
            self.set_params(content)
        except Exception as e:
            print(f'can not read settings! {type(e)} -> {e}')
            self.set_to_default()

    def write_volume(self, volume: float):
        self.reset()
        self._last_volume = volume
        self.rewrite()

    @property
    def has_change(self):
        change = self._has_change
        self._has_change = False
        return change


class DataManager:
    def __init__(self):
        self._running = True
        self._volume = None
        self._temp_msgs = None
        self._background_img = None
        self._screen = None
        self._username = None
        self._password = None
        pygame.mixer.music.set_volume(settings.last_volume)
        pygame.mixer.music.load(BACKGROUND_SOUND)
        pygame.mixer.music.play(-1)

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, running):
        self._running = running
    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        self._username = value
        
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def volume(self):
        return self._volume

    def __iadd__(self, other: str):
        if self._running:
            self._temp_msgs += TempMsg(other, self._screen, volume=self._volume.value)
        return self

    def handle_events(self, events):
        if self._volume.handle_events(events):
            pygame.mixer.music.set_volume(self._volume.value)

    def draw(self, screen):
        self._volume.draw(screen)
        self._temp_msgs.draw(screen)

    def delete(self, screen):
        screen.blit(self._background_img, (0, 0))

    def empty(self):
        self._temp_msgs.empty()

    def reset(self, screen):
        self._running = True
        self._volume = VolumeBar(screen, 0)
        self._volume.value = settings.last_volume
        pygame.mixer.music.set_volume(self._volume.value)
        self._temp_msgs = TempMsgList(screen)
        self._background_img = pygame.transform.scale(pygame.image.load(BACKGROUND_IMG), screen.get_size())
        self._screen = screen
        self.delete(screen)


class TempMsg(Message):
    """
    המחלקה האחראית על הצגת הודעות זמניות
    """
    def __init__(self, text: str, screen, color: COLOR = WHITE, play_error_sound: bool = True, volume: float = 1):
        """
        הפעולה הבונה
        :param text: ראה במחלקת האב
        :param color: הצבע ההתחלתי של ההודעה
        :param play_error_sound: האם להפעיל סאונד של שגיאה או לא
        :param volume: עוצמת הווליום של סאונד השגיאה (מספר בין 0 ל-1)
        """
        super(TempMsg, self).__init__(screen.get_rect().center, text, settings.text_size, color, CENTER)
        if play_error_sound:
            play_sound(TEMP_MSG_CHANNEL, ERROR_SOUND, volume)
        self._speed = self.rect.centery / (LOBBY_REFRESH_RATE * TEMP_MSG_EXIST_TIMER)
        self._color_dec = [item / (LOBBY_REFRESH_RATE * TEMP_MSG_EXIST_TIMER) for item in self.color]

    def draw(self, screen: pygame.Surface) -> bool:
        """
        מצייר את ההודעה אל המסך
        :param screen: אובייקט המסך
        :return: True - אם זמן ההודעה פג וצריך להוריד אותה
                 False - אחרת
        """
        self.fade_out()
        super(TempMsg, self).draw(screen)
        if self.rect.top < 0:
            return True
        return False

    def fade_out(self) -> NoReturn:
        """
        משנה את הצבע של ההודעה לבהיר יותר
        :return: None
        """
        self.color = self._next_color
        self._pos = self._next_pos

    @property
    def _next_pos(self) -> POSITION:
        """
        מחזיר את המיקום החדש של ההודעה
        :return: מיקום חדש
        """
        x, y = self._pos
        return x, y - self._speed

    @property
    def _next_color(self):
        return [self._color[i] - self._color_dec[i] for i in range(len(self._color))]


class TempMsgList:
    def __init__(self, screen: pygame.Surface):
        self._lst: List[TempMsg] = []
        self._starter_pos = screen.get_rect().center

    def __iadd__(self, other: TempMsg):
        other.pos = self._starter_pos
        self._lst.append(other)
        return self

    def draw(self, screen):
        to_remove = [msg for msg in self._lst if msg.draw(screen)]
        for msg in to_remove:
            self._lst.remove(msg)

    def empty(self):
        self._lst = []


class GameBlock(BlockObject):
    def delete(self, screen):
        screen.fill(settings.background_color, self.rect)


def screen_grids(screen: pygame.Surface):
    width, height = screen.get_size()
    return width // settings.snake_speed, height // settings.snake_speed


settings = Settings()
