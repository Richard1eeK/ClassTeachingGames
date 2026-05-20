"""Stardew Valley inspired decorative drawing — wood planks, parchment cards, ornaments.

All drawing uses Pygame primitives. Heavy backgrounds are cached to surfaces
so they don't repaint every frame.
"""
import pygame
import math
import random
from game import theme as T


_bg_cache = {}


def get_wood_background(w, h, seed=42):
    """Cached cream wood-plank background. Returns a Surface."""
    key = ("wood_bg", w, h, seed)
    if key in _bg_cache:
        return _bg_cache[key]

    surf = pygame.Surface((w, h)).convert()
    surf.fill(T.CREAM_BG)

    rng = random.Random(seed)

    # subtle horizontal wood-grain bands
    plank_h = 90
    y = 0
    band_idx = 0
    while y < h:
        shade = T.CREAM_BG if band_idx % 2 == 0 else T.CREAM_BG_DARK
        pygame.draw.rect(surf, shade, (0, y, w, plank_h))
        # plank divider line (very faint)
        pygame.draw.line(surf, T.PARCHMENT_SHADOW, (0, y), (w, y), 1)
        # grain lines
        for _ in range(3):
            gy = y + rng.randint(8, plank_h - 8)
            gx_start = rng.randint(0, w // 4)
            gx_end = w - rng.randint(0, w // 4)
            grain_color = (T.CREAM_BG_DARK[0] - 8, T.CREAM_BG_DARK[1] - 8, T.CREAM_BG_DARK[2] - 8)
            pygame.draw.line(surf, grain_color, (gx_start, gy), (gx_end, gy), 1)
        # occasional wood knot
        if rng.random() < 0.35:
            kx = rng.randint(80, w - 80)
            ky = y + rng.randint(20, plank_h - 20)
            kr = rng.randint(6, 12)
            pygame.draw.ellipse(surf, T.WOOD_LIGHT, (kx - kr, ky - kr // 2, kr * 2, kr))
            pygame.draw.ellipse(surf, T.WOOD_BROWN, (kx - kr + 2, ky - kr // 2 + 1, kr * 2 - 4, kr - 2), 1)
        y += plank_h
        band_idx += 1

    # vignette: very subtle dark corners
    vignette = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(40):
        alpha = int(40 * (i / 40))
        pygame.draw.rect(
            vignette,
            (60, 40, 20, max(0, 25 - alpha)),
            (i, i, w - i * 2, h - i * 2),
            1,
        )
    surf.blit(vignette, (0, 0))

    _bg_cache[key] = surf
    return surf


def draw_parchment_card(surface, rect, fill=T.PARCHMENT, border_outer=T.WOOD_DARK,
                       border_inner=T.GOLD, radius=T.RADIUS_LG, shadow=True,
                       rivets=True):
    """Draw a parchment card with double border (outer wood, inner gold) and corner rivets."""
    if shadow:
        shadow_rect = rect.move(0, 5)
        shadow_surf = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
        for i in range(6):
            alpha = 18 - i * 2
            pygame.draw.rect(
                shadow_surf,
                (40, 25, 15, max(0, alpha)),
                (6 - i, 6 - i, rect.width + i * 2, rect.height + i * 2),
                border_radius=radius + i,
            )
        surface.blit(shadow_surf, (rect.x - 6, rect.y - 1))

    # main fill
    pygame.draw.rect(surface, fill, rect, border_radius=radius)

    # paper texture: random faint dots
    # (skip per-frame randomness — would flicker; use deterministic pattern)
    texture_overlay = _get_parchment_texture(rect.width, rect.height, radius)
    surface.blit(texture_overlay, rect.topleft)

    # outer border (wood)
    pygame.draw.rect(surface, border_outer, rect, 4, border_radius=radius)
    # inner border (gold), inset by 4px
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surface, border_inner, inner, 2, border_radius=max(2, radius - 4))

    if rivets:
        rivet_inset = 14
        rivet_color = T.GOLD_DARK
        rivet_highlight = T.GOLD_LIGHT
        for cx, cy in [
            (rect.left + rivet_inset, rect.top + rivet_inset),
            (rect.right - rivet_inset, rect.top + rivet_inset),
            (rect.left + rivet_inset, rect.bottom - rivet_inset),
            (rect.right - rivet_inset, rect.bottom - rivet_inset),
        ]:
            pygame.draw.circle(surface, T.WOOD_DARK, (cx, cy), 5)
            pygame.draw.circle(surface, rivet_color, (cx, cy), 4)
            pygame.draw.circle(surface, rivet_highlight, (cx - 1, cy - 1), 1)


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
    """Wood plank panel — used for HUD bars, buttons backgrounds."""
    if shadow:
        shadow_rect = rect.move(0, 4)
        shadow_surf = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
        for i in range(4):
            alpha = 22 - i * 4
            pygame.draw.rect(
                shadow_surf,
                (30, 18, 10, max(0, alpha)),
                (4 - i, 4 - i, rect.width + i * 2, rect.height + i * 2),
                border_radius=radius + i,
            )
        surface.blit(shadow_surf, (rect.x - 4, rect.y))

    pygame.draw.rect(surface, color, rect, border_radius=radius)
    # top highlight
    highlight_rect = pygame.Rect(rect.x + 4, rect.y + 3, rect.width - 8, max(2, rect.height // 5))
    pygame.draw.rect(surface, light, highlight_rect, border_radius=max(2, radius - 4))
    # bottom shadow
    bottom_rect = pygame.Rect(rect.x + 4, rect.bottom - rect.height // 4, rect.width - 8, rect.height // 5)
    pygame.draw.rect(surface, dark, bottom_rect, border_radius=max(2, radius - 4))
    # outline
    pygame.draw.rect(surface, dark, rect, 2, border_radius=radius)


def draw_speech_bubble(surface, rect, fill=T.PARCHMENT, border=T.WOOD_DARK,
                      tail="bottom", radius=T.RADIUS_LG):
    """Rounded bubble with a small tail."""
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 3, border_radius=radius)

    if tail == "bottom":
        cx = rect.centerx
        ty = rect.bottom
        tail_pts = [(cx - 12, ty - 2), (cx + 12, ty - 2), (cx - 4, ty + 14)]
        pygame.draw.polygon(surface, fill, tail_pts)
        pygame.draw.line(surface, border, (cx - 12, ty - 1), (cx - 4, ty + 14), 3)
        pygame.draw.line(surface, border, (cx + 12, ty - 1), (cx - 4, ty + 14), 3)
    elif tail == "top":
        cx = rect.centerx
        ty = rect.top
        tail_pts = [(cx - 12, ty + 2), (cx + 12, ty + 2), (cx + 4, ty - 14)]
        pygame.draw.polygon(surface, fill, tail_pts)
        pygame.draw.line(surface, border, (cx - 12, ty + 1), (cx + 4, ty - 14), 3)
        pygame.draw.line(surface, border, (cx + 12, ty + 1), (cx + 4, ty - 14), 3)


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
