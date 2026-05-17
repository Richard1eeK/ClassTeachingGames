import pygame
import json
import os
import sys
from game.ui_components import (
    Button, Slider, TextInput, get_font,
    BG_COLOR, BLACK, WHITE, CANDY_BLUE, CANDY_GREEN, CANDY_PINK,
    CANDY_PURPLE, CANDY_YELLOW, CANDY_ORANGE, GRAY, DARK_GRAY, SCREEN_W, SCREEN_H
)


class SettingsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.cup_slider = Slider(100, 180, 300, 3, 7, 3, "杯子数量", 1)
        self.round_slider = Slider(100, 280, 300, 3, 20, 5, "游戏轮数", 1)
        self.speed_slider = Slider(100, 380, 300, 1, 5, 2, "交换速度", 1)

        self.mode_manual = Button(100, 460, 180, 50, "手动输入", CANDY_GREEN)
        self.mode_bank = Button(300, 460, 180, 50, "题库加载", CANDY_PURPLE)
        self.input_mode = "manual"

        self.manual_items = []
        self.text_input = TextInput(100, 540, 350, 45, "输入文字后按回车添加")
        self.add_image_btn = Button(460, 540, 120, 45, "添加图片", CANDY_ORANGE)

        self.bank_files = self._scan_banks()
        self.selected_bank = 0

        self.start_btn = Button(SCREEN_W // 2 - 100, SCREEN_H - 90, 200, 60, "开始游戏!", CANDY_PINK, BLACK, 32)

        self.speed_labels = {1: "慢", 2: "中", 3: "快", 4: "超快", 5: "疯狂"}

    def _scan_banks(self):
        banks = []
        data_dir = self._get_data_dir()
        custom_dir = os.path.join(data_dir, "custom")
        if os.path.exists(custom_dir):
            for f in sorted(os.listdir(custom_dir)):
                if f.endswith(".json"):
                    banks.append((f.replace(".json", ""), os.path.join(custom_dir, f)))
        return banks

    def _get_data_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, "data")
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        return self._get_settings()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None

            self.cup_slider.handle_event(event)
            self.round_slider.handle_event(event)
            self.speed_slider.handle_event(event)

            if self.input_mode == "manual":
                result = self.text_input.handle_event(event)
                if result == "enter" and self.text_input.text.strip():
                    self.manual_items.append({"type": "text", "content": self.text_input.text.strip(), "hint": ""})
                    self.text_input.text = ""

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.mode_manual.is_clicked(pos, True):
                    self.input_mode = "manual"
                elif self.mode_bank.is_clicked(pos, True):
                    self.input_mode = "bank"
                elif self.start_btn.is_clicked(pos, True):
                    self.running = False
                elif self.input_mode == "manual" and self.add_image_btn.is_clicked(pos, True):
                    self._add_image()
                elif self.input_mode == "bank" and self.bank_files:
                    for i, (name, path) in enumerate(self.bank_files):
                        btn_rect = pygame.Rect(100, 540 + i * 45, 400, 40)
                        if btn_rect.collidepoint(pos):
                            self.selected_bank = i

    def _add_image(self):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif")]
            )
            root.destroy()
            if file_path:
                self.manual_items.append({"type": "image", "content": file_path, "hint": ""})
        except:
            pass

    def _update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.mode_manual.update(mouse_pos)
        self.mode_bank.update(mouse_pos)
        self.start_btn.update(mouse_pos)
        self.add_image_btn.update(mouse_pos)
        if self.input_mode == "manual":
            self.text_input.update(dt)

        can_start = True
        if self.input_mode == "manual" and len(self.manual_items) < 1:
            can_start = False
        if self.input_mode == "bank" and not self.bank_files:
            can_start = False
        self.start_btn.enabled = can_start

    def _draw(self):
        self.screen.fill(BG_COLOR)

        title_font = get_font(40, bold=True)
        title = title_font.render("猜杯子游戏 - 设置", True, BLACK)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))

        self.cup_slider.draw(self.screen)
        self.round_slider.draw(self.screen)

        speed_font = get_font(24)
        speed_text = speed_font.render(
            f"交换速度: {self.speed_labels.get(self.speed_slider.value, '中')}",
            True, BLACK
        )
        self.screen.blit(speed_text, (100, self.speed_slider.y - 30))
        self.speed_slider.label = f"交换速度 ({self.speed_labels.get(self.speed_slider.value, '中')})"
        self.speed_slider.draw(self.screen)

        mode_font = get_font(24)
        mode_text = mode_font.render("内容来源:", True, BLACK)
        self.screen.blit(mode_text, (100, 435))

        self.mode_manual.color = CANDY_GREEN if self.input_mode == "manual" else GRAY
        self.mode_bank.color = CANDY_PURPLE if self.input_mode == "bank" else GRAY
        self.mode_manual.draw(self.screen)
        self.mode_bank.draw(self.screen)

        if self.input_mode == "manual":
            self.text_input.draw(self.screen)
            self.add_image_btn.draw(self.screen)

            items_font = get_font(20)
            y_offset = 600
            for i, item in enumerate(self.manual_items[-6:]):
                display = item["content"] if item["type"] == "text" else f"[图片] {os.path.basename(item['content'])}"
                item_text = items_font.render(f"  {i+1}. {display}", True, DARK_GRAY)
                self.screen.blit(item_text, (100, y_offset + i * 28))

            if len(self.manual_items) < 1:
                hint = items_font.render("请至少添加 1 项内容（每轮随机选一个作为目标）", True, CANDY_PINK)
                self.screen.blit(hint, (100, y_offset + min(len(self.manual_items), 6) * 28 + 5))

        elif self.input_mode == "bank":
            bank_font = get_font(22)
            if self.bank_files:
                y = 540
                for i, (name, path) in enumerate(self.bank_files):
                    btn_rect = pygame.Rect(100, y + i * 45, 400, 40)
                    color = CANDY_BLUE if i == self.selected_bank else WHITE
                    pygame.draw.rect(self.screen, color, btn_rect, border_radius=8)
                    pygame.draw.rect(self.screen, DARK_GRAY, btn_rect, 1, border_radius=8)
                    text = bank_font.render(f"  {'> ' if i == self.selected_bank else '  '}{name}", True, BLACK)
                    self.screen.blit(text, (btn_rect.x + 10, btn_rect.centery - text.get_height() // 2))

                help_font = get_font(18)
                help_texts = [
                    "JSON 格式: [{\"type\":\"text\",\"content\":\"A\",\"hint\":\"字母A\"}]",
                    "type: text 或 image, content: 内容, hint: 提示(可选)",
                    "题库文件放入 data/custom/ 文件夹即可",
                ]
                for j, t in enumerate(help_texts):
                    hs = help_font.render(t, True, DARK_GRAY)
                    self.screen.blit(hs, (100, y + len(self.bank_files) * 45 + 20 + j * 22))
            else:
                no_bank = bank_font.render("(暂无题库文件)", True, GRAY)
                self.screen.blit(no_bank, (100, 550))
                help_font = get_font(18)
                help_texts = [
                    "题库需为 JSON 文件，放入 data/custom/ 文件夹",
                    "格式示例: [{\"type\":\"text\",\"content\":\"A\",\"hint\":\"字母A\"}]",
                    "每轮会从题库中随机选一个作为目标",
                ]
                for j, t in enumerate(help_texts):
                    hs = help_font.render(t, True, DARK_GRAY)
                    self.screen.blit(hs, (100, 590 + j * 22))

        self.start_btn.draw(self.screen)

    def _get_settings(self):
        items = []
        if self.input_mode == "bank" and self.bank_files:
            _, path = self.bank_files[self.selected_bank]
            try:
                with open(path, "r", encoding="utf-8") as f:
                    items = json.load(f)
            except:
                items = [{"type": "text", "content": chr(65 + i), "hint": ""} for i in range(26)]
        else:
            items = self.manual_items

        speed_map = {1: 1200, 2: 800, 3: 500, 4: 280, 5: 150}
        speed_level = self.speed_slider.value

        return {
            "num_cups": self.cup_slider.value,
            "num_rounds": self.round_slider.value,
            "swap_duration": speed_map.get(speed_level, 800),
            "speed_level": speed_level,
            "items": items,
        }
