from basicObject import *
from .constants import *


class Message(ScreenObject):
    def __init__(self, pos: POSITION, text: str, size: int, color: COLOR, position_at: str = TOPLEFT, title=False):
        self._text = text
        self._color = color
        self._text_font = pygame.font.Font(TITLE_FONT if title else TEXT_FONT, size)
        self._text_surf = self._text_font.render(text, True, color)
        super(Message, self).__init__(pos, self.text_surf.get_size(), position_at)
        self._played_sound = False

    def __str__(self):
        return self._text

    def draw(self, screen: pygame.Surface):
        screen.blit(self._text_surf, self._pos)
        if self.is_touch_mouse():
            if not self._played_sound:
                self._play_sound()
        else:
            self._played_sound = False

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect)

    def _play_sound(self):
        self._played_sound = True

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
            self._size = self.text_surf.get_size()


class Clicker(ImageObject):
    def __init__(self, pos, image: str | pygame.Surface, size=0, direction=0, color_key=WHITE, position_at=TOPLEFT):
        super(Clicker, self).__init__(pos, image, size, direction, color_key, position_at)

    def draw_select(self, screen):
        pygame.draw.rect(screen, RED, self.rect, 5)

    def copy_color(self, src_color, dst_color):
        w, h = self.size
        img = self._image.copy()
        for x in range(w):
            for y in range(h):
                if img.get_at((x, y))[:-1] == src_color:
                    img.set_at((x, y), dst_color)
        return Clicker(self._pos, img, 0, self._direction, self._color_key, self._position_at)
