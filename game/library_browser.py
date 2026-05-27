"""Built-in material library browser UI for the Settings screen."""
import pygame
from typing import Callable, Dict, List, Optional, Tuple

from game import theme as T
from game.ui_components import Button, render_text_outlined
from game import library


# Layout constants (relative to the rect this browser lives in)
CATEGORY_BTN_HEIGHT = 38
LIST_ROW_HEIGHT = 30
INFO_HEIGHT = 70
USE_BTN_HEIGHT = 44


class LibraryBrowser:
    """Browse the built-in material library.

    Handles its own click events and rendering. Calls `on_use(items)` when
    the user clicks "Use this material" and confirms the overwrite dialog.
    """

    def __init__(self, rect: pygame.Rect, on_use: Callable[[List[Dict]], None]):
        self.rect = rect
        self.on_use = on_use
        self.index: Dict = library.scan_library()

        # Selection state
        self.category: str = "flashcards"  # "flashcards" or "words"
        self.expanded_series: Optional[str] = None
        self.expanded_level: Optional[str] = None
        self.selected: Optional[Tuple[str, str, str, str]] = None  # (cat, series, level, unit)
        self.preview_count: int = 0

        # Scroll for the list
        self.scroll_offset: int = 0

        # Confirmation dialog state
        self.confirm_open: bool = False
        self.pending_items: List[Dict] = []

        # Cached row hit rects: list of (rect, kind, payload)
        # kind in {"series", "level", "unit", "bright_spark_topic"}
        self._row_rects: List[Tuple[pygame.Rect, str, dict]] = []

        # Layout: compute top-level button positions
        self._init_buttons()

    def _init_buttons(self):
        x = self.rect.x
        w = self.rect.width
        # Two category buttons side by side
        cat_y = self.rect.y
        cat_w = (w - 8) // 2
        self.flashcards_btn = Button(
            x, cat_y, cat_w, CATEGORY_BTN_HEIGHT,
            "Flashcards", T.SV_BLUE, T.TEXT_LIGHT, T.FONT_CAPTION,
        )
        self.words_btn = Button(
            x + cat_w + 8, cat_y, cat_w, CATEGORY_BTN_HEIGHT,
            "Words", T.SV_BLUE, T.TEXT_LIGHT, T.FONT_CAPTION,
        )

        # Use this material button at bottom
        use_y = self.rect.bottom - USE_BTN_HEIGHT
        self.use_btn = Button(
            x, use_y, w, USE_BTN_HEIGHT,
            "Use this material", T.SV_GREEN, T.TEXT_LIGHT, T.FONT_BODY,
        )
        self.use_btn.enabled = False

        # Confirmation dialog (drawn over the whole screen, not relative to self.rect)
        from game.theme import SCREEN_W, SCREEN_H
        dlg_w, dlg_h = 460, 200
        dlg_x = (SCREEN_W - dlg_w) // 2
        dlg_y = (SCREEN_H - dlg_h) // 2
        self.confirm_rect = pygame.Rect(dlg_x, dlg_y, dlg_w, dlg_h)
        btn_y = dlg_y + dlg_h - 60
        self.confirm_yes_btn = Button(
            dlg_x + 40, btn_y, 160, 44, "Replace", T.SV_RED, T.TEXT_LIGHT, T.FONT_BODY,
        )
        self.confirm_no_btn = Button(
            dlg_x + dlg_w - 200, btn_y, 160, 44, "Cancel", T.WOOD_BROWN, T.TEXT_LIGHT, T.FONT_BODY,
        )

    @property
    def list_top(self) -> int:
        return self.rect.y + CATEGORY_BTN_HEIGHT + 14

    @property
    def list_bottom(self) -> int:
        # Reserve space for info text + use button at bottom
        return self.rect.bottom - USE_BTN_HEIGHT - INFO_HEIGHT - 8

    def update(self, mouse_pos: Tuple[int, int], dt: int) -> None:
        self.flashcards_btn.update(mouse_pos, dt)
        self.words_btn.update(mouse_pos, dt)
        self.use_btn.update(mouse_pos, dt)
        if self.confirm_open:
            self.confirm_yes_btn.update(mouse_pos, dt)
            self.confirm_no_btn.update(mouse_pos, dt)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True if event was consumed."""
        if self.confirm_open:
            return self._handle_confirm_event(event)

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, self.scroll_offset - event.y * 30)
            self.scroll_offset = min(self.scroll_offset, self._max_scroll())
            return True

        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        pos = event.pos

        # Category buttons
        if self.flashcards_btn.is_clicked(pos, True):
            self._switch_category("flashcards")
            return True
        if self.words_btn.is_clicked(pos, True):
            self._switch_category("words")
            return True

        # Use button
        if self.use_btn.is_clicked(pos, True) and self.use_btn.enabled:
            self._on_use_clicked()
            return True

        # List rows (use cached hit rects)
        # Only consider clicks inside the list visible region
        list_rect = pygame.Rect(self.rect.x, self.list_top,
                                self.rect.width, self.list_bottom - self.list_top)
        if list_rect.collidepoint(pos):
            for row_rect, kind, payload in self._row_rects:
                if row_rect.collidepoint(pos):
                    self._on_row_clicked(kind, payload)
                    return True
            return True  # consumed (clicked in list area but not on a row)

        return False

    def _handle_confirm_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.confirm_open = False
            self.pending_items = []
            return True
        if event.type != pygame.MOUSEBUTTONDOWN:
            return True  # consume all other events while dialog is open
        pos = event.pos
        if self.confirm_yes_btn.is_clicked(pos, True):
            items = self.pending_items
            self.confirm_open = False
            self.pending_items = []
            try:
                self.on_use(items)
            except Exception:
                pass
            return True
        if self.confirm_no_btn.is_clicked(pos, True):
            self.confirm_open = False
            self.pending_items = []
            return True
        return True  # block clicks behind the dialog

    def _switch_category(self, category: str):
        if category not in self.index:
            return
        self.category = category
        self.expanded_series = None
        self.expanded_level = None
        self.selected = None
        self.preview_count = 0
        self.scroll_offset = 0
        self.use_btn.enabled = False

    def _on_row_clicked(self, kind: str, payload: dict):
        if kind == "series":
            series = payload["series"]
            self.expanded_series = None if self.expanded_series == series else series
            self.expanded_level = None
        elif kind == "level":
            level = payload["level"]
            self.expanded_level = None if self.expanded_level == level else level
        elif kind in ("unit", "bright_spark_topic"):
            series = payload["series"]
            level = payload["level"]
            unit = payload["unit"]
            self.selected = (self.category, series, level, unit)
            try:
                items = library.load_unit(self.category, series, level, unit)
            except Exception:
                items = []
            self.preview_count = len(items)
            self.use_btn.enabled = self.preview_count > 0

    def _on_use_clicked(self):
        if not self.selected:
            return
        cat, series, level, unit = self.selected
        try:
            items = library.load_unit(cat, series, level, unit)
        except Exception:
            items = []
        if not items:
            return
        self.pending_items = items
        self.confirm_open = True

    def _max_scroll(self) -> int:
        # Total content height = num visible rows * row height
        rows = self._count_visible_rows()
        content_h = rows * LIST_ROW_HEIGHT
        view_h = self.list_bottom - self.list_top
        return max(0, content_h - view_h)

    def _count_visible_rows(self) -> int:
        if self.category not in self.index:
            return 0
        count = 0
        for series, levels in self.index[self.category].items():
            count += 1  # series row
            if self.expanded_series == series:
                if self._is_bright_spark_series(series):
                    count += len(levels)  # topic rows
                    continue
                for level, units in levels.items():
                    count += 1  # level row
                    if self.expanded_level == level:
                        count += len(units)  # unit rows
        return count

    def draw(self, screen: pygame.Surface):
        # Highlight selected category button
        self.flashcards_btn.color = T.SV_BLUE_DARK if self.category == "flashcards" else T.SV_BLUE
        self.words_btn.color = T.SV_BLUE_DARK if self.category == "words" else T.SV_BLUE
        self.flashcards_btn.draw(screen)
        self.words_btn.draw(screen)

        # Empty library?
        if not self.index:
            self._draw_empty_state(screen)
            self.use_btn.draw(screen)
            return

        if self.category not in self.index:
            self._draw_no_content_for_category(screen)
            self.use_btn.draw(screen)
            return

        # List area with clipping
        list_rect = pygame.Rect(self.rect.x, self.list_top,
                                self.rect.width, self.list_bottom - self.list_top)
        prev_clip = screen.get_clip()
        screen.set_clip(list_rect)

        self._row_rects = []
        y = self.list_top - self.scroll_offset
        for series, levels in self.index[self.category].items():
            y = self._draw_series_row(screen, series, y)
            if self.expanded_series == series:
                if self._is_bright_spark_series(series):
                    for topic, units in levels.items():
                        unit = units[0] if units else library.BRIGHT_SPARK_TOPIC_UNIT
                        y = self._draw_bright_spark_topic_row(screen, series, topic, unit, y)
                    continue
                for level, units in levels.items():
                    y = self._draw_level_row(screen, series, level, y)
                    if self.expanded_level == level:
                        for unit in units:
                            y = self._draw_unit_row(screen, series, level, unit, y)

        screen.set_clip(prev_clip)

        # Selection info
        self._draw_info(screen)

        # Use button
        self.use_btn.draw(screen)

        # Confirmation dialog last (above everything)
        if self.confirm_open:
            self._draw_confirm_dialog(screen)

    def _draw_empty_state(self, screen: pygame.Surface):
        msg = render_text_outlined(
            "No materials available yet.",
            T.FONT_BODY, T.TEXT_BROWN,
            outline_color=T.PARCHMENT, outline_w=1, bold=True,
        )
        screen.blit(msg, (self.rect.x + 8, self.list_top + 12))
        sub = render_text_outlined(
            "Add files to data/library/ to get started.",
            T.FONT_CAPTION, T.TEXT_MUTED,
            outline_color=T.PARCHMENT, outline_w=1, bold=False,
        )
        screen.blit(sub, (self.rect.x + 8, self.list_top + 44))

    def _draw_no_content_for_category(self, screen: pygame.Surface):
        label = "Flashcards" if self.category == "flashcards" else "Words"
        msg = render_text_outlined(
            f"No {label} materials yet.",
            T.FONT_BODY, T.TEXT_BROWN,
            outline_color=T.PARCHMENT, outline_w=1, bold=True,
        )
        screen.blit(msg, (self.rect.x + 8, self.list_top + 12))

    def _is_bright_spark_series(self, series: str) -> bool:
        return self.category == library.CATEGORY_FLASHCARDS and series == library.BRIGHT_SPARK_SERIES

    def _showing_bright_spark_topics(self) -> bool:
        return self._is_bright_spark_series(self.expanded_series or "")

    def _selected_bright_spark_topic(self) -> bool:
        return (self.selected is not None
                and self.selected[0] == library.CATEGORY_FLASHCARDS
                and self.selected[1] == library.BRIGHT_SPARK_SERIES)

    def _draw_series_row(self, screen, series: str, y: int) -> int:
        is_expanded = (self.expanded_series == series)
        label = f"{series} Categories" if self._is_bright_spark_series(series) else series
        text = ("▼ " if is_expanded else "▶ ") + label
        return self._draw_row(screen, text, y, indent=0, kind="series",
                              payload={"series": series}, bold=True)

    def _draw_level_row(self, screen, series: str, level: str, y: int) -> int:
        is_expanded = (self.expanded_level == level)
        text = ("▼ " if is_expanded else "▶ ") + level
        return self._draw_row(screen, text, y, indent=18, kind="level",
                              payload={"series": series, "level": level}, bold=False)

    def _draw_unit_row(self, screen, series: str, level: str, unit: str, y: int) -> int:
        sel = self.selected
        is_selected = (sel is not None
                       and sel[0] == self.category
                       and sel[1] == series
                       and sel[2] == level
                       and sel[3] == unit)
        return self._draw_row(screen, unit, y, indent=36, kind="unit",
                              payload={"series": series, "level": level, "unit": unit},
                              bold=False, selected=is_selected)

    def _draw_bright_spark_topic_row(self, screen, series: str, topic: str, unit: str, y: int) -> int:
        sel = self.selected
        is_selected = (sel is not None
                       and sel[0] == self.category
                       and sel[1] == series
                       and sel[2] == topic
                       and sel[3] == unit)
        return self._draw_row(screen, topic, y, indent=18, kind="bright_spark_topic",
                              payload={"series": series, "level": topic, "unit": unit},
                              bold=False, selected=is_selected)

    def _draw_row(self, screen, text: str, y: int, indent: int, kind: str,
                  payload: dict, bold: bool = False, selected: bool = False) -> int:
        # Skip rows entirely outside the visible area
        if y + LIST_ROW_HEIGHT < self.list_top or y > self.list_bottom:
            # Still register hit rect for scrolled rows? No — they aren't clickable.
            return y + LIST_ROW_HEIGHT

        row_rect = pygame.Rect(self.rect.x, y, self.rect.width, LIST_ROW_HEIGHT)

        if selected:
            pygame.draw.rect(screen, T.GOLD_LIGHT, row_rect)
            pygame.draw.rect(screen, T.GOLD_DARK, row_rect, 2)

        color = T.TEXT_DARK if not selected else T.WOOD_DARK
        surf = render_text_outlined(text, T.FONT_CAPTION, color,
                                    outline_color=T.PARCHMENT, outline_w=1, bold=bold)
        screen.blit(surf, (self.rect.x + 8 + indent, y + (LIST_ROW_HEIGHT - surf.get_height()) // 2))

        self._row_rects.append((row_rect, kind, payload))
        return y + LIST_ROW_HEIGHT

    def _draw_info(self, screen: pygame.Surface):
        info_y = self.list_bottom + 6
        if self.selected and self.preview_count > 0:
            cat, series, level, unit = self.selected
            if cat == library.CATEGORY_FLASHCARDS and series == library.BRIGHT_SPARK_SERIES:
                line1 = f"{series} / {level}"
            else:
                line1 = f"{series} / {level} / {unit}"
            kind = "images" if cat == "flashcards" else "words"
            line2 = f"{self.preview_count} {kind} loaded"
            l1 = render_text_outlined(line1, T.FONT_CAPTION, T.TEXT_DARK,
                                      outline_color=T.PARCHMENT, outline_w=1, bold=True)
            l2 = render_text_outlined(line2, T.FONT_CAPTION, T.SV_GREEN_DARK,
                                      outline_color=T.PARCHMENT, outline_w=1, bold=False)
            screen.blit(l1, (self.rect.x + 4, info_y))
            screen.blit(l2, (self.rect.x + 4, info_y + 22))
        else:
            if self.selected and self._selected_bright_spark_topic():
                hint_text = "No images in this category yet"
            elif self._showing_bright_spark_topics():
                hint_text = "Pick a Category to preview"
            else:
                hint_text = "Pick a Unit to preview"
            hint = render_text_outlined(hint_text,
                                        T.FONT_CAPTION, T.TEXT_MUTED,
                                        outline_color=T.PARCHMENT, outline_w=1, bold=False)
            screen.blit(hint, (self.rect.x + 4, info_y))

    def _draw_confirm_dialog(self, screen: pygame.Surface):
        from game.theme import SCREEN_W, SCREEN_H
        # Dim overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((82, 61, 45, 140))
        screen.blit(overlay, (0, 0))

        # Dialog box
        from game.decorations import draw_parchment_card
        draw_parchment_card(screen, self.confirm_rect)

        title = render_text_outlined(
            "Replace current items?", T.FONT_HEADING, T.TEXT_DARK,
            outline_color=T.PARCHMENT, outline_w=2, bold=True,
        )
        screen.blit(title, (self.confirm_rect.centerx - title.get_width() // 2,
                            self.confirm_rect.y + 28))

        msg = render_text_outlined(
            f"This will replace your current {len(self.pending_items)} item(s).",
            T.FONT_CAPTION, T.TEXT_BROWN,
            outline_color=T.PARCHMENT, outline_w=1, bold=False,
        )
        screen.blit(msg, (self.confirm_rect.centerx - msg.get_width() // 2,
                          self.confirm_rect.y + 80))

        self.confirm_yes_btn.draw(screen)
        self.confirm_no_btn.draw(screen)
