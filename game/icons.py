"""Pygame 手绘图标 — 不依赖字体和图片，跨平台零问题"""
import pygame
import math


def draw_star(surface, center_x, center_y, size, color, filled=True):
    """五角星"""
    points = []
    for i in range(10):
        r = size if i % 2 == 0 else size * 0.4
        angle = math.pi / 2 + i * math.pi / 5
        points.append((center_x + r * math.cos(angle), center_y - r * math.sin(angle)))
    if filled:
        pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 2)


def draw_check(surface, x, y, size, color):
    """对勾"""
    w = size
    h = size * 1.3
    points = [(x - w // 2, y), (x - w // 4, y + h // 2), (x + w // 2, y - h // 3)]
    pygame.draw.lines(surface, color, False, points, max(3, size // 6))


def draw_cross(surface, x, y, size, color):
    """叉号"""
    d = size // 2
    lw = max(3, size // 6)
    pygame.draw.line(surface, color, (x - d, y - d), (x + d, y + d), lw)
    pygame.draw.line(surface, color, (x + d, y - d), (x - d, y + d), lw)


def draw_eye(surface, x, y, size, color):
    """眼睛"""
    r = size // 2
    pygame.draw.ellipse(surface, (255, 255, 255), (x - r, y - r, size, size))
    pygame.draw.ellipse(surface, color, (x - r, y - r, size, size), 2)
    pygame.draw.circle(surface, color, (x, y), max(2, r // 3))


def draw_arrow_up(surface, x, y, size, color):
    """上箭头"""
    points = [(x, y - size), (x - size, y + size // 2), (x + size, y + size // 2)]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 2)


def draw_sparkle(surface, x, y, size, color):
    """小闪光/星星"""
    draw_star(surface, x, y, size, color, filled=True)
