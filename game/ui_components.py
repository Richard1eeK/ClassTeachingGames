"""Stardew Valley themed UI components."""
import pygame
import os
import math

from game import theme as T
from game.theme import (
    SCREEN_W, SCREEN_H,
    BG_COLOR, BLACK, WHITE, GRAY, DARK_GRAY,
    CANDY_PINK, CANDY_BLUE, CANDY_GREEN, CANDY_YELLOW,
    CANDY_PURPLE, CANDY_ORANGE, CANDY_RED, CUP_COLOR,
)
from game.decorations import draw_wood_plank, draw_parchment_card


def get_font(size, bold=False):
    bundled = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts", "font.ttf")
    if os.path.exists(bundled):
        try:
            f = pygame.font.Font(bundled, size)
            if bold:
                f.set_bold(True)
            return f
        except Exception:
            pass

    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                f = pygame.font.Font(path, size)
                if bold:
                    f.set_bold(True)
                return f
            except Exception:
                continue
    try:
        for name in ["helvetica", "segoeui", "arial", "dejavusans"]:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                return font
    except Exception:
        pass
    return pygame.font.Font(None, size)


def render_text_outlined(text, size, color, outline_color=T.WOOD_DARK, outline_w=2, bold=False):
    """Render text with a thick outline (like Stardew dialog text)."""
    font = get_font(size, bold=bold)
    base = font.render(text, True, color)
    w, h = base.get_size()
    pad = outline_w + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    outline_surf = font.render(text, True, outline_color)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx == 0 and dy == 0:
                continue
            out.blit(outline_surf, (pad + dx, pad + dy))
    out.blit(base, (pad, pad))
    return out


