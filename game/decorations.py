"""Stardew Valley inspired decorative drawing — wood planks, parchment cards, ornaments.

All drawing uses Pygame primitives. Heavy backgrounds are cached to surfaces
so they don't repaint every frame.
"""
import pygame
import math
import random
from game import theme as T
from game.assets import load_image, draw_tiled, draw_nineslice


_bg_cache = {}


def get_wood_background(w, h, seed=42):
    """Cached pixel wood-plank background. Returns a Surface."""
    key = ("wood_bg", w, h, seed)
    if key in _bg_cache:
        return _bg_cache[key]

    surf = pygame.Surface((w, h)).convert()
    tile = load_image("assets", "pixel", "wood_tile.png")
    if tile:
        draw_tiled(surf, pygame.Rect(0, 0, w, h), tile)
    else:
        surf.fill(T.CREAM_BG_DARK)

    rng = random.Random(seed)
    plank_h = 64
    for y in range(0, h, plank_h):
        pygame.draw.line(surf, T.WOOD_DARK, (0, y), (w, y), 3)
        pygame.draw.line(surf, T.WOOD_HIGHLIGHT, (0, y + 3), (w, y + 3), 1)
        for _ in range(4):
            gy = y + rng.randint(10, max(12, plank_h - 10))
            gx = rng.randint(0, max(1, w - 120))
            pygame.draw.line(surf, T.WOOD_DARK, (gx, gy), (min(w, gx + rng.randint(40, 130)), gy), 2)

    vignette = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(0, 44, 4):
        pygame.draw.rect(vignette, (34, 20, 12, 18), (i, i, w - i * 2, h - i * 2), 4)
    surf.blit(vignette, (0, 0))

    _bg_cache[key] = surf
    return surf


def draw_parchment_card(surface, rect, fill=T.PARCHMENT, border_outer=T.WOOD_DARK,
                       border_inner=T.GOLD, radius=T.RADIUS_LG, shadow=True,
                       rivets=True):
    """Draw a pixel parchment panel with a 9-slice wood frame."""
    if shadow:
        pygame.draw.rect(surface, (43, 25, 15), rect.move(6, 7))

    if draw_nineslice(surface, rect, "panel_9slice.png", border=12):
        paper_tile = load_image("assets", "pixel", "parchment_tile.png")
        if paper_tile:
            inner = rect.inflate(-26, -26)
            draw_tiled(surface, inner, paper_tile)
            pygame.draw.rect(surface, T.WOOD_DARK, inner, 2)
        return

    pygame.draw.rect(surface, fill, rect)
    texture_overlay = _get_parchment_texture(rect.width, rect.height, radius)
    surface.blit(texture_overlay, rect.topleft)
    pygame.draw.rect(surface, border_outer, rect, 6)
    inner = rect.inflate(-12, -12)
    pygame.draw.rect(surface, border_inner, inner, 2)


_parchment_texture_cache = {}


def _get_parchment_texture(w, h, radius):
    key = (w, h, radius)
    if key in _parchment_texture_cache:
        return _parchment_texture_cache[key]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(w * 1000 + h)
    # mask for rounded corners
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
    # speckles
    for _ in range(int(w * h / 800)):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        a = rng.randint(8, 22)
        surf.set_at((x, y), (T.PARCHMENT_SHADOW[0], T.PARCHMENT_SHADOW[1], T.PARCHMENT_SHADOW[2], a))
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _parchment_texture_cache[key] = surf
    return surf


def draw_wood_plank(surface, rect, color=T.WOOD_BROWN, dark=T.WOOD_DARK,
                    light=T.WOOD_HIGHLIGHT, radius=T.RADIUS_MD, shadow=True):
    """Pixel wood plank panel — used for HUD bars and signs."""
    if shadow:
        pygame.draw.rect(surface, (43, 25, 15), rect.move(4, 5))

    if draw_nineslice(surface, rect, "wood_sign_9slice.png", border=8):
        return

    pygame.draw.rect(surface, dark, rect)
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surface, color, inner)
    pygame.draw.line(surface, light, (inner.left, inner.top), (inner.right, inner.top), 2)
    pygame.draw.line(surface, dark, (inner.left, inner.bottom), (inner.right, inner.bottom), 2)


