import pygame
import math
from game import theme as T
from game.ui_components import get_font


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def ease_out_back(t, overshoot=T.SPRING_OVERSHOOT):
    """Spring/back easing — overshoots then settles."""
    c1 = overshoot
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def ease_out_elastic(t):
    if t == 0 or t == 1:
        return t
    p = 0.3
    return pow(2, -10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1


class Cup:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = T.CUP_ORANGE
        self.lifted = False
        self.lift_offset = 0
        self.shake_offset = 0
        self.glow = 0.0  # 0..1 — gold glow intensity
        self.target_x = x
        self.start_x = x
        self.ball_content = None
        self.ball_type = "text"

    def draw(self, surface, show_ball=False):
        cup_y = self.y - self.lift_offset
        cx = self.x + self.shake_offset

        # ground shadow (stays at base height, fades when lifted)
        ground_y = self.y + self.height + 6
        shadow_w = int(self.width * (1.0 + self.lift_offset / 300))
        shadow_h = max(6, 14 - self.lift_offset // 18)
        shadow_alpha = max(40, 110 - self.lift_offset // 2)
        sh_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(sh_surf, (40, 25, 15, shadow_alpha),
                            (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(sh_surf, (cx - shadow_w, ground_y - shadow_h))

        # gold glow under cup (when target reveal)
        if self.glow > 0.01:
            glow_r = int(self.width * 1.2)
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            for i in range(6):
                a = int(40 * self.glow * (1 - i / 6))
                pygame.draw.circle(glow_surf,
                                   (T.GOLD[0], T.GOLD[1], T.GOLD[2], a),
                                   (glow_r, glow_r), glow_r - i * 6)
            surface.blit(glow_surf, (cx - glow_r, cup_y + self.height // 2 - glow_r),
                         special_flags=pygame.BLEND_PREMULTIPLIED if False else 0)

        top_w = int(self.width * 0.72)
        # cup body (trapezoid)
        body_pts = [
            (cx - self.width // 2, cup_y + self.height),
            (cx + self.width // 2, cup_y + self.height),
            (cx + top_w // 2, cup_y),
            (cx - top_w // 2, cup_y),
        ]
        pygame.draw.polygon(surface, self.color, body_pts)
        # darker shaded right side
        shade_pts = [
            (cx + top_w // 4, cup_y),
            (cx + top_w // 2, cup_y),
            (cx + self.width // 2, cup_y + self.height),
            (cx + self.width // 4, cup_y + self.height),
        ]
        pygame.draw.polygon(surface, T.CUP_ORANGE_DARK, shade_pts)
        # outline
        pygame.draw.polygon(surface, T.WOOD_DARK, body_pts, 3)

        # rim (top ellipse)
        rim_rect = pygame.Rect(cx - top_w // 2 - 6, cup_y - 9, top_w + 12, 18)
        pygame.draw.ellipse(surface, T.CUP_ORANGE_DARK, rim_rect)
        inner_rim = rim_rect.inflate(-6, -6)
        pygame.draw.ellipse(surface, T.WOOD_DARK, inner_rim)
        pygame.draw.ellipse(surface, T.WOOD_DARK, rim_rect, 3)

        # left highlight stripe
        hl_pts = [
            (cx - self.width // 3, cup_y + 8),
            (cx - self.width // 3 + 6, cup_y + 8),
            (cx - self.width // 3 + 3, cup_y + self.height - 12),
            (cx - self.width // 3 - 4, cup_y + self.height - 12),
        ]
        pygame.draw.polygon(surface, T.CUP_ORANGE_HIGHLIGHT, hl_pts)

        # gold band when glowing
        if self.glow > 0.01:
            band_rect = pygame.Rect(cx - top_w // 2 - 4, cup_y - 4, top_w + 8, 8)
            pygame.draw.ellipse(surface, T.GOLD, band_rect)
            pygame.draw.ellipse(surface, T.GOLD_DARK, band_rect, 2)

        if (show_ball or self.lifted) and self.ball_content is not None:
            self._draw_ball(surface, cx)

    def _draw_ball(self, surface, cx=None):
        if cx is None:
            cx = self.x + self.shake_offset
        ball_y = self.y + self.height - 30
        ball_radius = min(self.width // 3, 35)
        # ball shadow
        shadow_surf = pygame.Surface((ball_radius * 3, ball_radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (40, 25, 15, 90),
                            (0, 0, ball_radius * 3, ball_radius))
        surface.blit(shadow_surf, (cx - ball_radius * 3 // 2, ball_y + ball_radius // 2))

        pygame.draw.circle(surface, T.PARCHMENT, (cx, ball_y), ball_radius)
        pygame.draw.circle(surface, T.GOLD_DARK, (cx, ball_y), ball_radius, 3)
        pygame.draw.circle(surface, T.GOLD, (cx, ball_y), ball_radius - 3, 1)

        if self.ball_content:
            if self.ball_type == "text":
                font_size = max(16, min(30, ball_radius))
                font = get_font(font_size, bold=True)
                text_surf = font.render(str(self.ball_content), True, T.TEXT_DARK)
                text_rect = text_surf.get_rect(center=(cx, ball_y))
                if text_rect.width > ball_radius * 1.8:
                    font_size = max(12, font_size - 6)
                    font = get_font(font_size, bold=True)
                    text_surf = font.render(str(self.ball_content), True, T.TEXT_DARK)
                    text_rect = text_surf.get_rect(center=(cx, ball_y))
                surface.blit(text_surf, text_rect)
            elif self.ball_type == "image" and isinstance(self.ball_content, pygame.Surface):
                img = self.ball_content
                max_size = int(ball_radius * 1.5)
                img_w, img_h = img.get_size()
                scale = min(max_size / img_w, max_size / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                scaled = pygame.transform.smoothscale(img, (new_w, new_h))
                img_rect = scaled.get_rect(center=(cx, ball_y))
                surface.blit(scaled, img_rect)


class AnimationManager:
    def __init__(self):
        self.animations = []
        self.is_animating = False

    def add_swap(self, cup_a, cup_b, duration_ms):
        self.animations.append({
            "type": "swap",
            "cup_a": cup_a,
            "cup_b": cup_b,
            "duration": duration_ms,
            "elapsed": 0,
            "start_a": None,
            "start_b": None,
            "initialized": False,
        })

    def add_lift(self, cups, duration_ms=400, lift_amount=120):
        self.animations.append({
            "type": "lift",
            "cups": cups,
            "duration": duration_ms,
            "elapsed": 0,
            "lift_amount": lift_amount,
            "direction": "up",
        })

    def add_lower(self, cups, duration_ms=400):
        self.animations.append({
            "type": "lower",
            "cups": cups,
            "duration": duration_ms,
            "elapsed": 0,
            "start_offsets": None,
        })

    def add_scramble(self, cups, duration_ms):
        """All cups shuffle to random positions simultaneously."""
        import random
        positions = [cup.x for cup in cups]
        shuffled = positions[:]
        random.shuffle(shuffled)
        self.animations.append({
            "type": "scramble",
            "cups": cups,
            "duration": duration_ms,
            "elapsed": 0,
            "start_positions": None,
            "target_positions": shuffled,
        })

    def add_pause(self, duration_ms):
        self.animations.append({
            "type": "pause",
            "duration": duration_ms,
            "elapsed": 0,
        })

    def add_shake(self, cup, duration_ms=400, intensity=14):
        """Side-to-side shake (used for wrong-answer feedback)."""
        self.animations.append({
            "type": "shake",
            "cup": cup,
            "duration": duration_ms,
            "elapsed": 0,
            "intensity": intensity,
        })

    def add_glow(self, cup, duration_ms=600, peak=1.0):
        """Pulse a cup's gold glow in then back out."""
        self.animations.append({
            "type": "glow",
            "cup": cup,
            "duration": duration_ms,
            "elapsed": 0,
            "peak": peak,
        })

    def update(self, dt):
        if not self.animations:
            self.is_animating = False
            return

        self.is_animating = True
        anim = self.animations[0]
        anim["elapsed"] += dt

        t = min(1.0, anim["elapsed"] / anim["duration"])
        eased = ease_in_out(t)

        if anim["type"] == "swap":
            cup_a = anim["cup_a"]
            cup_b = anim["cup_b"]
            if not anim["initialized"]:
                anim["start_a"] = cup_a.x
                anim["start_b"] = cup_b.x
                anim["initialized"] = True
            start_a = anim["start_a"]
            start_b = anim["start_b"]
            cup_a.x = int(start_a + (start_b - start_a) * eased)
            cup_b.x = int(start_b + (start_a - start_b) * eased)

        elif anim["type"] == "scramble":
            cups = anim["cups"]
            if anim["start_positions"] is None:
                anim["start_positions"] = [cup.x for cup in cups]
            starts = anim["start_positions"]
            targets = anim["target_positions"]
            for i, cup in enumerate(cups):
                cup.x = int(starts[i] + (targets[i] - starts[i]) * eased)

        elif anim["type"] == "lift":
            for cup in anim["cups"]:
                cup.lift_offset = int(anim["lift_amount"] * eased)
                if t >= 1.0:
                    cup.lifted = True

        elif anim["type"] == "lower":
            if anim["start_offsets"] is None:
                anim["start_offsets"] = [cup.lift_offset for cup in anim["cups"]]
            for i, cup in enumerate(anim["cups"]):
                start_off = anim["start_offsets"][i]
                cup.lift_offset = int(start_off * (1 - eased)) if t < 1.0 else 0
                if t >= 1.0:
                    cup.lifted = False
                    cup.lift_offset = 0

        elif anim["type"] == "shake":
            cup = anim["cup"]
            decay = 1 - t
            cup.shake_offset = int(math.sin(t * math.pi * 8) * anim["intensity"] * decay)
            if t >= 1.0:
                cup.shake_offset = 0

        elif anim["type"] == "glow":
            cup = anim["cup"]
            # bell curve: rise then fall
            cup.glow = anim["peak"] * math.sin(t * math.pi)
            if t >= 1.0:
                cup.glow = 0.0

        if t >= 1.0:
            if anim["type"] == "swap":
                cup_a = anim["cup_a"]
                cup_b = anim["cup_b"]
                cup_a.x = anim["start_b"]
                cup_b.x = anim["start_a"]
            elif anim["type"] == "scramble":
                cups = anim["cups"]
                targets = anim["target_positions"]
                for i, cup in enumerate(cups):
                    cup.x = targets[i]
            self.animations.pop(0)

    @property
    def done(self):
        return len(self.animations) == 0
