"""Hand-drawn Pygame icons — no font or image dependencies."""
import pygame
import math


def draw_star(surface, center_x, center_y, size, color, filled=True, outline=(0, 0, 0)):
    """Five-pointed star."""
    points = []
    for i in range(10):
        r = size if i % 2 == 0 else size * 0.4
        angle = math.pi / 2 + i * math.pi / 5
        points.append((center_x + r * math.cos(angle), center_y - r * math.sin(angle)))
    if filled:
        pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, outline, points, 2)


def draw_check(surface, x, y, size, color):
    """Check mark."""
    w = size
    h = size * 1.3
    points = [(x - w // 2, y), (x - w // 4, y + h // 2), (x + w // 2, y - h // 3)]
    pygame.draw.lines(surface, color, False, points, max(3, size // 6))


def draw_cross(surface, x, y, size, color):
    """Cross."""
    d = size // 2
    lw = max(3, size // 6)
    pygame.draw.line(surface, color, (x - d, y - d), (x + d, y + d), lw)
    pygame.draw.line(surface, color, (x + d, y - d), (x - d, y + d), lw)


def draw_eye(surface, x, y, size, color):
    """Eye icon."""
    r = size // 2
    pygame.draw.ellipse(surface, (255, 255, 255), (x - r, y - r, size, size))
    pygame.draw.ellipse(surface, color, (x - r, y - r, size, size), 2)
    pygame.draw.circle(surface, color, (x, y), max(2, r // 3))


def draw_arrow_up(surface, x, y, size, color):
    """Up arrow."""
    points = [(x, y - size), (x - size, y + size // 2), (x + size, y + size // 2)]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 2)


def draw_sparkle(surface, x, y, size, color):
    """Sparkle star."""
    draw_star(surface, x, y, size, color, filled=True)


def draw_heart(surface, x, y, size, color, outline=(75, 55, 40)):
    """Heart icon."""
    r = size // 2
    pygame.draw.circle(surface, color, (x - r // 2, y - r // 4), r)
    pygame.draw.circle(surface, color, (x + r // 2, y - r // 4), r)
    pts = [
        (x - size, y - r // 4),
        (x + size, y - r // 4),
        (x, y + size),
    ]
    pygame.draw.polygon(surface, color, pts)
    # outline approximation
    pygame.draw.circle(surface, outline, (x - r // 2, y - r // 4), r, 2)
    pygame.draw.circle(surface, outline, (x + r // 2, y - r // 4), r, 2)
    pygame.draw.line(surface, outline, (x - size + 1, y - r // 4 + 1), (x, y + size - 1), 2)
    pygame.draw.line(surface, outline, (x + size - 1, y - r // 4 + 1), (x, y + size - 1), 2)


def draw_snail(surface, x, y, size, color=(130, 90, 60), shell_color=(200, 155, 50)):
    """Snail — speed 1 (slow)."""
    body_w = size * 2
    body_h = size
    pygame.draw.ellipse(surface, color, (x - body_w // 2, y, body_w, body_h))
    pygame.draw.ellipse(surface, (75, 55, 40), (x - body_w // 2, y, body_w, body_h), 2)
    # shell
    pygame.draw.circle(surface, shell_color, (x, y - 2), size)
    pygame.draw.circle(surface, (75, 55, 40), (x, y - 2), size, 2)
    pygame.draw.circle(surface, (75, 55, 40), (x, y - 2), size // 2, 2)
    # antennae
    pygame.draw.line(surface, (75, 55, 40), (x - body_w // 2 + 4, y + 2), (x - body_w // 2, y - 6), 2)
    pygame.draw.circle(surface, (75, 55, 40), (x - body_w // 2, y - 6), 2)


def draw_rabbit(surface, x, y, size, color=(220, 215, 200)):
    """Rabbit — speed 2."""
    outline = (75, 55, 40)
    # body
    pygame.draw.ellipse(surface, color, (x - size, y - size // 2, size * 2, size + 4))
    pygame.draw.ellipse(surface, outline, (x - size, y - size // 2, size * 2, size + 4), 2)
    # head
    pygame.draw.circle(surface, color, (x + size // 2, y - size // 2), size // 2 + 2)
    pygame.draw.circle(surface, outline, (x + size // 2, y - size // 2), size // 2 + 2, 2)
    # ears
    for ex_off in (-2, 6):
        ear = pygame.Rect(x + size // 2 + ex_off - 3, y - size - 4, 6, size)
        pygame.draw.ellipse(surface, color, ear)
        pygame.draw.ellipse(surface, outline, ear, 2)
    # eye
    pygame.draw.circle(surface, outline, (x + size, y - size // 2 - 1), 1)
    # tail
    pygame.draw.circle(surface, color, (x - size, y), 4)
    pygame.draw.circle(surface, outline, (x - size, y), 4, 1)


def draw_lightning(surface, x, y, size, color=(245, 200, 80)):
    """Lightning bolt — speed 3 (fast)."""
    outline = (75, 55, 40)
    pts = [
        (x - size // 4, y - size),
        (x + size // 2, y - size // 4),
        (x, y - size // 4),
        (x + size // 4, y + size),
        (x - size // 2, y + size // 4),
        (x, y + size // 4),
    ]
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.polygon(surface, outline, pts, 2)


def draw_flame(surface, x, y, size, color=(235, 100, 50), inner=(245, 200, 80)):
    """Flame — speed 4 (ultra fast)."""
    outline = (75, 55, 40)
    outer_pts = [
        (x, y - size),
        (x + size // 2, y - size // 4),
        (x + size, y + size // 2),
        (x + size // 2, y + size),
        (x - size // 2, y + size),
        (x - size, y + size // 2),
        (x - size // 2, y - size // 4),
    ]
    pygame.draw.polygon(surface, color, outer_pts)
    pygame.draw.polygon(surface, outline, outer_pts, 2)
    inner_pts = [
        (x, y - size // 2),
        (x + size // 3, y),
        (x + size // 4, y + size // 2),
        (x - size // 4, y + size // 2),
        (x - size // 3, y),
    ]
    pygame.draw.polygon(surface, inner, inner_pts)


def draw_tornado(surface, x, y, size, color=(165, 130, 195)):
    """Tornado — speed 5 (insane)."""
    outline = (75, 55, 40)
    layers = [
        (size, size // 2),
        (size // 2 + 4, size // 4 + 2),
        (size // 3 + 2, size // 6 + 1),
    ]
    cy = y - size + 4
    for w, h in layers:
        pygame.draw.ellipse(surface, color, (x - w, cy, w * 2, h * 2))
        pygame.draw.ellipse(surface, outline, (x - w, cy, w * 2, h * 2), 2)
        cy += h * 2 + 2
    # base swirl line
    pygame.draw.line(surface, outline, (x - size // 6, cy + 4), (x + size // 6, cy + 8), 2)


def draw_replay(surface, x, y, size, color=(75, 55, 40)):
    """Circular replay arrow."""
    rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
    pygame.draw.arc(surface, color, rect, math.radians(40), math.radians(320), max(3, size // 5))
    # arrowhead at start
    ax = x + int(size * math.cos(math.radians(-40)))
    ay = y - int(size * math.sin(math.radians(-40)))
    head = [
        (ax, ay),
        (ax - 6, ay - 8),
        (ax + 6, ay - 4),
    ]
    pygame.draw.polygon(surface, color, head)


def draw_door(surface, x, y, size, color=(130, 90, 60)):
    """Door icon."""
    outline = (75, 55, 40)
    rect = pygame.Rect(x - size // 2, y - size, size, size * 2)
    pygame.draw.rect(surface, color, rect, border_radius=size // 3)
    pygame.draw.rect(surface, outline, rect, 2, border_radius=size // 3)
    pygame.draw.circle(surface, (245, 200, 80), (x + size // 4, y), 3)


def draw_trash(surface, x, y, size, color=(170, 70, 60)):
    """Small trash can icon — for delete buttons."""
    outline = (75, 55, 40)
    lid = pygame.Rect(x - size, y - size, size * 2, size // 2)
    body = pygame.Rect(x - size + 2, y - size // 2, size * 2 - 4, size + size // 2)
    pygame.draw.rect(surface, color, body, border_radius=4)
    pygame.draw.rect(surface, outline, body, 2, border_radius=4)
    pygame.draw.rect(surface, color, lid, border_radius=4)
    pygame.draw.rect(surface, outline, lid, 2, border_radius=4)
    # vertical lines
    for off in (-size // 3, 0, size // 3):
        pygame.draw.line(surface, outline, (x + off, y - size // 4), (x + off, y + size - 2), 1)


def draw_image_icon(surface, x, y, size, color=(85, 160, 200)):
    """Small picture icon — to mark image-type entries."""
    outline = (75, 55, 40)
    rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
    pygame.draw.rect(surface, (255, 248, 230), rect, border_radius=4)
    pygame.draw.rect(surface, outline, rect, 2, border_radius=4)
    # mountain
    pts = [(x - size + 4, y + size - 4), (x - 2, y), (x + 2, y + size // 3),
           (x + size // 2, y - size // 3), (x + size - 4, y + size - 4)]
    pygame.draw.polygon(surface, color, pts)
    # sun
    pygame.draw.circle(surface, (245, 200, 80), (x + size // 2, y - size // 2), 3)


def draw_text_icon(surface, x, y, size, color=(75, 55, 40)):
    """Small 'A' icon — to mark text-type entries."""
    rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
    pygame.draw.rect(surface, (255, 248, 230), rect, border_radius=4)
    pygame.draw.rect(surface, color, rect, 2, border_radius=4)
    # 'A' shape
    pts = [(x - size // 2, y + size // 2), (x, y - size // 2), (x + size // 2, y + size // 2)]
    pygame.draw.lines(surface, color, False, pts, 2)
    pygame.draw.line(surface, color, (x - size // 4, y + 2), (x + size // 4, y + 2), 2)


def draw_plus(surface, x, y, size, color=(135, 180, 90)):
    """Plus icon."""
    lw = max(3, size // 4)
    pygame.draw.line(surface, color, (x, y - size), (x, y + size), lw)
    pygame.draw.line(surface, color, (x - size, y), (x + size, y), lw)


def draw_info(surface, x, y, size, color=(75, 55, 40)):
    """Information icon."""
    outline = (75, 55, 40)
    pygame.draw.circle(surface, (255, 248, 230), (x, y), size)
    pygame.draw.circle(surface, outline, (x, y), size, 2)
    pygame.draw.circle(surface, color, (x, y - size // 2), max(2, size // 7))
    pygame.draw.line(surface, color, (x, y - size // 5), (x, y + size // 2), max(3, size // 5))
    pygame.draw.line(surface, color, (x - size // 4, y + size // 2), (x + size // 4, y + size // 2), max(2, size // 7))


def draw_gear(surface, x, y, size, color=(75, 55, 40)):
    """Gear / settings icon — for Adjust button."""
    teeth = 8
    outer = size
    inner = int(size * 0.6)
    pts = []
    for i in range(teeth * 2):
        r = outer if i % 2 == 0 else inner
        angle = i * math.pi / teeth - math.pi / 2
        pts.append((x + r * math.cos(angle), y + r * math.sin(angle)))
    pygame.draw.polygon(surface, color, pts)
    # center hole
    hole_r = max(3, size // 3)
    pygame.draw.circle(surface, (255, 248, 230), (x, y), hole_r)
    pygame.draw.circle(surface, color, (x, y), hole_r, 2)
