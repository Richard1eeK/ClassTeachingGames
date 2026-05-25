import pygame
import os

from game import theme as T
from game.theme import SCREEN_W, SCREEN_H
from game.ui_components import (
    Button, Slider, TextInput, Card, WoodSign,
    get_font, render_text_outlined,
)
from game.decorations import (
    get_wood_background, draw_parchment_card, draw_wood_plank,
    make_floating_decorations, update_floating_decorations,
    draw_floating_decorations,
)
from game.icons import (
    draw_snail, draw_rabbit, draw_lightning, draw_flame, draw_tornado,
    draw_info, draw_text_icon, draw_image_icon,
)
from game.question_bank import read_text_bank_file, scan_image_folder
from game.help_modal import HelpModal
from game.item_list import ItemList


SPEED_ICONS = [
    (1, "Slow", draw_snail, T.WOOD_BROWN),
    (2, "Medium", draw_rabbit, T.WOOD_BROWN),
    (3, "Fast", draw_lightning, T.GOLD_DARK),
    (4, "Ultra", draw_flame, T.SV_RED),
    (5, "Insane", draw_tornado, T.SV_PURPLE),
]


def normalize_settings(settings):
    """Validate and clamp all settings to safe ranges."""
    if not settings:
        return {}

    normalized = {}

    # Clamp answer_count: 1-5
    answer_count = max(1, min(5, settings.get("answer_count", 1)))
    normalized["answer_count"] = answer_count

    # Clamp num_cups: must be >= answer_count + 2, max 9
    num_cups = max(answer_count + 2, min(9, settings.get("num_cups", answer_count + 2)))
    normalized["num_cups"] = num_cups

    # Clamp num_rounds: 1-50
    normalized["num_rounds"] = max(1, min(50, settings.get("num_rounds", 5)))

    # Clamp speed_level: 1-5
    normalized["speed_level"] = max(1, min(5, settings.get("speed_level", 2)))

    # Copy items list
    normalized["items"] = list(settings.get("items", []))

    return normalized