class Button:
    """Wood plank button with press-down feedback."""

    def __init__(self, x, y, w, h, text, color=T.SV_BLUE, text_color=T.TEXT_LIGHT,
                 font_size=T.FONT_BODY, icon=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.dark = self._darken(color, 0.65)
        self.light = self._lighten(color, 1.25)
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self.icon = icon  # callable(surface, x, y, size, color)
        self._press_anim = 0.0  # 0..1

    @staticmethod
    def _darken(color, factor):
        return tuple(max(0, int(c * factor)) for c in color)

    @staticmethod
    def _lighten(color, factor):
        return tuple(min(255, int(c * factor)) for c in color)

    def draw(self, surface):
        rect = self.rect.copy()
        # press depth offset
        offset = int(4 * self._press_anim)
        rect.y += offset

        color = self.color
        if not self.enabled:
            color = T.PARCHMENT_SHADOW
            light = T.PARCHMENT_DARK
            dark = T.WOOD_LIGHT
        else:
            color = self.light if self.hovered else self.color
            light = self._lighten(color, 1.18)
            dark = self._darken(color, 0.6)

        # shadow (skip when pressed for press-down effect)
        if not self.pressed and self.enabled:
            shadow_surf = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
            for i in range(4):
                a = 28 - i * 6
                pygame.draw.rect(
                    shadow_surf,
                    (30, 18, 10, max(0, a)),
                    (4 - i, 4 - i, rect.width + i * 2, rect.height + i * 2),
                    border_radius=T.RADIUS_MD + i,
                )
            surface.blit(shadow_surf, (rect.x - 4, rect.y))

        # body
        pygame.draw.rect(surface, color, rect, border_radius=T.RADIUS_MD)
        # top highlight
        hl = pygame.Rect(rect.x + 4, rect.y + 3, rect.width - 8, max(2, rect.height // 4))
        pygame.draw.rect(surface, light, hl, border_radius=T.RADIUS_SM)
        # bottom shade
        sh = pygame.Rect(rect.x + 4, rect.bottom - rect.height // 5, rect.width - 8, rect.height // 6)
        pygame.draw.rect(surface, dark, sh, border_radius=T.RADIUS_SM)
        # outline
        pygame.draw.rect(surface, T.WOOD_DARK, rect, 3, border_radius=T.RADIUS_MD)

        # text + optional icon
        text_color = self.text_color if self.enabled else T.TEXT_MUTED
        text_surf = render_text_outlined(self.text, self.font_size, text_color,
                                         outline_color=T.WOOD_DARK, outline_w=2, bold=True)
        tw = text_surf.get_width()
        if self.icon:
            icon_size = max(10, self.font_size // 2)
            total_w = tw + icon_size * 2 + 12
            icon_x = rect.centerx - total_w // 2 + icon_size
            icon_y = rect.centery
            self.icon(surface, icon_x, icon_y, icon_size, text_color)
            text_x = icon_x + icon_size + 8
            text_y = rect.centery - text_surf.get_height() // 2
            surface.blit(text_surf, (text_x, text_y))
        else:
            surface.blit(text_surf, (rect.centerx - tw // 2,
                                     rect.centery - text_surf.get_height() // 2))

    def update(self, mouse_pos, dt=16):
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        target = 1.0 if self.pressed else 0.0
        self._press_anim += (target - self._press_anim) * min(1.0, dt / 80)

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
        self.knob_radius = 16

    def draw(self, surface):
        font = get_font(T.FONT_BODY, bold=True)
        label_surf = render_text_outlined(
            f"{self.label}: {self.value}", T.FONT_BODY, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True
        )
        surface.blit(label_surf, (self.x - 2, self.y - 34))

        track_y = self.y + self.h // 2
        # track shadow
        pygame.draw.line(surface, T.WOOD_DARK, (self.x, track_y + 2),
                         (self.x + self.w, track_y + 2), 8)
        # track base
        pygame.draw.line(surface, T.WOOD_LIGHT, (self.x, track_y),
                         (self.x + self.w, track_y), 6)
        ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        knob_x = self.x + int(ratio * self.w)
        # filled portion (gold)
        if knob_x > self.x:
            pygame.draw.line(surface, T.GOLD, (self.x, track_y), (knob_x, track_y), 6)

        # knob (gold coin style)
        pygame.draw.circle(surface, T.WOOD_DARK, (knob_x, track_y + 2), self.knob_radius)
        pygame.draw.circle(surface, T.GOLD_DARK, (knob_x, track_y), self.knob_radius)
        pygame.draw.circle(surface, T.GOLD, (knob_x, track_y), self.knob_radius - 2)
        pygame.draw.circle(surface, T.GOLD_LIGHT, (knob_x - 4, track_y - 4), self.knob_radius // 3)
        pygame.draw.circle(surface, T.WOOD_DARK, (knob_x, track_y), self.knob_radius, 2)

    def handle_event(self, event):
        track_y = self.y + self.h // 2
        if event.type == pygame.MOUSEBUTTONDOWN:
            ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
            knob_x = self.x + int(ratio * self.w)
            dx = event.pos[0] - knob_x
            dy = event.pos[1] - track_y
            if dx * dx + dy * dy <= (self.knob_radius + 6) ** 2:
                self.dragging = True
            elif self.x <= event.pos[0] <= self.x + self.w and abs(dy) < 20:
                # click anywhere on track jumps to value
                self._set_from_x(event.pos[0])
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_x(event.pos[0])

    def _set_from_x(self, px):
        ratio = (px - self.x) / max(1, self.w)
        ratio = max(0.0, min(1.0, ratio))
        raw = self.min_val + ratio * (self.max_val - self.min_val)
        self.value = round(raw / self.step) * self.step
        self.value = max(self.min_val, min(self.max_val, self.value))


class TextInput:
    def __init__(self, x, y, w, h, placeholder="", font_size=T.FONT_BODY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.font_size = font_size
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface):
        # parchment-ish input
        fill = T.PARCHMENT if self.active else T.PARCHMENT_DARK
        pygame.draw.rect(surface, fill, self.rect, border_radius=T.RADIUS_MD)
        border = T.GOLD_DARK if self.active else T.WOOD_BROWN
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=T.RADIUS_MD)

        font = get_font(self.font_size)
        if self.text:
            text_surf = font.render(self.text, True, T.TEXT_DARK)
        else:
            text_surf = font.render(self.placeholder, True, T.TEXT_MUTED)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 14, self.rect.centery))
        surface.blit(text_surf, text_rect)

        if self.active and self.cursor_visible:
            cursor_x = text_rect.right + 3 if self.text else self.rect.x + 14
            pygame.draw.line(surface, T.TEXT_DARK,
                             (cursor_x, self.rect.y + 8),
                             (cursor_x, self.rect.bottom - 8), 2)

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


class Card:
    """Parchment card container — a positional helper for layout."""

    def __init__(self, x, y, w, h, title=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title

    def draw(self, surface):
        draw_parchment_card(surface, self.rect)
        if self.title:
            title_surf = render_text_outlined(
                self.title, T.FONT_HEADING, T.TEXT_LIGHT,
                outline_color=T.WOOD_DARK, outline_w=2, bold=True,
            )
            tx = self.rect.centerx - title_surf.get_width() // 2
            ty = self.rect.y - title_surf.get_height() // 2 + 4
            # ribbon behind title
            ribbon = pygame.Rect(tx - 16, ty + 4, title_surf.get_width() + 32, title_surf.get_height() - 4)
            draw_wood_plank(surface, ribbon, color=T.WOOD_BROWN, radius=T.RADIUS_MD, shadow=True)
            surface.blit(title_surf, (tx, ty))

    def inner_rect(self, padding=T.SPACE_LG):
        return self.rect.inflate(-padding * 2, -padding * 2).move(0, 0)


class WoodSign:
    """Hanging wood sign for titles."""

    def __init__(self, x, y, w, h, text, font_size=T.FONT_TITLE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font_size = font_size

    def draw(self, surface):
        # rope
        rope_color = T.WOOD_DARK
        pygame.draw.line(surface, rope_color, (self.rect.left + 30, self.rect.top - 30),
                         (self.rect.left + 30, self.rect.top + 4), 3)
        pygame.draw.line(surface, rope_color, (self.rect.right - 30, self.rect.top - 30),
                         (self.rect.right - 30, self.rect.top + 4), 3)
        # plank
        draw_wood_plank(surface, self.rect, color=T.WOOD_BROWN, radius=T.RADIUS_MD, shadow=True)
        text_surf = render_text_outlined(self.text, self.font_size, T.TEXT_LIGHT,
                                         outline_color=T.WOOD_DARK, outline_w=2, bold=True)
        surface.blit(text_surf, (self.rect.centerx - text_surf.get_width() // 2,
                                 self.rect.centery - text_surf.get_height() // 2))


# Legacy name aliases (kept so existing imports don't break during migration)
__all__ = [
    "Button", "Slider", "TextInput", "Card", "WoodSign",
    "get_font", "render_text_outlined",
    "SCREEN_W", "SCREEN_H",
    "BG_COLOR", "BLACK", "WHITE", "GRAY", "DARK_GRAY",
    "CANDY_PINK", "CANDY_BLUE", "CANDY_GREEN", "CANDY_YELLOW",
    "CANDY_PURPLE", "CANDY_ORANGE", "CANDY_RED", "CUP_COLOR",
]
