"""Help modal component for the settings screen."""
import pygame
from typing import Tuple, List

from game import theme as T
from game.theme import SCREEN_W, SCREEN_H
from game.ui_components import Button, get_font, render_text_outlined
from game.decorations import draw_parchment_card, draw_wood_plank
from game.icons import draw_info


class HelpModal:
    def __init__(self) -> None:
        self.open: bool = False
        self.lang: str = "en"
        self.btn_rect: pygame.Rect = pygame.Rect(SCREEN_W - 96, 56, 46, 46)
        self.modal_rect: pygame.Rect = pygame.Rect(132, 106, 760, 556)
        self.lang_btn: Button = Button(self.modal_rect.right - 150, self.modal_rect.y + 24,
                                        92, 38, "中文", T.SV_BLUE, T.TEXT_LIGHT, T.FONT_CAPTION)
        self.close_btn: Button = Button(self.modal_rect.right - 50, self.modal_rect.y + 24,
                                         32, 38, "X", T.SV_RED, T.TEXT_LIGHT, T.FONT_CAPTION)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events when modal is open."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.open = False
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        pos = event.pos
        if self.close_btn.is_clicked(pos, True):
            self.open = False
        elif self.lang_btn.is_clicked(pos, True):
            self.lang = "zh" if self.lang == "en" else "en"

    def update(self, mouse_pos: Tuple[int, int], dt: int) -> None:
        """Update button hover states."""
        self.lang_btn.update(mouse_pos, dt)
        self.close_btn.update(mouse_pos, dt)

    def draw_entry_button(self, screen: pygame.Surface) -> None:
        """Draw the help button in the top-right corner."""
        label = render_text_outlined(
            "Need Help? ->", T.FONT_CAPTION, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True,
        )
        screen.blit(label, (self.btn_rect.x - label.get_width() - 10,
                           self.btn_rect.centery - label.get_height() // 2))
        pygame.draw.rect(screen, T.SHADOW_COLOR, self.btn_rect.move(3, 4))
        pygame.draw.rect(screen, T.WOOD_DARK, self.btn_rect)
        pygame.draw.rect(screen, T.GOLD_LIGHT, self.btn_rect.inflate(-6, -6))
        draw_info(screen, self.btn_rect.centerx, self.btn_rect.centery, 13, T.WOOD_DARK)

    def draw_modal(self, screen: pygame.Surface) -> None:
        """Draw the help modal overlay."""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((82, 61, 45, 116))
        screen.blit(overlay, (0, 0))

        draw_parchment_card(screen, self.modal_rect)
        title_text = "Game Guide" if self.lang == "en" else "游戏说明"
        title = render_text_outlined(
            title_text, T.FONT_HEADING, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True,
        )
        ribbon = pygame.Rect(self.modal_rect.x + 28, self.modal_rect.y + 20, 250, 44)
        draw_wood_plank(screen, ribbon, color=T.WOOD_BROWN, radius=T.RADIUS_MD, shadow=True)
        screen.blit(title, (ribbon.centerx - title.get_width() // 2,
                           ribbon.centery - title.get_height() // 2))

        self.lang_btn.text = "中文" if self.lang == "en" else "EN"
        self.lang_btn.draw(screen)
        self.close_btn.draw(screen)

        self._draw_sections(screen, self.modal_rect.x + 44, self.modal_rect.y + 92,
                           self.modal_rect.width - 88)

    def _get_content(self) -> List[Tuple[str, List[str]]]:
        """Get help content in the current language."""
        if self.lang == "zh":
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

    def _draw_sections(self, screen: pygame.Surface, x: int, y: int, max_w: int) -> None:
        """Draw help content sections."""
        for section_title, lines in self._get_content():
            title = render_text_outlined(
                section_title, T.FONT_BODY, T.TEXT_DARK,
                outline_color=T.PARCHMENT, outline_w=1, bold=True,
            )
            screen.blit(title, (x, y))
            y += 32
            number = 1
            for line in lines:
                is_note = line.startswith("(") or line.startswith("（")
                bullet = "" if is_note else f"{number}. "
                if not is_note:
                    number += 1
                wrapped = self._wrap_text(bullet + line, T.FONT_CAPTION, max_w - 18)
                color = T.TEXT_MUTED if is_note else T.TEXT_BROWN
                for wrapped_line in wrapped:
                    surf = render_text_outlined(
                        wrapped_line, T.FONT_CAPTION, color,
                        outline_color=T.PARCHMENT, outline_w=1, bold=False,
                    )
                    screen.blit(surf, (x + 18, y))
                    y += 22
                y += 1
            y += 14

    def _wrap_text(self, text: str, size: int, max_w: int) -> List[str]:
        """Wrap text to fit within max width."""
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
