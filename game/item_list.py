import pygame
import os
from typing import List, Dict, Any, Tuple, Optional
from game import theme as T
from game.ui_components import render_text_outlined
from game.icons import draw_image_icon, draw_text_icon, draw_trash


class ItemList:
    ITEM_ROW_HEIGHT = 38
    SCROLL_STEP = 30
    SCROLLBAR_W = 16
    SCROLLBAR_TOUCH_W = 34

    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        self.items: List[Dict[str, Any]] = items if items is not None else []
        self.scroll_offset: int = 0
        self._delete_btn_rects: List[Tuple[pygame.Rect, int]] = []
        self._dragging_scrollbar: bool = False
        self._dragging_content: bool = False
        self._drag_start_y: int = 0
        self._drag_start_offset: int = 0
        self._drag_thumb_offset: int = 0
        self._drag_moved: bool = False
        self._pressed_delete_index: Optional[int] = None

    def add_item(self, item: Dict[str, Any]) -> None:
        self.items.append(item)

    def remove_item(self, index: int) -> None:
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def extend_items(self, items: List[Dict[str, Any]]) -> None:
        self.items.extend(items)

    def handle_scroll(self, event: pygame.event.Event, list_height: int) -> None:
        if event.type == pygame.MOUSEWHEEL:
            rect = pygame.Rect(0, 0, 1, list_height)
            self._scroll_by(-event.y * self.SCROLL_STEP, rect)

    def handle_event(self, event: pygame.event.Event, list_rect: pygame.Rect) -> bool:
        pos = self._event_pos(event)

        if event.type == pygame.MOUSEWHEEL:
            return self._scroll_by(-event.y * self.SCROLL_STEP, list_rect)

        if self._is_mouse_wheel_button(event):
            delta = -self.SCROLL_STEP if event.button == 4 else self.SCROLL_STEP
            return self._scroll_by(delta, list_rect)

        if self._is_press(event):
            if pos is None:
                return False
            if self._scrollbar_hit_rect(list_rect).collidepoint(pos):
                if self._can_scroll(list_rect):
                    thumb = self._thumb_rect(list_rect)
                    if thumb.collidepoint(pos):
                        self._drag_thumb_offset = pos[1] - thumb.y
                    else:
                        self._drag_thumb_offset = thumb.height // 2
                        self._set_scroll_from_thumb_top(pos[1] - self._drag_thumb_offset, list_rect)
                    self._dragging_scrollbar = True
                return True
            if list_rect.collidepoint(pos):
                self._dragging_content = True
                self._drag_start_y = pos[1]
                self._drag_start_offset = self.scroll_offset
                self._drag_moved = False
                self._pressed_delete_index = self._delete_index_at(pos)
                return True
            return False

        if self._is_motion(event):
            if pos is None:
                return False
            if self._dragging_scrollbar:
                self._set_scroll_from_thumb_top(pos[1] - self._drag_thumb_offset, list_rect)
                return True
            if self._dragging_content:
                dy = pos[1] - self._drag_start_y
                if abs(dy) > 4:
                    self._drag_moved = True
                self.scroll_offset = self._clamped_offset(self._drag_start_offset - dy, list_rect)
                return True
            return False

        if self._is_release(event):
            if self._dragging_scrollbar:
                self._dragging_scrollbar = False
                return True
            if self._dragging_content:
                was_click = not self._drag_moved
                pressed_delete_index = self._pressed_delete_index
                self._dragging_content = False
                self._pressed_delete_index = None
                if was_click and pos is not None and pressed_delete_index is not None:
                    if self._delete_index_at(pos) == pressed_delete_index:
                        self.remove_item(pressed_delete_index)
                        self.scroll_offset = self._clamped_offset(self.scroll_offset, list_rect)
                return True
            return False

        return False

    def handle_delete_click(self, pos: Tuple[int, int]) -> bool:
        idx = self._delete_index_at(pos)
        if idx is not None:
            self.remove_item(idx)
            return True
        return False

    def draw(self, screen: pygame.Surface, list_rect: pygame.Rect) -> None:
        self.scroll_offset = self._clamped_offset(self.scroll_offset, list_rect)
        self._delete_btn_rects = []
        list_top = list_rect.y
        list_bottom = list_rect.bottom
        list_left = list_rect.x
        list_right = list_rect.right
        content_right = list_right - self.SCROLLBAR_TOUCH_W - 6

        clip_rect = pygame.Rect(list_left, list_top,
                                list_right - list_left, list_bottom - list_top)
        prev_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        item_h = self.ITEM_ROW_HEIGHT
        if not self.items:
            hint = render_text_outlined(
                "Add at least 1 item to start.",
                T.FONT_BODY, T.TEXT_BROWN, outline_color=T.PARCHMENT,
                outline_w=1, bold=True,
            )
            screen.blit(hint, (list_left + 8, list_top + 12))
            sub = render_text_outlined(
                "Each round picks one randomly.",
                T.FONT_CAPTION, T.TEXT_MUTED, outline_color=T.PARCHMENT,
                outline_w=1, bold=False,
            )
            screen.blit(sub, (list_left + 8, list_top + 44))
        else:
            for i, item in enumerate(self.items):
                row_y = list_top + i * item_h - self.scroll_offset
                if row_y + item_h < list_top or row_y > list_bottom:
                    continue
                row_rect = pygame.Rect(list_left, row_y, content_right - list_left, item_h - 5)
                pygame.draw.rect(screen, T.WOOD_DARK, row_rect)
                pygame.draw.rect(screen, T.PARCHMENT_DARK, row_rect.inflate(-4, -4))

                icon_x = row_rect.x + 22
                icon_y = row_rect.centery
                if item["type"] == "image":
                    draw_image_icon(screen, icon_x, icon_y, 11)
                else:
                    draw_text_icon(screen, icon_x, icon_y, 11)

                if item["type"] == "image":
                    display = os.path.basename(item["content"])
                else:
                    display = str(item["content"])
                if len(display) > 20:
                    display = display[:19] + "…"
                txt = render_text_outlined(
                    f"{i + 1}. {display}", T.FONT_BODY, T.TEXT_DARK,
                    outline_color=T.PARCHMENT_DARK, outline_w=1, bold=True,
                )
                screen.blit(txt, (icon_x + 22, row_rect.centery - txt.get_height() // 2))

                del_x = row_rect.right - 24
                del_y = row_rect.centery
                del_rect = pygame.Rect(del_x - 14, del_y - 12, 28, 24)
                pygame.draw.rect(screen, T.WOOD_DARK, del_rect)
                pygame.draw.rect(screen, T.SV_RED, del_rect.inflate(-4, -4))
                draw_trash(screen, del_x, del_y, 8)
                self._delete_btn_rects.append((del_rect, i))

        screen.set_clip(prev_clip)

        self._draw_scrollbar(screen, list_rect)
        count_text = render_text_outlined(
            f"{len(self.items)} items",
            T.FONT_CAPTION, T.TEXT_MUTED,
            outline_color=T.PARCHMENT, outline_w=1, bold=False,
        )
        screen.blit(
            count_text,
            (list_left + 4, list_bottom - count_text.get_height() - 2),
        )

    def _event_pos(self, event: pygame.event.Event) -> Optional[Tuple[int, int]]:
        return getattr(event, "pos", None)

    def _is_press(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            return getattr(event, "button", 1) == 1
        finger_down = getattr(pygame, "FINGERDOWN", None)
        return finger_down is not None and event.type == finger_down

    def _is_release(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONUP:
            return getattr(event, "button", 1) == 1
        finger_up = getattr(pygame, "FINGERUP", None)
        return finger_up is not None and event.type == finger_up

    def _is_motion(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            return True
        finger_motion = getattr(pygame, "FINGERMOTION", None)
        return finger_motion is not None and event.type == finger_motion

    def _is_mouse_wheel_button(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) in (4, 5)

    def _delete_index_at(self, pos: Tuple[int, int]) -> Optional[int]:
        for del_rect, idx in self._delete_btn_rects:
            if del_rect.collidepoint(pos):
                return idx
        return None

    def _content_height(self) -> int:
        return len(self.items) * self.ITEM_ROW_HEIGHT

    def _max_scroll(self, list_rect: pygame.Rect) -> int:
        return max(0, self._content_height() - list_rect.height)

    def _can_scroll(self, list_rect: pygame.Rect) -> bool:
        return self._max_scroll(list_rect) > 0

    def _clamped_offset(self, offset: int, list_rect: pygame.Rect) -> int:
        return max(0, min(self._max_scroll(list_rect), int(offset)))

    def _scroll_by(self, delta: int, list_rect: pygame.Rect) -> bool:
        if not self._can_scroll(list_rect):
            self.scroll_offset = 0
            return False
        self.scroll_offset = self._clamped_offset(self.scroll_offset + delta, list_rect)
        return True

    def _track_rect(self, list_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(list_rect.right - 25, list_rect.y + 4,
                           self.SCROLLBAR_W, max(1, list_rect.height - 8))

    def _scrollbar_hit_rect(self, list_rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(list_rect.right - self.SCROLLBAR_TOUCH_W, list_rect.y,
                           self.SCROLLBAR_TOUCH_W, list_rect.height)

    def _thumb_rect(self, list_rect: pygame.Rect) -> pygame.Rect:
        track = self._track_rect(list_rect)
        max_scroll = self._max_scroll(list_rect)
        if max_scroll <= 0:
            return pygame.Rect(track.x, track.y, track.w, track.h)
        content_h = max(1, self._content_height())
        thumb_h = max(44, int(track.height * list_rect.height / content_h))
        thumb_h = min(track.height, thumb_h)
        travel = max(1, track.height - thumb_h)
        thumb_y = track.y + int(travel * self.scroll_offset / max_scroll)
        return pygame.Rect(track.x, thumb_y, track.w, thumb_h)

    def _set_scroll_from_thumb_top(self, thumb_top: int, list_rect: pygame.Rect) -> None:
        track = self._track_rect(list_rect)
        thumb = self._thumb_rect(list_rect)
        max_scroll = self._max_scroll(list_rect)
        travel = max(1, track.height - thumb.height)
        ratio = (thumb_top - track.y) / travel
        ratio = max(0.0, min(1.0, ratio))
        self.scroll_offset = int(max_scroll * ratio)

    def _draw_scrollbar(self, screen: pygame.Surface, list_rect: pygame.Rect) -> None:
        track = self._track_rect(list_rect)
        thumb = self._thumb_rect(list_rect)
        hit_rect = self._scrollbar_hit_rect(list_rect)
        pygame.draw.rect(screen, T.WOOD_DARK, hit_rect)
        pygame.draw.rect(screen, T.PARCHMENT_SHADOW, hit_rect.inflate(-4, -4))
        pygame.draw.rect(screen, T.WOOD_BROWN, track)
        pygame.draw.rect(screen, T.WOOD_DARK, track, 2)
        thumb_color = T.GOLD if self._can_scroll(list_rect) else T.GOLD_LIGHT
        if self._dragging_scrollbar:
            thumb_color = T.GOLD_DARK
        pygame.draw.rect(screen, T.WOOD_DARK, thumb.inflate(4, 2))
        pygame.draw.rect(screen, thumb_color, thumb)
        pygame.draw.rect(screen, T.GOLD_LIGHT, thumb.inflate(-4, -4))
        grip_y = thumb.centery
        for dy in (-6, 0, 6):
            pygame.draw.line(screen, T.WOOD_DARK,
                             (thumb.x + 4, grip_y + dy),
                             (thumb.right - 5, grip_y + dy), 2)
