import pygame
import os

CANDY_PINK = (255, 182, 193)
CANDY_BLUE = (173, 216, 230)
CANDY_GREEN = (144, 238, 144)
CANDY_YELLOW = (255, 255, 153)
CANDY_PURPLE = (216, 191, 255)
CANDY_ORANGE = (255, 200, 130)
CANDY_RED = (255, 150, 150)

WHITE = (255, 255, 255)
BLACK = (50, 50, 50)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BG_COLOR = (230, 245, 255)

CUP_COLORS = [CANDY_PINK, CANDY_GREEN, CANDY_YELLOW, CANDY_PURPLE, CANDY_ORANGE, CANDY_RED, CANDY_BLUE]

SCREEN_W = 1024
SCREEN_H = 768


def get_font(size, bold=False):
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.Font(None, size)


class Button:
    def __init__(self, x, y, w, h, text, color=CANDY_BLUE, text_color=BLACK, font_size=28):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
        self.enabled = True

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        if not self.enabled:
            color = GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=12)
        font = get_font(self.font_size)
        text_surf = font.render(self.text, True, self.text_color if self.enabled else DARK_GRAY)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.enabled and self.rect.collidepoint(mouse_pos) and mouse_pressed


class Slider:
    def __init__(self, x, y, w, min_val, max_val, current, label="", step=1):
        self.x = x
        self.y = y
        self.w = w
        self.h = 40
        self.min_val = min_val
        self.max_val = max_val
        self.value = current
        self.label = label
        self.step = step
        self.dragging = False
        self.knob_radius = 14

    def draw(self, surface):
        font = get_font(24)
        label_surf = font.render(f"{self.label}: {self.value}", True, BLACK)
        surface.blit(label_surf, (self.x, self.y - 30))

        track_y = self.y + self.h // 2
        pygame.draw.line(surface, GRAY, (self.x, track_y), (self.x + self.w, track_y), 6)

        ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        knob_x = self.x + int(ratio * self.w)
        pygame.draw.circle(surface, CANDY_PURPLE, (knob_x, track_y), self.knob_radius)
        pygame.draw.circle(surface, DARK_GRAY, (knob_x, track_y), self.knob_radius, 2)

    def handle_event(self, event):
        track_y = self.y + self.h // 2
        if event.type == pygame.MOUSEBUTTONDOWN:
            ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
            knob_x = self.x + int(ratio * self.w)
            dx = event.pos[0] - knob_x
            dy = event.pos[1] - track_y
            if dx * dx + dy * dy <= (self.knob_radius + 5) ** 2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            ratio = (event.pos[0] - self.x) / max(1, self.w)
            ratio = max(0, min(1, ratio))
            raw = self.min_val + ratio * (self.max_val - self.min_val)
            self.value = round(raw / self.step) * self.step
            self.value = max(self.min_val, min(self.max_val, self.value))


class TextInput:
    def __init__(self, x, y, w, h, placeholder="", font_size=26):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font_size = font_size
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface):
        color = CANDY_BLUE if self.active else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY if self.active else GRAY, self.rect, 2, border_radius=8)

        font = get_font(self.font_size)
        if self.text:
            text_surf = font.render(self.text, True, BLACK)
        else:
            text_surf = font.render(self.placeholder, True, GRAY)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)

        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 2 if self.text else self.rect.x + 10
            pygame.draw.line(surface, BLACK, (cursor_x, self.rect.y + 8), (cursor_x, self.rect.bottom - 8), 2)

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "enter"
            elif event.unicode and len(self.text) < 30:
                self.text += event.unicode
        return None
