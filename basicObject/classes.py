from definitions import *


class ScreenObject:
    def __init__(self, pos: POSITION, size: POSITION, position_at: str = TOPLEFT):
        self._pos = (0, 0)
        self._size = size
        self._position_at = position_at
        self.pos = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        rect = self.rect
        if self._position_at == TOPLEFT:
            rect.topleft = pos
        elif self._position_at == CENTER:
            rect.center = pos
        elif self._position_at == TOPRIGHT:
            rect.topright = pos
        elif self._position_at == BOTTOMLEFT:
            rect.bottomleft = pos
        elif self._position_at == BOTTOMRIGHT:
            rect.bottomright = pos
        else:
            raise ValueError
        self._pos = rect.topleft

    @property
    def size(self):
        return self._size

    @property
    def rect(self):
        return pygame.Rect(self._pos, self._size)

    def is_touch(self, other: {rect}):
        return self.rect.colliderect(other.rect)

    def draw(self, screen: pygame.Surface):
        pass

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect)


class BlockObject(ScreenObject):
    def __init__(self, pos: POSITION, size: POSITION, color, position_at: str = TOPLEFT):
        super(BlockObject, self).__init__(pos, size, position_at)
        self._color = color

    def draw(self, screen):
        screen.fill(self._color, self.rect)


class CircleObject(ScreenObject):
    def __init__(self, pos: POSITION, radius: int, color, position_at: str = CENTER):
        super(CircleObject, self).__init__(pos, (radius * 2, radius * 2), position_at)
        self._color = color
        self._radius = radius

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self._color, self.rect.center, self._radius)

    @property
    def color(self):
        return self._color


class ImageObject(ScreenObject):
    def __init__(self, pos, image: str | pygame.Surface, size: int = 0, direction=0, color_key=WHITE,
                 position_at: str = TOPLEFT):
        self._image = pygame.image.load(image) if type(image) == str else image.copy()
        self._color_key = color_key
        if color_key:
            self._image = self._image.convert()
            self._image.set_colorkey(color_key)
        if size != 0:
            new_size = int(self._image.get_rect().width * size), int(self._image.get_rect().height * size)
            self._image = pygame.transform.scale(self._image, new_size)
        super(ImageObject, self).__init__(pos, self._image.get_size(), position_at)
        self._direction = direction

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._image = pygame.transform.scale(self._image, size)
        self._size = self._image.get_size()

    @property
    def direction(self):
        return self._direction

    @property
    def _display_image(self):
        return pygame.transform.rotate(self._image, self._direction)

    def draw(self, screen):
        screen.blit(self._display_image, self._pos)

    def to_bytes(self):
        image = pygame.transform.scale(self._image, (DEFAULT_BLOCK_SIZE, DEFAULT_BLOCK_SIZE))
        return pygame.surfarray.array3d(image)

    def repos(self, pos, direction=None):
        self._pos = pos
        if direction is not None:
            self._direction = direction
