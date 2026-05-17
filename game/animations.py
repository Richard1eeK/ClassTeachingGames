import pygame
from game.ui_components import CUP_COLORS, WHITE, BLACK, DARK_GRAY, get_font


def ease_in_out(t):
    return t * t * (3 - 2 * t)


class Cup:
    def __init__(self, x, y, width, height, color_index=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = CUP_COLORS[color_index % len(CUP_COLORS)]
        self.lifted = False
        self.lift_offset = 0
        self.target_x = x
        self.start_x = x
        self.ball_content = None
        self.ball_type = "text"

    def draw(self, surface, show_ball=False):
        cup_y = self.y - self.lift_offset

        if (show_ball or self.lifted) and self.ball_content is not None:
            self._draw_ball(surface)

        body_rect = pygame.Rect(self.x - self.width // 2, cup_y, self.width, self.height)
        top_w = int(self.width * 0.7)
        points = [
            (self.x - self.width // 2, cup_y + self.height),
            (self.x + self.width // 2, cup_y + self.height),
            (self.x + top_w // 2, cup_y),
            (self.x - top_w // 2, cup_y),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, DARK_GRAY, points, 3)

        rim_rect = pygame.Rect(self.x - top_w // 2 - 5, cup_y - 8, top_w + 10, 16)
        pygame.draw.ellipse(surface, self.color, rim_rect)
        pygame.draw.ellipse(surface, DARK_GRAY, rim_rect, 2)

        highlight_points = [
            (self.x - self.width // 4, cup_y + 10),
            (self.x - self.width // 4 + 8, cup_y + 10),
            (self.x - self.width // 4 + 5, cup_y + self.height - 10),
            (self.x - self.width // 4 - 3, cup_y + self.height - 10),
        ]
        highlight_color = tuple(min(c + 60, 255) for c in self.color)
        pygame.draw.polygon(surface, highlight_color, highlight_points)

    def _draw_ball(self, surface):
        cup_y = self.y - self.lift_offset
        ball_y = cup_y + self.height - 30
        ball_radius = min(self.width // 3, 35)
        pygame.draw.circle(surface, WHITE, (self.x, ball_y), ball_radius)
        pygame.draw.circle(surface, DARK_GRAY, (self.x, ball_y), ball_radius, 2)

        if self.ball_content:
            if self.ball_type == "text":
                font_size = max(16, min(28, ball_radius))
                font = get_font(font_size)
                text_surf = font.render(str(self.ball_content), True, BLACK)
                text_rect = text_surf.get_rect(center=(self.x, ball_y))
                if text_rect.width > ball_radius * 1.8:
                    font_size = max(12, font_size - 6)
                    font = get_font(font_size)
                    text_surf = font.render(str(self.ball_content), True, BLACK)
                    text_rect = text_surf.get_rect(center=(self.x, ball_y))
                surface.blit(text_surf, text_rect)
            elif self.ball_type == "image" and isinstance(self.ball_content, pygame.Surface):
                img = self.ball_content
                max_size = int(ball_radius * 1.5)
                img_w, img_h = img.get_size()
                scale = min(max_size / img_w, max_size / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                scaled = pygame.transform.smoothscale(img, (new_w, new_h))
                img_rect = scaled.get_rect(center=(self.x, ball_y))
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

    def add_pause(self, duration_ms):
        self.animations.append({
            "type": "pause",
            "duration": duration_ms,
            "elapsed": 0,
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

        if t >= 1.0:
            if anim["type"] == "swap":
                cup_a = anim["cup_a"]
                cup_b = anim["cup_b"]
                cup_a.x = anim["start_b"]
                cup_b.x = anim["start_a"]
            self.animations.pop(0)

    @property
    def done(self):
        return len(self.animations) == 0
