import pygame
from typing import Tuple, Optional, Callable

from game import theme as T
from game.theme import SCREEN_W, SCREEN_H


class ScaledWindow:
    def __init__(self, width: int = SCREEN_W, height: int = SCREEN_H) -> None:
        self.logical_size: Tuple[int, int] = (width, height)
        self.window: pygame.Surface = pygame.display.set_mode(self.logical_size, pygame.RESIZABLE)
        self.surface: pygame.Surface = pygame.Surface(self.logical_size).convert()
        self.scale: float = 1.0
        self.offset: Tuple[int, int] = (0, 0)
        self.scaled_size: Tuple[int, int] = self.logical_size
        self._scaled_surface: Optional[pygame.Surface] = None
        # Callback fired during VIDEORESIZE so callers can repaint immediately
        # (window dragging on macOS/Windows blocks the event loop until released).
        self.on_resize: Optional[Callable[[], None]] = None
        self._update_viewport()

    def event_to_logical(self, event: pygame.event.Event) -> pygame.event.Event:
        if event.type == pygame.VIDEORESIZE:
            size = getattr(event, "size", (getattr(event, "w", 1), getattr(event, "h", 1)))
            self.window = pygame.display.set_mode((max(1, size[0]), max(1, size[1])), pygame.RESIZABLE)
            self._scaled_surface = None
            self._update_viewport()
            # Trigger an immediate repaint so the window doesn't appear frozen
            # while the user is still dragging the resize handle.
            if self.on_resize is not None:
                try:
                    self.on_resize()
                except Exception:
                    pass

        if hasattr(event, "pos"):
            data = event.dict.copy()
            data["pos"] = self.to_logical_pos(event.pos)
            return pygame.event.Event(event.type, data)

        finger_events = (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION)
        if event.type in finger_events and hasattr(event, "x") and hasattr(event, "y"):
            win_w, win_h = self.window.get_size()
            data = event.dict.copy()
            data["pos"] = self.to_logical_pos((int(event.x * win_w), int(event.y * win_h)))
            return pygame.event.Event(event.type, data)

        return event

    def get_mouse_pos(self) -> Tuple[int, int]:
        return self.to_logical_pos(pygame.mouse.get_pos())

    def present(self) -> None:
        self._update_viewport()
        win_size = self.window.get_size()
        if win_size == self.logical_size:
            self.window.blit(self.surface, (0, 0))
        else:
            self.window.fill(T.WOOD_DARK)
            if self.scaled_size == self.logical_size:
                self.window.blit(self.surface, self.offset)
            else:
                if self._scaled_surface is None or self._scaled_surface.get_size() != self.scaled_size:
                    self._scaled_surface = pygame.Surface(self.scaled_size).convert()
                # smoothscale gives crisp anti-aliased output when shrinking;
                # plain scale (nearest-neighbour) makes everything look blurry/blocky.
                pygame.transform.smoothscale(self.surface, self.scaled_size, self._scaled_surface)
                self.window.blit(self._scaled_surface, self.offset)
        pygame.display.flip()

    def to_logical_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        self._update_viewport()
        x = (pos[0] - self.offset[0]) * self.logical_size[0] / max(1, self.scaled_size[0])
        y = (pos[1] - self.offset[1]) * self.logical_size[1] / max(1, self.scaled_size[1])
        return int(x), int(y)

    def _update_viewport(self) -> None:
        win_w, win_h = self.window.get_size()
        logical_w, logical_h = self.logical_size
        scale = min(max(1, win_w) / logical_w, max(1, win_h) / logical_h)
        self.scale = max(0.001, scale)
        scaled_w = max(1, int(logical_w * self.scale))
        scaled_h = max(1, int(logical_h * self.scale))
        self.scaled_size = (scaled_w, scaled_h)
        self.offset = ((win_w - scaled_w) // 2, (win_h - scaled_h) // 2)
