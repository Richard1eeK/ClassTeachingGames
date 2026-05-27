import pygame
import math
from functools import lru_cache
from game import theme as T
from game.assets import load_image
from game.ui_components import get_font

TARGET_CARD_FILL = (255, 255, 255)
TARGET_CARD_TEXT = (20, 20, 20)


@lru_cache(maxsize=128)
def _cached_smoothscale(surface_id, width, height, surface_ref):
    """Cache smoothscale results. surface_ref is a weak reference holder (not used in cache key)."""
    return pygame.transform.smoothscale(surface_ref, (width, height))


def get_scaled_image(surface, target_width, target_height):
    """Get a cached smoothscaled version of the surface."""
    return _cached_smoothscale(id(surface), target_width, target_height, surface)


def fit_text_surface(text, max_width, max_height, start_size, min_size=10):
    font_size = start_size
    while font_size >= min_size:
        font = get_font(font_size, bold=True)
        surface = font.render(str(text), True, TARGET_CARD_TEXT)
        if surface.get_width() <= max_width and surface.get_height() <= max_height:
            return surface
        font_size -= 1
    font = get_font(min_size, bold=True)
    return font.render(str(text), True, TARGET_CARD_TEXT)


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
        self._cached_cup_sprite = None
        self._cached_size = None
        self._shadow_cache = {}
        self._glow_cache = {}

    def draw(self, surface, show_ball=False):
        cup_y = self.y - self.lift_offset
        cx = self.x + self.shake_offset

        # ground shadow (stays at base height, fades when lifted)
        ground_y = self.y + self.height + 6
        shadow_w = int(self.width * (1.0 + self.lift_offset / 300))
        shadow_h = max(6, 14 - self.lift_offset // 18)
        shadow_alpha = max(40, 110 - self.lift_offset // 2)

        # Cache shadow surface by size
        shadow_key = (shadow_w, shadow_h, shadow_alpha)
        if shadow_key not in self._shadow_cache:
            sh_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(sh_surf, (*T.SHADOW_DARK, shadow_alpha),
                                (0, 0, shadow_w * 2, shadow_h * 2))
            self._shadow_cache[shadow_key] = sh_surf
        surface.blit(self._shadow_cache[shadow_key], (cx - shadow_w, ground_y - shadow_h))

        # gold glow under cup (when target reveal)
        if self.glow > 0.01:
            glow_r = int(self.width * 1.2)
            glow_key = glow_r
            if glow_key not in self._glow_cache:
                glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                for i in range(6):
                    a = int(40 * (1 - i / 6))
                    pygame.draw.circle(glow_surf,
                                       (T.GOLD[0], T.GOLD[1], T.GOLD[2], a),
                                       (glow_r, glow_r), glow_r - i * 6)
                self._glow_cache[glow_key] = glow_surf

            glow_surf = self._glow_cache[glow_key].copy()
            glow_surf.set_alpha(int(255 * self.glow))
            surface.blit(glow_surf, (cx - glow_r, cup_y + self.height // 2 - glow_r))

        cup_sprite = load_image("assets", "pixel", "cup.png")
        if cup_sprite:
            if self._cached_size != (self.width, self.height):
                self._cached_cup_sprite = pygame.transform.scale(cup_sprite, (self.width, self.height))
                self._cached_size = (self.width, self.height)
            surface.blit(self._cached_cup_sprite, (int(cx - self.width // 2), int(cup_y)))
        else:
            top_w = int(self.width * 0.72)
            body_pts = [
                (cx - self.width // 2, cup_y + self.height),
                (cx + self.width // 2, cup_y + self.height),
                (cx + top_w // 2, cup_y),
                (cx - top_w // 2, cup_y),
            ]
            pygame.draw.polygon(surface, self.color, body_pts)
            pygame.draw.polygon(surface, T.WOOD_DARK, body_pts, 3)

        if self.glow > 0.01:
            band_rect = pygame.Rect(cx - int(self.width * 0.38), cup_y + 5, int(self.width * 0.76), 8)
            pygame.draw.rect(surface, T.GOLD, band_rect)
            pygame.draw.rect(surface, T.GOLD_DARK, band_rect, 2)

        if (show_ball or self.lifted) and self.ball_content is not None:
            self._draw_ball(surface, cx)

    def _draw_ball(self, surface, cx=None):
        if cx is None:
            cx = self.x + self.shake_offset
        ball_y = self.y + self.height - 30
        ball_radius = min(self.width // 3, 52)
        # ball shadow
        shadow_surf = pygame.Surface((ball_radius * 3, ball_radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (*T.SHADOW_DARK, 72),
                            (0, 0, ball_radius * 3, ball_radius))
        surface.blit(shadow_surf, (cx - ball_radius * 3 // 2, ball_y + ball_radius // 2))

        card_w = max(ball_radius * 2, min(200, int(self.width * 1.6)))
        card_h = ball_radius * 2
        card = pygame.Rect(cx - card_w // 2, ball_y - card_h // 2, card_w, card_h)
        pygame.draw.rect(surface, T.WOOD_DARK, card)
        inner = card.inflate(-6, -6)
        pygame.draw.rect(surface, TARGET_CARD_FILL, inner)
        pygame.draw.rect(surface, T.GOLD_DARK, inner, 2)

        if self.ball_content:
            if self.ball_type == "text":
                text_surf = fit_text_surface(
                    self.ball_content,
                    inner.width - 6,
                    inner.height - 4,
                    start_size=max(18, min(36, ball_radius)),
                    min_size=10,
                )
                text_rect = text_surf.get_rect(center=inner.center)
                surface.blit(text_surf, text_rect)
            elif self.ball_type == "image" and isinstance(self.ball_content, pygame.Surface):
                img = self.ball_content
                max_size = int(ball_radius * 2.2)
                img_w, img_h = img.get_size()
                scale = min(max_size / img_w, max_size / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                scaled = get_scaled_image(img, new_w, new_h)
                img_rect = scaled.get_rect(center=(cx, ball_y))
                surface.blit(scaled, img_rect)


class MultiIntroBall:
    def __init__(self, x, y, base_radius, targets):
        self.x = x
        self.y = y
        self.base_radius = base_radius
        self.scale = 2.8
        self.targets = targets
        self.alpha = 0.0
        self.visible = False

    def draw(self, surface):
        if not self.visible or self.alpha <= 0.01:
            return
        count = max(1, len(self.targets))
        radius = int(self.base_radius * self.scale)
        card_w = max(180, min(260, int(radius * 3.4)))
        card_h = max(72, int(radius * 1.55))
        gap = 16
        total_w = card_w * count + gap * (count - 1)
        surf = pygame.Surface((total_w + 24, card_h + 28), pygame.SRCALPHA)
        for i, target in enumerate(self.targets):
            x = 12 + i * (card_w + gap)
            y = 8
            shadow = pygame.Rect(x + 5, y + 7, card_w, card_h)
            pygame.draw.rect(surf, (*T.SHADOW_DARK, 80), shadow)
            outer = pygame.Rect(x, y, card_w, card_h)
            pygame.draw.rect(surf, T.WOOD_DARK, outer)
            inner = outer.inflate(-12, -12)
            pygame.draw.rect(surf, TARGET_CARD_FILL, inner)
            pygame.draw.rect(surf, T.GOLD_DARK, inner, 3)
            if target["type"] == "text":
                text_surf = fit_text_surface(
                    target["content"], inner.width - 10, inner.height - 8,
                    start_size=max(20, int(radius * 0.72)), min_size=12,
                )
                surf.blit(text_surf, text_surf.get_rect(center=inner.center))
            elif target["type"] == "image" and isinstance(target["content"], pygame.Surface):
                img = target["content"]
                iw, ih = img.get_size()
                scale = min((inner.width - 8) / iw, (inner.height - 8) / ih)
                scaled = get_scaled_image(img, max(1, int(iw * scale)), max(1, int(ih * scale)))
                surf.blit(scaled, scaled.get_rect(center=inner.center))
        surf.set_alpha(int(255 * max(0.0, min(1.0, self.alpha))))
        surface.blit(surf, (int(self.x - surf.get_width() // 2), int(self.y - surf.get_height() // 2)))


class IntroBall:
    """A standalone ball used for the round-intro show + fly-in animation."""

    def __init__(self, x, y, base_radius, content, content_type):
        self.x = x
        self.y = y
        self.base_radius = base_radius  # final size when seated in cup
        self.scale = 2.8                # current scale relative to base_radius
        self.content = content
        self.content_type = content_type
        self.alpha = 0.0                # 0..1
        self.visible = False

    def draw(self, surface):
        if not self.visible or self.alpha <= 0.01:
            return
        radius = int(self.base_radius * self.scale)
        if radius < 2:
            return
        ball_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        cx = cy = radius * 2

        # shadow
        shadow = pygame.Surface((radius * 3, radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (*T.SHADOW_DARK, 72),
                            (0, 0, radius * 3, radius))
        ball_surf.blit(shadow, (cx - radius * 3 // 2, cy + radius // 2))

        card_w = min(radius * 4 - 12, max(radius * 2, int(radius * 3.2)))
        card_h = radius * 2
        outer = pygame.Rect(cx - card_w // 2, cy - card_h // 2, card_w, card_h)
        pygame.draw.rect(ball_surf, T.WOOD_DARK, outer)
        inner = outer.inflate(-max(8, radius // 7), -max(8, radius // 7))
        pygame.draw.rect(ball_surf, TARGET_CARD_FILL, inner)
        pygame.draw.rect(ball_surf, T.GOLD_DARK, inner, max(2, radius // 18))

        if self.content is not None:
            if self.content_type == "text":
                text_surf = fit_text_surface(
                    self.content,
                    inner.width - 8,
                    inner.height - 6,
                    start_size=max(20, int(radius * 0.86)),
                    min_size=14,
                )
                trect = text_surf.get_rect(center=inner.center)
                ball_surf.blit(text_surf, trect)
            elif self.content_type == "image" and isinstance(self.content, pygame.Surface):
                img = self.content
                max_size = int(radius * 1.7)
                iw, ih = img.get_size()
                s = min(max_size / iw, max_size / ih)
                scaled = get_scaled_image(img, int(iw * s), int(ih * s))
                irect = scaled.get_rect(center=(cx, cy))
                ball_surf.blit(scaled, irect)

        ball_surf.set_alpha(int(255 * max(0.0, min(1.0, self.alpha))))
        surface.blit(ball_surf, (int(self.x) - radius * 2, int(self.y) - radius * 2))


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

    def add_intro_show(self, intro_ball, duration_ms=2000, fade_in_ms=350,
                       fade_out_ms=0):
        """Show intro_ball at center: fade in, hold at scale, optional fade out."""
        self.animations.append({
            "type": "intro_show",
            "ball": intro_ball,
            "duration": duration_ms,
            "elapsed": 0,
            "fade_in": fade_in_ms,
            "fade_out": fade_out_ms,
        })

    def add_intro_fly(self, intro_ball, target_cup, duration_ms=800,
                      end_scale=1.0, arc_height=140):
        """Fly intro_ball along an arc into target_cup, scaling to end_scale."""
        self.animations.append({
            "type": "intro_fly",
            "ball": intro_ball,
            "target_cup": target_cup,
            "duration": duration_ms,
            "elapsed": 0,
            "start_x": None,
            "start_y": None,
            "start_scale": None,
            "end_scale": end_scale,
            "arc_height": arc_height,
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

        elif anim["type"] == "intro_show":
            ball = anim["ball"]
            ball.visible = True
            elapsed = anim["elapsed"]
            fade_in = anim["fade_in"]
            fade_out = anim["fade_out"]
            duration = anim["duration"]
            if fade_in > 0 and elapsed < fade_in:
                ball.alpha = elapsed / fade_in
            elif fade_out > 0 and elapsed > duration - fade_out:
                ball.alpha = max(0.0, (duration - elapsed) / fade_out)
            else:
                ball.alpha = 1.0

        elif anim["type"] == "intro_fly":
            ball = anim["ball"]
            target = anim["target_cup"]
            if anim["start_x"] is None:
                anim["start_x"] = ball.x
                anim["start_y"] = ball.y
                anim["start_scale"] = ball.scale
            sx = anim["start_x"]
            sy = anim["start_y"]
            ss = anim["start_scale"]
            # target = center of where the ball sits inside the cup
            tx = target.x
            ty = target.y + target.height - 30
            # linear interp x; parabolic arc on y
            ball.x = sx + (tx - sx) * eased
            base_y = sy + (ty - sy) * eased
            arc = -math.sin(t * math.pi) * anim["arc_height"]
            ball.y = base_y + arc
            ball.scale = ss + (anim["end_scale"] - ss) * eased
            ball.visible = True
            ball.alpha = 1.0
            if t >= 1.0:
                ball.x = tx
                ball.y = ty
                ball.scale = anim["end_scale"]
                ball.visible = False

        if t >= 1.0:
            if anim["type"] == "intro_show" and anim.get("fade_out", 0) > 0:
                anim["ball"].visible = False
                anim["ball"].alpha = 0.0
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
