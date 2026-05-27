import pygame
import os
from typing import List, Dict, Any, Tuple, Optional
from game import theme as T
from game.ui_components import render_text_outlined
from game.icons import draw_image_icon, draw_text_icon, draw_trash


class ItemList:
    ITEM_ROW_HEIGHT = 38

    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        self.items: List[Dict[str, Any]] = items if items is not None else []
        self.scroll_offset: int = 0
        self._delete_btn_rects: List[Tuple[pygame.Rect, int]] = []

    def add_item(self, item: Dict[str, Any]) -> None:
        self.items.append(item)

    def remove_item(self, index: int) -> None:
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def extend_items(self, items: List[Dict[str, Any]]) -> None:
        self.items.extend(items)

    def handle_scroll(self, event: pygame.event.Event, list_height: int) -> None:
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, self.scroll_offset - event.y * 30)
            max_scroll = max(0, len(self.items) * self.ITEM_ROW_HEIGHT - list_height)
            self.scroll_offset = min(self.scroll_offset, max_scroll)

    def handle_delete_click(self, pos: Tuple[int, int]) -> bool:
        for del_rect, idx in self._delete_btn_rects:
            if del_rect.collidepoint(pos):
                self.remove_item(idx)
                return True
        return False

    def draw(self, screen: pygame.Surface, list_rect: pygame.Rect) -> None:
        self._delete_btn_rects = []
        list_top = list_rect.y
        list_bottom = list_rect.bottom
        list_left = list_rect.x
        list_right = list_rect.right

        # clipping region
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
                row_rect = pygame.Rect(list_left, row_y, list_right - list_left, item_h - 5)
                pygame.draw.rect(screen, T.WOOD_DARK, row_rect)
                pygame.draw.rect(screen, T.PARCHMENT_DARK, row_rect.inflate(-4, -4))

                # type icon
                icon_x = row_rect.x + 22
                icon_y = row_rect.centery
                if item["type"] == "image":
                    draw_image_icon(screen, icon_x, icon_y, 11)
                else:
                    draw_text_icon(screen, icon_x, icon_y, 11)

                # content text
                if item["type"] == "image":
                    display = os.path.basename(item["content"])
                else:
                    display = str(item["content"])
                if len(display) > 22:
                    display = display[:21] + "…"
                txt = render_text_outlined(
                    f"{i + 1}. {display}", T.FONT_CAPTION, T.TEXT_DARK,
                    outline_color=T.WOOD_DARK, outline_w=2, bold=True,
                )
                screen.blit(txt, (icon_x + 22, row_rect.centery - txt.get_height() // 2))

                # delete button
                del_x = row_rect.right - 24
                del_y = row_rect.centery
                del_rect = pygame.Rect(del_x - 14, del_y - 12, 28, 24)
                pygame.draw.rect(screen, T.WOOD_DARK, del_rect)
                pygame.draw.rect(screen, T.SV_RED, del_rect.inflate(-4, -4))
                draw_trash(screen, del_x, del_y, 8)
                self._delete_btn_rects.append((del_rect, i))

        screen.set_clip(prev_clip)

        # scroll hint
        if len(self.items) * item_h > (list_bottom - list_top):
            count_text = render_text_outlined(
                f"{len(self.items)} items (scroll to see more)",
                T.FONT_CAPTION, T.TEXT_MUTED,
                outline_color=T.PARCHMENT, outline_w=1, bold=False,
            )
            screen.blit(
                count_text,
                (list_left + 4, list_bottom - count_text.get_height() - 2),
            )
