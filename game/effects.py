"""Particle effects, screen flashes, floating text."""
import pygame
import random
import math
from game import theme as T
from game.icons import draw_star, draw_heart, draw_sparkle
from game.ui_components import get_font


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "kind", "rot", "rot_speed")

    def __init__(self, x, y, vx, vy, life, size, color, kind="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.kind = kind
        self.rot = random.uniform(0, math.tau)
        self.rot_speed = random.uniform(-0.005, 0.005)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.0009 * dt  # gravity
        self.vx *= 0.995
        self.life -= dt
        self.rot += self.rot_speed * dt

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = max(0.0, self.life / self.max_life)
        size = max(2, int(self.size * (0.4 + alpha * 0.6)))
        color = self.color
        if self.kind == "circle":
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, int(255 * alpha)), (size, size), size)
            surface.blit(s, (int(self.x) - size, int(self.y) - size))
        elif self.kind == "star":
            # alpha-aware draw via temp surface
            s = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            draw_star(s, size * 2, size * 2, size, color, filled=True, outline=color)
            s.set_alpha(int(255 * alpha))
            surface.blit(s, (int(self.x) - size * 2, int(self.y) - size * 2))
        elif self.kind == "heart":
            s = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            draw_heart(s, size * 2, size * 2, size, color, outline=color)
            s.set_alpha(int(255 * alpha))
            surface.blit(s, (int(self.x) - size * 2, int(self.y) - size * 2))


class FloatingText:
    """Text that drifts upward and fades — for '+1' style feedback."""

    def __init__(self, x, y, text, color=T.GOLD_DARK, size=T.FONT_HEADING,
                 life=1100, vy=-0.18):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.vy = vy

    def update(self, dt):
        self.y += self.vy * dt
        self.vy *= 0.985
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        from game.ui_components import render_text_outlined
        alpha = max(0.0, self.life / self.max_life)
        surf = render_text_outlined(self.text, self.size, self.color,
                                    outline_color=T.WOOD_DARK, outline_w=2, bold=True)
        surf.set_alpha(int(255 * alpha))
        surface.blit(surf, (int(self.x) - surf.get_width() // 2,
                            int(self.y) - surf.get_height() // 2))


class EffectsManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.shake_amount = 0
        self.shake_decay = 0
        self.flash_alpha = 0
        self.flash_color = (255, 255, 255)

    def burst_correct(self, x, y):
        """Gold/star/heart celebration burst — for correct answer."""
        for _ in range(18):
            angle = random.uniform(-math.pi, 0)  # mostly upward
            speed = random.uniform(0.18, 0.45)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([T.GOLD, T.GOLD_LIGHT, T.SV_GREEN, T.SV_BLUE])
            kind = random.choice(["star", "heart", "circle"])
            size = random.randint(6, 12)
            life = random.randint(700, 1300)
            self.particles.append(Particle(x, y, vx, vy, life, size, color, kind))
        # bigger sparkle
        for _ in range(6):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(0.05, 0.15)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 0.1
            self.particles.append(Particle(x, y, vx, vy, 1500, 14, T.GOLD_LIGHT, "star"))

    def burst_wrong(self, x, y):
        """Soft red dust — for wrong answer (not too harsh)."""
        for _ in range(12):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(0.08, 0.22)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([T.SV_RED, T.SV_RED_DARK, (220, 140, 130)])
            size = random.randint(4, 8)
            life = random.randint(500, 900)
            self.particles.append(Particle(x, y, vx, vy, life, size, color, "circle"))

    def burst_stars(self, x, y, count=8, color=T.GOLD):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(0.1, 0.3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, 1100,
                                           random.randint(8, 14), color, "star"))

    def add_text(self, x, y, text, color=T.GOLD_DARK, size=T.FONT_HEADING):
        self.floating_texts.append(FloatingText(x, y, text, color, size))

    def add_shake(self, amount=10, duration=300):
        self.shake_amount = amount
        self.shake_decay = duration

    def add_flash(self, color=(255, 255, 255), alpha=140):
        self.flash_color = color
        self.flash_alpha = alpha

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]
        if self.shake_decay > 0:
            self.shake_decay -= dt
            if self.shake_decay <= 0:
                self.shake_amount = 0
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - dt * 0.4)

    def get_shake_offset(self):
        if self.shake_amount <= 0:
            return (0, 0)
        return (random.randint(-self.shake_amount, self.shake_amount),
                random.randint(-self.shake_amount // 2, self.shake_amount // 2))

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface)
        if self.flash_alpha > 0:
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash.fill((*self.flash_color, int(self.flash_alpha)))
            surface.blit(flash, (0, 0))