def draw_speech_bubble(surface, rect, fill=T.PARCHMENT, border=T.WOOD_DARK,
                      tail="bottom", radius=T.RADIUS_LG):
    """Pixel dialogue box with a small blocky tail."""
    draw_parchment_card(surface, rect, shadow=True, rivets=False)

    cx = rect.centerx
    if tail == "bottom":
        ty = rect.bottom - 2
        tail_pts = [(cx - 14, ty), (cx + 10, ty), (cx - 2, ty + 14)]
        pygame.draw.polygon(surface, border, tail_pts)
        inner = [(cx - 8, ty), (cx + 4, ty), (cx - 2, ty + 7)]
        pygame.draw.polygon(surface, fill, inner)
    elif tail == "top":
        ty = rect.top + 2
        tail_pts = [(cx - 10, ty), (cx + 14, ty), (cx + 2, ty - 14)]
        pygame.draw.polygon(surface, border, tail_pts)
        inner = [(cx - 4, ty), (cx + 8, ty), (cx + 2, ty - 7)]
        pygame.draw.polygon(surface, fill, inner)


def draw_acorn(surface, x, y, size, color=T.WOOD_BROWN):
    """Small acorn ornament."""
    body_r = size
    pygame.draw.ellipse(surface, T.WOOD_LIGHT, (x - body_r, y - body_r // 2, body_r * 2, int(body_r * 1.6)))
    pygame.draw.ellipse(surface, T.WOOD_DARK, (x - body_r, y - body_r // 2, body_r * 2, int(body_r * 1.6)), 2)
    cap_rect = pygame.Rect(x - body_r - 2, y - body_r - 2, body_r * 2 + 4, body_r)
    pygame.draw.ellipse(surface, color, cap_rect)
    pygame.draw.ellipse(surface, T.WOOD_DARK, cap_rect, 2)
    # stem
    pygame.draw.line(surface, T.WOOD_DARK, (x, y - body_r - 2), (x, y - body_r - 6), 2)


def draw_clover(surface, x, y, size, color=T.SV_GREEN):
    """Four-leaf clover."""
    r = size // 2
    for dx, dy in [(-r, -r), (r, -r), (-r, r), (r, r)]:
        pygame.draw.circle(surface, color, (x + dx, y + dy), r)
        pygame.draw.circle(surface, T.SV_GREEN_DARK, (x + dx, y + dy), r, 1)
    pygame.draw.circle(surface, T.GOLD, (x, y), max(2, size // 6))


def draw_wheat(surface, x, y, size, color=T.GOLD_DARK):
    """Wheat sprig."""
    pygame.draw.line(surface, T.WOOD_BROWN, (x, y + size), (x, y - size), 2)
    for i in range(4):
        offset_y = -size + i * (size // 2)
        pygame.draw.ellipse(surface, color, (x - size // 2, y + offset_y - 3, size, 8))
        pygame.draw.ellipse(surface, T.WOOD_DARK, (x - size // 2, y + offset_y - 3, size, 8), 1)


def draw_floating_decorations(surface, decorations, w, h):
    """Render a list of floating decoration dicts.
    Each decoration: {kind, x, y, size, phase, speed}
    """
    for d in decorations:
        ox = math.sin(d["phase"]) * 6
        oy = math.cos(d["phase"] * 0.7) * 4
        x = int(d["x"] + ox)
        y = int(d["y"] + oy)
        kind = d["kind"]
        if kind == "acorn":
            draw_acorn(surface, x, y, d["size"])
        elif kind == "clover":
            draw_clover(surface, x, y, d["size"])
        elif kind == "wheat":
            draw_wheat(surface, x, y, d["size"])


def make_floating_decorations(count, w, h, seed=7):
    """Build a deterministic decoration list scattered in the corners/edges."""
    rng = random.Random(seed)
    decos = []
    kinds = ["acorn", "clover", "wheat"]
    edge_zones = [
        (20, 20, 180, 180),                 # top-left
        (w - 200, 20, w - 20, 180),         # top-right
        (20, h - 200, 180, h - 20),         # bottom-left
        (w - 200, h - 200, w - 20, h - 20), # bottom-right
    ]
    per_zone = max(1, count // 4)
    for zx1, zy1, zx2, zy2 in edge_zones:
        for _ in range(per_zone):
            decos.append({
                "kind": rng.choice(kinds),
                "x": rng.randint(zx1, zx2),
                "y": rng.randint(zy1, zy2),
                "size": rng.randint(10, 18),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.0008, 0.0015),
            })
    return decos


def update_floating_decorations(decorations, dt):
    for d in decorations:
        d["phase"] += d["speed"] * dt
