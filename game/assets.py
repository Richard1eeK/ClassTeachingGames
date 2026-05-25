import os
import sys
from functools import lru_cache

import pygame


_image_cache = {}
_nineslice_cache = {}
_tile_cache = {}


@lru_cache(maxsize=128)
def load_external_image(path, max_size=None):
    """Load and cache an external image file (user-provided images).

    Args:
        path: Absolute path to the image file
        max_size: If provided, scale image to fit within (max_size, max_size) while preserving aspect ratio

    Returns:
        pygame.Surface or None if loading fails
    """
    try:
        img = pygame.image.load(path).convert_alpha()
        if max_size and img:
            w, h = img.get_size()
            if w > max_size or h > max_size:
                scale = min(max_size / w, max_size / h)
                new_w, new_h = int(w * scale), int(h * scale)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
        return img
    except Exception:
        return None


def resource_path(*parts):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, *parts)


def load_image(*parts):
    path = resource_path(*parts)
    if path in _image_cache:
        return _image_cache[path]
    try:
        image = pygame.image.load(path).convert_alpha()
    except Exception:
        image = None
    _image_cache[path] = image
    return image


def pixel_scale(surface, size):
    return pygame.transform.scale(surface, size)


def tile_surface(tile, size):
    key = (id(tile), size)
    if key in _tile_cache:
        return _tile_cache[key]
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)
    tw, th = tile.get_size()
    for y in range(0, h, th):
        for x in range(0, w, tw):
            surf.blit(tile, (x, y))
    _tile_cache[key] = surf
    return surf


def draw_tiled(surface, rect, tile):
    tiled = tile_surface(tile, (rect.width, rect.height))
    surface.blit(tiled, rect.topleft)


def make_nineslice(image, size, border):
    key = (id(image), size, border)
    if key in _nineslice_cache:
        return _nineslice_cache[key]

    w, h = size
    iw, ih = image.get_size()
    b = border
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    pieces = [
        ((0, 0, b, b), (0, 0, b, b)),
        ((b, 0, iw - 2 * b, b), (b, 0, max(0, w - 2 * b), b)),
        ((iw - b, 0, b, b), (w - b, 0, b, b)),
        ((0, b, b, ih - 2 * b), (0, b, b, max(0, h - 2 * b))),
        ((b, b, iw - 2 * b, ih - 2 * b), (b, b, max(0, w - 2 * b), max(0, h - 2 * b))),
        ((iw - b, b, b, ih - 2 * b), (w - b, b, b, max(0, h - 2 * b))),
        ((0, ih - b, b, b), (0, h - b, b, b)),
        ((b, ih - b, iw - 2 * b, b), (b, h - b, max(0, w - 2 * b), b)),
        ((iw - b, ih - b, b, b), (w - b, h - b, b, b)),
    ]

    for src, dst in pieces:
        sx, sy, sw, sh = src
        dx, dy, dw, dh = dst
        if sw <= 0 or sh <= 0 or dw <= 0 or dh <= 0:
            continue
        part = image.subsurface(pygame.Rect(src))
        if (sw, sh) != (dw, dh):
            part = pixel_scale(part, (dw, dh))
        surf.blit(part, (dx, dy))

    _nineslice_cache[key] = surf
    return surf


def draw_nineslice(surface, rect, asset_name, border=8):
    image = load_image("assets", "pixel", asset_name)
    if image is None:
        return False
    surface.blit(make_nineslice(image, rect.size, border), rect.topleft)
    return True
