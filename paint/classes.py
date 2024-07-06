from font import *
from .constants import *
import queue


class PaintColor(CircleObject):
    def __init__(self, paint_bar, color):
        super(PaintColor, self).__init__(paint_bar.next_pos, paint_bar.radius, color)

    def draw_select(self, screen):
        pygame.draw.circle(screen, RED, self.rect.center, self._radius + 5, 5)


class PaintColorCustom(PaintColor):
    def __init__(self, paint_bar, data):
        super(PaintColorCustom, self).__init__(paint_bar, None)
        self._image = ImageObject(self._pos, PAINT_SELECTOR_IMAGE)
        self._image.size = self._radius*2, self._radius*2
        x, y = self.rect.midleft
        scale_length = 256
        self._r = ScaleBar((x+settings.text_size*2, y - settings.text_size * 2), 'red', scale_length, data, 0, 0, 255)
        self._g = ScaleBar((x+settings.text_size*2, y), 'green', scale_length, data, 0, 0, 255)
        self._b = ScaleBar((x+settings.text_size*2, y + settings.text_size * 2), 'blue', scale_length, data, 0, 0, 255)
        self._is_active = False

    def _scale_touch_mouse(self):
        return self._r.title_is_touch_mouse() or self._g.title_is_touch_mouse() or self._b.title_is_touch_mouse()

    def active(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if self.is_touch_mouse() or self._is_active and self._scale_touch_mouse():
                        self._is_active = True
                    else:
                        self._is_active = False
        if self._is_active:
            self._r.active(events)
            self._g.active(events)
            self._b.active(events)

    @property
    def _color(self):
        return self._r.real_value, self._g.real_value, self._b.real_value

    @_color.setter
    def _color(self, color):
        if color:
            r, g, b = color
            self._r.real_value = r
            self._g.real_value = g
            self._b.real_value = b

    def draw(self, screen):
        self._image.draw(screen)
        if self._is_active:
            self._r.draw(screen)
            self._g.draw(screen)
            self._b.draw(screen)

    def set_color(self, value):
        self._color = value


class ToolPaintBar:
    def __init__(self, pos):
        self._pos = pos
        self._pos_gen = next_pos(self._pos, (DEFAULT_BLOCK_SIZE * settings.delta_size * 2, 0))
        self._tools = [Clicker(self.next_pos, PAINT_PENCIL_IMAGE),
                       Clicker(self.next_pos, PAINT_SELECT_IMAGE),
                       Clicker(self.next_pos, PAINT_FILL_IMAGE)]
        self._tool_index = 0

    @property
    def next_pos(self):
        return next(self._pos_gen)

    @property
    def selected_tool(self):
        return self._tools[self._tool_index]

    @property
    def mode(self):
        return PAINT_MODES[self._tool_index]

    def is_touch_mouse(self):
        for tool in self._tools:
            if tool.is_touch_mouse():
                return tool
        return None

    def active(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    tool = self.is_touch_mouse()
                    if tool:
                        self._tool_index = self._tools.index(tool)

    def draw(self, screen):
        for tool in self._tools:
            tool.draw(screen)
        self.selected_tool.draw_select(screen)

    @mode.setter
    def mode(self, mode):
        self._tool_index = PAINT_MODES.index(mode)


class PaintBar:
    def __init__(self, pos_gen, data):
        self._pos = next(pos_gen)
        self._radius = settings.text_size // 2
        self._pos_gen = next_pos(self._pos, (self._radius * 4, 0))
        self._color_index = 0
        self._size_index = 0
        self._colors = [PaintColor(self, color) for color in COLORS]
        self._custom_color = PaintColorCustom(self, data)
        self._colors.append(self._custom_color)
        self._tool_bar = ToolPaintBar(next(pos_gen))

    @property
    def next_pos(self):
        return next(self._pos_gen)

    @property
    def selected_color(self):
        return self._colors[self._color_index].color

    @property
    def radius(self):
        return self._radius

    @property
    def mode(self):
        return self._tool_bar.mode

    @mode.setter
    def mode(self, mode):
        self._tool_bar.mode = mode

    def is_touch_mouse(self):
        for paint in self._colors:
            if paint.is_touch_mouse():
                return paint
        return None

    def active(self, events):
        self._tool_bar.active(events)
        self._custom_color.active(events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    paint = self.is_touch_mouse()
                    if paint:
                        self._color_index = self._colors.index(paint)
                elif event.button == MOUSE_SCROLL_UP:
                    self._size_index = (self._size_index + 1) % 20
                elif event.button == MOUSE_SCROLL_DOWN:
                    self._size_index = (self._size_index - 1) % 20

    @property
    def mouse_rect(self):
        if self.mode == PAINT_PENCIL:
            rect_size = settings.pixel_ratio * (self._size_index + 1)
        else:
            rect_size = 1
        mouse_rect = pygame.Rect(pygame.mouse.get_pos() + (rect_size, rect_size))
        if self.mode == PAINT_PENCIL:
            mouse_rect.bottomright = pygame.mouse.get_pos()
        return mouse_rect

    def draw(self, screen):
        for paint in self._colors:
            paint.draw(screen)
        self._colors[self._color_index].draw_select(screen)
        self._tool_bar.draw(screen)
        if self.mode == PAINT_PENCIL:
            pygame.draw.rect(screen, self.selected_color, self.mouse_rect)

    @selected_color.setter
    def selected_color(self, value):
        self._color_index = self._colors.index(self._custom_color)
        self._custom_color.set_color(value)


class ImageEditor(ImageObject):
    def __init__(self, pos, image: pygame.Surface, paint_bar: PaintBar):
        super(ImageEditor, self).__init__(pos, image, color_key=None)
        self._paint_bar = paint_bar
        w, h = self.size
        self.size = w * 2, h * 2
        self._pressed = False

    def is_touch_mouse(self):
        x1, y1 = pygame.mouse.get_pos()
        width1, height1 = 1, 1
        mouse_rect = pygame.Rect(x1, y1, width1, height1)
        return mouse_rect.colliderect(self.rect) or self._paint_bar.mouse_rect.colliderect(self.rect)

    @property
    def mouse_rect(self):
        x1, y1, w1, h1 = self._paint_bar.mouse_rect
        x2, y2 = self.rect.topleft
        return pygame.Rect(x1-x2, y1-y2, w1, h1)

    def _fill_color(self):
        mouse_pos = self.mouse_rect.topleft
        src_color = self._image.get_at(self.mouse_rect.topleft)[:-1]
        dst_color = self._paint_bar.selected_color
        if src_color == dst_color:
            return
        q = queue.Queue()
        q.put(mouse_pos)
        been_at = set()
        while not q.empty():
            x, y = q.get()
            if (x, y) in been_at:
                continue
            else:
                been_at.add((x, y))
            self._image.set_at((x, y), dst_color)
            try:
                if self._image.get_at((x + 1, y))[:-1] == src_color:
                    q.put((x + 1, y))
            except IndexError:
                pass
            try:
                if self._image.get_at((x - 1, y))[:-1] == src_color:
                    q.put((x - 1, y))
            except IndexError:
                pass
            try:
                if self._image.get_at((x, y + 1))[:-1] == src_color:
                    q.put((x, y + 1))
            except IndexError:
                pass
            try:
                if self._image.get_at((x, y - 1))[:-1] == src_color:
                    q.put((x, y - 1))
            except IndexError:
                pass

    def active(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_LEFT:
                    if self.is_touch_mouse():
                        if self._paint_bar.mode == PAINT_PENCIL:
                            pygame.draw.rect(self._image, self._paint_bar.selected_color, self.mouse_rect)
                            self._pressed = True
                        elif self._paint_bar.mode == PAINT_SELECT:
                            self._paint_bar.selected_color = self._image.get_at(self.mouse_rect.topleft)[:-1]
                            self._paint_bar.mode = PAINT_PENCIL
                        elif self._paint_bar.mode == PAINT_FILL:
                            self._fill_color()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == MOUSE_LEFT:
                    self._pressed = False
            elif event.type == pygame.MOUSEMOTION:
                if self._pressed:
                    pygame.draw.rect(self._image, self._paint_bar.selected_color, self.mouse_rect)
