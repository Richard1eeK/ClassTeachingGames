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
    draw_image_icon, draw_text_icon, draw_trash, draw_plus, draw_info,
)
from game.question_bank import read_text_bank_file, scan_image_folder


SPEED_ICONS = [
    (1, "Slow", draw_snail, T.WOOD_BROWN),
    (2, "Medium", draw_rabbit, T.WOOD_BROWN),
    (3, "Fast", draw_lightning, T.GOLD_DARK),
    (4, "Ultra", draw_flame, T.SV_RED),
    (5, "Insane", draw_tornado, T.SV_PURPLE),
]


class SettingsScreen:
    def __init__(self, window, initial_settings=None):
        self.window = window
        self.screen = window.surface
        self.clock = pygame.time.Clock()
        self.running = True
        self.quit_requested = False

        # Read defaults from initial_settings (preserve previous round's choices)
        init = initial_settings or {}
        init_answers = max(1, min(5, init.get("answer_count", max(1, init.get("num_cups", 3) - 2))))
        init_cups = max(init_answers + 2, min(9, init.get("num_cups", init_answers + 2)))
        init_rounds = init.get("num_rounds", 5)
        init_speed = init.get("speed_level", 2)
        init_items = list(init.get("items", []))

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

        self.manual_items = init_items
        self.scroll_offset = 0
        self._delete_btn_rects = []  # tuples of (rect, item_index)

        # Hanging title sign
        self.title_sign = WoodSign(SCREEN_W // 2 - 240, 44, 480, 62,
                                   "Shell Cup Game", font_size=T.FONT_TITLE)

        self.start_btn = Button(SCREEN_W // 2 - 120, SCREEN_H - 94, 240, 54,
                                "Start Game!", T.SV_GREEN, T.TEXT_LIGHT, T.FONT_HEADING)
        self.help_open = False
        self.help_lang = "en"
        self.help_btn_rect = pygame.Rect(SCREEN_W - 96, 56, 46, 46)
        self.help_modal_rect = pygame.Rect(132, 106, 760, 556)
        self.help_lang_btn = Button(self.help_modal_rect.right - 150, self.help_modal_rect.y + 24,
                                    92, 38, "中文", T.SV_BLUE, T.TEXT_LIGHT, T.FONT_CAPTION)
        self.help_close_btn = Button(self.help_modal_rect.right - 50, self.help_modal_rect.y + 24,
                                     32, 38, "X", T.SV_RED, T.TEXT_LIGHT, T.FONT_CAPTION)

        self.decorations = make_floating_decorations(8, SCREEN_W, SCREEN_H, seed=11)

        self.speed_labels = {1: "Slow", 2: "Medium", 3: "Fast", 4: "Ultra", 5: "Insane"}

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self._handle_events()
            self._update(dt)
            self._draw()
            self.window.present()

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
            if self.help_open:
                self._handle_help_event(event)
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
                self.manual_items.append({
                    "type": "text",
                    "content": self.text_input.text.strip(),
                    "hint": "",
                })
                self.text_input.text = ""

            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset = max(0, self.scroll_offset - event.y * 30)
                max_scroll = max(0, len(self.manual_items) * 48 - 320)
                self.scroll_offset = min(self.scroll_offset, max_scroll)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.start_btn.is_clicked(pos, True):
                    self.running = False
                elif self.import_text_btn.is_clicked(pos, True):
                    self._import_text_bank()
                elif self.add_image_btn.is_clicked(pos, True):
                    self._import_image_folder()
                elif self.help_btn_rect.collidepoint(pos):
                    self.help_open = True
                else:
                    # delete buttons in items list
                    for rect, idx in self._delete_btn_rects:
                        if rect.collidepoint(pos):
                            if 0 <= idx < len(self.manual_items):
                                self.manual_items.pop(idx)
                            break

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
                    self.manual_items.extend(items)
        except Exception:
            pass

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
                    self.manual_items.extend(items)
        except Exception:
            pass

    def _update(self, dt):
        mouse_pos = self.window.get_mouse_pos()
        self.help_lang_btn.update(mouse_pos, dt)
        self.help_close_btn.update(mouse_pos, dt)
        if self.help_open:
            update_floating_decorations(self.decorations, dt)
            return
        self.start_btn.update(mouse_pos, dt)
        self.cup_slider.min_val = self.answer_slider.value + 2
        self.cup_slider.value = max(self.cup_slider.value, self.cup_slider.min_val)
        self.import_text_btn.update(mouse_pos, dt)
        self.add_image_btn.update(mouse_pos, dt)
        self.text_input.update(dt)
        update_floating_decorations(self.decorations, dt)

        can_start = len(self.manual_items) >= 1
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
        self._draw_items_list()

        self.start_btn.draw(self.screen)
        self._draw_help_entry()
        if self.help_open:
            self._draw_help_modal()

    def _handle_help_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.help_open = False
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        pos = event.pos
        if self.help_close_btn.is_clicked(pos, True):
            self.help_open = False
        elif self.help_lang_btn.is_clicked(pos, True):
            self.help_lang = "zh" if self.help_lang == "en" else "en"

    def _draw_help_entry(self):
        label = render_text_outlined(
            "Need Help? ->", T.FONT_CAPTION, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True,
        )
        self.screen.blit(label, (self.help_btn_rect.x - label.get_width() - 10,
                                 self.help_btn_rect.centery - label.get_height() // 2))
        pygame.draw.rect(self.screen, T.SHADOW_COLOR, self.help_btn_rect.move(3, 4))
        pygame.draw.rect(self.screen, T.WOOD_DARK, self.help_btn_rect)
        pygame.draw.rect(self.screen, T.GOLD_LIGHT, self.help_btn_rect.inflate(-6, -6))
        draw_info(self.screen, self.help_btn_rect.centerx, self.help_btn_rect.centery, 13, T.WOOD_DARK)

    def _draw_help_modal(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((82, 61, 45, 116))
        self.screen.blit(overlay, (0, 0))

        draw_parchment_card(self.screen, self.help_modal_rect)
        title_text = "Game Guide" if self.help_lang == "en" else "游戏说明"
        title = render_text_outlined(
            title_text, T.FONT_HEADING, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True,
        )
        ribbon = pygame.Rect(self.help_modal_rect.x + 28, self.help_modal_rect.y + 20, 250, 44)
        draw_wood_plank(self.screen, ribbon, color=T.WOOD_BROWN, radius=T.RADIUS_MD, shadow=True)
        self.screen.blit(title, (ribbon.centerx - title.get_width() // 2,
                                 ribbon.centery - title.get_height() // 2))

        self.help_lang_btn.text = "中文" if self.help_lang == "en" else "EN"
        self.help_lang_btn.draw(self.screen)
        self.help_close_btn.draw(self.screen)

        self._draw_help_sections(self.help_modal_rect.x + 44, self.help_modal_rect.y + 92,
                                 self.help_modal_rect.width - 88)

    def _help_content(self):
        if self.help_lang == "zh":
            return [
                ("如何设置", [
                    "用 Answers 选择每一轮有几个正确答案。",
                    "用 Cups 选择杯子数量。",
                    "用 Rounds 选择游戏轮数。",
                    "用 Speed 选择洗牌速度。",
                ]),
                ("添加题目", [
                    "输入单词后按 Enter 添加。",
                    "点击 Import 从 .txt 文件导入单词。",
                    ".txt 文件中每行写一个带序号的单词，例如 1. apple、2. banana、3. cat。",
                    "（可以截图单词表后，用 AI 帮你整理成带序号的文本。）",
                    "点击 Folder 从文件夹导入图片。",
                    "至少添加 1 个题目后才能开始游戏。",
                ]),
                ("怎么玩", [
                    "先认真看目标答案。",
                    "观察杯子洗牌。",
                    "点击你认为正确的杯子。",
                    "如果全部选对，就得 1 分。",
                ]),
            ]
        return [
            ("How to Set Up", [
                "Choose how many correct answers you want with Answers.",
                "Choose how many cups you want with Cups.",
                "Choose the number of rounds with Rounds.",
                "Choose the shuffle speed with Speed.",
            ]),
            ("Add Your Items", [
                "Type a word and press Enter to add it.",
                "Click Import to add words from a .txt file.",
                "In the .txt file, put one word on each line with a number, like 1. apple, 2. banana, 3. cat.",
                "(You can screenshot a word list and ask AI to turn it into numbered text.)",
                "Click Folder to add pictures from a folder.",
                "You need at least one item to start the game.",
            ]),
            ("How to Play", [
                "Look carefully at the target answer or answers.",
                "Watch the cups shuffle.",
                "Click the cup or cups you think are correct.",
                "If all your choices are correct, you score 1 point.",
            ]),
        ]

    def _draw_help_sections(self, x, y, max_w):
        for section_title, lines in self._help_content():
            title = render_text_outlined(
                section_title, T.FONT_BODY, T.TEXT_DARK,
                outline_color=T.PARCHMENT, outline_w=1, bold=True,
            )
            self.screen.blit(title, (x, y))
            y += 32
            number = 1
            for line in lines:
                is_note = line.startswith("(") or line.startswith("（")
                bullet = "" if is_note else f"{number}. "
                if not is_note:
                    number += 1
                wrapped = self._wrap_help_text(bullet + line, T.FONT_CAPTION, max_w - 18)
                color = T.TEXT_MUTED if is_note else T.TEXT_BROWN
                for wrapped_line in wrapped:
                    surf = render_text_outlined(
                        wrapped_line, T.FONT_CAPTION, color,
                        outline_color=T.PARCHMENT, outline_w=1, bold=False,
                    )
                    self.screen.blit(surf, (x + 18, y))
                    y += 22
                y += 1
            y += 14

    def _wrap_help_text(self, text, size, max_w):
        font = get_font(size, text=text)
        if font.size(text)[0] <= max_w:
            return [text]
        units = text.split(" ") if " " in text else list(text)
        lines = []
        current = ""
        sep = " " if " " in text else ""
        for unit in units:
            candidate = unit if not current else current + sep + unit
            if font.size(candidate)[0] <= max_w:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = unit
        if current:
            lines.append(current)
        return lines

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

    def _draw_items_list(self):
        self._delete_btn_rects = []
        list_top = self.right_card.rect.y + 130
        list_bottom = self.right_card.rect.bottom - 24
        list_left = self.right_card.rect.x + 26
        list_right = self.right_card.rect.right - 26
        # clipping region
        clip_rect = pygame.Rect(list_left, list_top,
                                list_right - list_left, list_bottom - list_top)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        item_h = 38
        if not self.manual_items:
            hint = render_text_outlined(
                "Add at least 1 item to start.",
                T.FONT_BODY, T.TEXT_BROWN, outline_color=T.PARCHMENT,
                outline_w=1, bold=True,
            )
            self.screen.blit(hint, (list_left + 8, list_top + 12))
            sub = render_text_outlined(
                "Each round picks one randomly.",
                T.FONT_CAPTION, T.TEXT_MUTED, outline_color=T.PARCHMENT,
                outline_w=1, bold=False,
            )
            self.screen.blit(sub, (list_left + 8, list_top + 44))
        else:
            for i, item in enumerate(self.manual_items):
                row_y = list_top + i * item_h - self.scroll_offset
                if row_y + item_h < list_top or row_y > list_bottom:
                    continue
                row_rect = pygame.Rect(list_left, row_y, list_right - list_left, item_h - 5)
                pygame.draw.rect(self.screen, T.WOOD_DARK, row_rect)
                pygame.draw.rect(self.screen, T.PARCHMENT_DARK, row_rect.inflate(-4, -4))

                # type icon
                icon_x = row_rect.x + 22
                icon_y = row_rect.centery
                if item["type"] == "image":
                    draw_image_icon(self.screen, icon_x, icon_y, 11)
                else:
                    draw_text_icon(self.screen, icon_x, icon_y, 11)

                # content text
                if item["type"] == "image":
                    display = os.path.basename(item["content"])
                else:
                    display = str(item["content"])
                if len(display) > 22:
                    display = display[:21] + "…"
                txt = render_text_outlined(
                    f"{i + 1}. {display}", T.FONT_CAPTION, T.TEXT_DARK,
                    outline_color=T.PARCHMENT_DARK, outline_w=1, bold=False,
                )
                self.screen.blit(txt, (icon_x + 22, row_rect.centery - txt.get_height() // 2))

                # delete button
                del_x = row_rect.right - 24
                del_y = row_rect.centery
                del_rect = pygame.Rect(del_x - 14, del_y - 12, 28, 24)
                pygame.draw.rect(self.screen, T.WOOD_DARK, del_rect)
                pygame.draw.rect(self.screen, T.SV_RED, del_rect.inflate(-4, -4))
                draw_trash(self.screen, del_x, del_y, 8)
                self._delete_btn_rects.append((del_rect, i))

        self.screen.set_clip(prev_clip)

        # scroll hint
        if len(self.manual_items) * item_h > (list_bottom - list_top):
            count_text = render_text_outlined(
                f"{len(self.manual_items)} items (scroll to see more)",
                T.FONT_CAPTION, T.TEXT_MUTED,
                outline_color=T.PARCHMENT, outline_w=1, bold=False,
            )
            self.screen.blit(
                count_text,
                (list_left + 4, list_bottom - count_text.get_height() - 2),
            )

    def _get_settings(self):
        speed_map = {1: 1200, 2: 800, 3: 500, 4: 280, 5: 150}
        speed_level = self.speed_slider.value

        return {
            "answer_count": self.answer_slider.value,
            "num_cups": self.cup_slider.value,
            "num_rounds": self.round_slider.value,
            "swap_duration": speed_map.get(speed_level, 800),
            "speed_level": speed_level,
            "items": self.manual_items,
        }