class SettingsScreen:
    def __init__(self, window, initial_settings=None):
        self.window = window
        self.screen = window.surface
        self.clock = pygame.time.Clock()
        self.running = True
        self.quit_requested = False

        # Normalize and validate initial_settings
        init = normalize_settings(initial_settings or {})
        init_answers = init.get("answer_count", 1)
        init_cups = init.get("num_cups", 3)
        init_rounds = init.get("num_rounds", 5)
        init_speed = init.get("speed_level", 2)
        init_items = init.get("items", [])

        # Left card: Answers / Cups / Rounds / Speed
        self.left_card = Card(50, 130, 430, 510, title="Game Settings")
        self.answer_slider = Slider(self.left_card.rect.x + 34, self.left_card.rect.y + 82,
                                    self.left_card.rect.width - 68, 1, 5, init_answers, "Answers")
        self.cup_slider = Slider(self.left_card.rect.x + 34, self.left_card.rect.y + 172,
                                 self.left_card.rect.width - 68, 3, 9, init_cups, "Cups")
        self.round_slider = Slider(self.left_card.rect.x + 34, self.left_card.rect.y + 262,
                                   self.left_card.rect.width - 68, 3, 20, init_rounds, "Rounds")
        self.speed_slider = Slider(self.left_card.rect.x + 34, self.left_card.rect.y + 352,
                                   self.left_card.rect.width - 68, 1, 5, init_speed, "Speed")

        # Right card: content
        self.right_card = Card(SCREEN_W - 480, 130, 430, 510, title="Your Items")
        self.text_input = TextInput(
            self.right_card.rect.x + 26, self.right_card.rect.y + 70,
            self.right_card.rect.width - 252, 44, "Type a word and press Enter",
            font_size=T.FONT_CAPTION,
        )
        self.import_text_btn = Button(
            self.right_card.rect.right - 212, self.right_card.rect.y + 70,
            90, 44, "Import", T.GOLD, T.TEXT_LIGHT, T.FONT_CAPTION,
            icon=draw_text_icon,
        )
        self.add_image_btn = Button(
            self.right_card.rect.right - 116, self.right_card.rect.y + 70,
            90, 44, "Folder", T.SV_BLUE, T.TEXT_LIGHT, T.FONT_CAPTION,
            icon=draw_image_icon,
        )

        self.item_list = ItemList(init_items)

        # Status message for import feedback
        self.status_message = ""
        self.status_timer = 0
        self.status_color = T.GOLD_DARK

        # Hanging title sign
        self.title_sign = WoodSign(SCREEN_W // 2 - 240, 44, 480, 62,
                                   "Shell Cup Game", font_size=T.FONT_TITLE)

        self.start_btn = Button(SCREEN_W // 2 - 120, SCREEN_H - 94, 240, 54,
                                "Start Game!", T.SV_GREEN, T.TEXT_LIGHT, T.FONT_HEADING)
        self.help_modal = HelpModal()

        self.decorations = make_floating_decorations(8, SCREEN_W, SCREEN_H, seed=11)

        self.speed_labels = {1: "Slow", 2: "Medium", 3: "Fast", 4: "Ultra", 5: "Insane"}

    def run(self):
        # Register live-repaint callback so the screen redraws while the user
        # is still dragging the resize handle (OS blocks the event loop otherwise).
        self.window.on_resize = self._repaint_during_resize
        try:
            while self.running:
                dt = self.clock.tick(60)
                self._handle_events()
                self._update(dt)
                self._draw()
                self.window.present()
        finally:
            self.window.on_resize = None

        if self.quit_requested:
            return None
        return self._get_settings()

    def _handle_events(self):
        for event in pygame.event.get():
            event = self.window.event_to_logical(event)
            if event.type == pygame.QUIT:
                self.quit_requested = True
                self.running = False
                return
            if self.help_modal.open:
                self.help_modal.handle_event(event)
                continue

            prev_answers = self.answer_slider.value
            self.answer_slider.handle_event(event)
            if self.answer_slider.value != prev_answers:
                self.cup_slider.value = max(self.cup_slider.value, self.answer_slider.value + 2)
            self.cup_slider.min_val = self.answer_slider.value + 2
            self.cup_slider.handle_event(event)
            self.cup_slider.value = max(self.cup_slider.value, self.answer_slider.value + 2)
            self.round_slider.handle_event(event)
            self.speed_slider.handle_event(event)

            result = self.text_input.handle_event(event)
            if result == "enter" and self.text_input.text.strip():
                self.item_list.add_item({
                    "type": "text",
                    "content": self.text_input.text.strip(),
                    "hint": "",
                })
                self.text_input.text = ""

            if event.type == pygame.MOUSEWHEEL:
                self.item_list.handle_scroll(event, 320)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.start_btn.is_clicked(pos, True):
                    self.running = False
                elif self.import_text_btn.is_clicked(pos, True):
                    self._import_text_bank()
                elif self.add_image_btn.is_clicked(pos, True):
                    self._import_image_folder()
                elif self.help_modal.btn_rect.collidepoint(pos):
                    self.help_modal.open = True
                else:
                    # delete buttons in items list
                    self.item_list.handle_delete_click(pos)

    def _import_text_bank(self):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            root.destroy()
            if file_path:
                items = read_text_bank_file(file_path)
                if items:
                    self.item_list.extend_items(items)
                    self.status_message = f"Imported {len(items)} items"
                    self.status_color = T.SV_GREEN
                    self.status_timer = 3000
                else:
                    self.status_message = "No valid items found in file"
                    self.status_color = T.SV_RED
                    self.status_timer = 3000
        except Exception as e:
            self.status_message = f"Import failed: {str(e)[:40]}"
            self.status_color = T.SV_RED
            self.status_timer = 3000

    def _import_image_folder(self):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            folder_path = filedialog.askdirectory()
            root.destroy()
            if folder_path:
                items = scan_image_folder(folder_path)
                if items:
                    self.item_list.extend_items(items)
                    self.status_message = f"Imported {len(items)} images"
                    self.status_color = T.SV_GREEN
                    self.status_timer = 3000
                else:
                    self.status_message = "No valid images found"
                    self.status_color = T.SV_RED
                    self.status_timer = 3000
        except Exception as e:
            self.status_message = f"Import failed: {str(e)[:40]}"
            self.status_color = T.SV_RED
            self.status_timer = 3000

    def _repaint_during_resize(self):
        """Called by ScaledWindow during VIDEORESIZE so the window stays live while dragging."""
        try:
            self._draw()
            self.window.present()
        except Exception:
            pass

    def _update(self, dt):
        mouse_pos = self.window.get_mouse_pos()
        self.help_modal.update(mouse_pos, dt)
        if self.help_modal.open:
            update_floating_decorations(self.decorations, dt)
            return
        self.start_btn.update(mouse_pos, dt)
        self.cup_slider.min_val = self.answer_slider.value + 2
        self.cup_slider.value = max(self.cup_slider.value, self.cup_slider.min_val)
        self.import_text_btn.update(mouse_pos, dt)
        self.add_image_btn.update(mouse_pos, dt)
        self.text_input.update(dt)
        update_floating_decorations(self.decorations, dt)

        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= dt

        can_start = len(self.item_list.items) >= 1
        self.start_btn.enabled = can_start

    def _draw(self):
        bg = get_wood_background(SCREEN_W, SCREEN_H)
        self.screen.blit(bg, (0, 0))
        draw_floating_decorations(self.screen, self.decorations, SCREEN_W, SCREEN_H)

        self.title_sign.draw(self.screen)

        # === Left card: settings ===
        self.left_card.draw(self.screen)
        self.answer_slider.draw(self.screen)
        self._draw_slider_label(self.answer_slider, f"Answers: {self.answer_slider.value}")
        self._draw_answers_helper()
        self.cup_slider.draw(self.screen)
        self._draw_slider_label(self.cup_slider, f"Cups: {self.cup_slider.value}")
        self.round_slider.draw(self.screen)
        self._draw_slider_label(self.round_slider, f"Rounds: {self.round_slider.value}")
        self.speed_slider.draw(self.screen)
        self._draw_slider_label(
            self.speed_slider,
            f"Speed: {self.speed_labels.get(self.speed_slider.value, 'Medium')}"
        )

        # speed icons row (under slider)
        self._draw_speed_icons()

        # === Right card: items ===
        self.right_card.draw(self.screen)
        self.text_input.draw(self.screen)
        self.import_text_btn.draw(self.screen)
        self.add_image_btn.draw(self.screen)

        # Draw items list
        list_rect = pygame.Rect(
            self.right_card.rect.x + 26,
            self.right_card.rect.y + 130,
            self.right_card.rect.width - 52,
            self.right_card.rect.bottom - 24 - (self.right_card.rect.y + 130)
        )
        self.item_list.draw(self.screen, list_rect)

        self.start_btn.draw(self.screen)
        self.help_modal.draw_entry_button(self.screen)

        # Draw status message if active
        if self.status_timer > 0:
            status_surf = render_text_outlined(
                self.status_message, T.FONT_BODY, self.status_color,
                outline_color=T.WOOD_DARK, outline_w=2, bold=True
            )
            status_x = SCREEN_W // 2 - status_surf.get_width() // 2
            status_y = SCREEN_H - 160
            self.screen.blit(status_surf, (status_x, status_y))

        if self.help_modal.open:
            self.help_modal.draw_modal(self.screen)

    def _draw_answers_helper(self):
        helper = render_text_outlined(
            f"Cups need at least {self.answer_slider.value + 2}; you can add more.",
            T.FONT_CAPTION,
            T.TEXT_MUTED,
            outline_color=T.PARCHMENT,
            outline_w=1,
            bold=False,
        )
        self.screen.blit(helper, (self.answer_slider.x, self.answer_slider.y + 32))

    def _draw_slider_label(self, slider, text):
        # cover the light-text label drawn by the slider (parchment background)
        cover = pygame.Rect(slider.x - 4, slider.y - 36, slider.w + 8, 30)
        pygame.draw.rect(self.screen, T.PARCHMENT, cover)
        label = render_text_outlined(text, T.FONT_BODY, T.TEXT_DARK,
                                     outline_color=T.PARCHMENT, outline_w=1, bold=True)
        self.screen.blit(label, (slider.x, slider.y - 32))

    def _draw_speed_icons(self):
        slider = self.speed_slider
        y = slider.y + 52
        track_x = slider.x
        track_w = slider.w
        for value, label, icon_fn, color in SPEED_ICONS:
            ratio = (value - slider.min_val) / (slider.max_val - slider.min_val)
            cx = track_x + int(ratio * track_w)
            selected = (value == slider.value)
            size = 14 if selected else 11
            if selected:
                pygame.draw.rect(self.screen, T.GOLD_LIGHT, (cx - 18, y - 18, 36, 36))
                pygame.draw.rect(self.screen, T.GOLD_DARK, (cx - 18, y - 18, 36, 36), 2)
            icon_fn(self.screen, cx, y, size, color)
            if selected:
                lbl = render_text_outlined(label, T.FONT_CAPTION, T.TEXT_DARK,
                                           outline_color=T.PARCHMENT, outline_w=1, bold=True)
                self.screen.blit(lbl, (cx - lbl.get_width() // 2, y + 24))

    def _get_settings(self):
        speed_map = {1: 1200, 2: 800, 3: 500, 4: 280, 5: 150}
        speed_level = self.speed_slider.value

        return {
            "answer_count": self.answer_slider.value,
            "num_cups": self.cup_slider.value,
            "num_rounds": self.round_slider.value,
            "swap_duration": speed_map.get(speed_level, 800),
            "speed_level": speed_level,
            "items": self.item_list.items,
        }
