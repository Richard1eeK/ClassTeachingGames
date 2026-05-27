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
                ("游戏设置（左侧面板）", [
                    "Answers：每一轮有几个正确答案（1~5）。",
                    "Cups：杯子总数量（至少 Answers + 2）。",
                    "Rounds：总共玩几轮（3~20）。",
                    "Speed：洗牌速度，共 5 档，越高越快。",
                ]),
                ("素材来源（右侧面板）", [
                    "Resources 标签：浏览内置材料库。",
                    "  - Bright Spark：按词汇类别组织的闪卡（Activities、Colours、Numbers 等 37 类）。",
                    "  - High Flyer：按 Level / Unit 组织的文字和图片库。",
                    "  - 切换 Flashcards / Words 可筛选图片或文字材料。",
                    "  - 点击类别再点 Use this material 即可加载。",
                    "Manually Type-in 标签：手动输入或导入自己的题目。",
                    "  - 输入单词后按 Enter 添加。",
                    "  - 点击 Import 从 .txt 文件批量导入（每行一个带序号单词，如 1. apple）。",
                    "  - 点击 Folder 从文件夹导入图片。",
                ]),
                ("怎么玩", [
                    "认真看目标答案（intro 阶段会放大展示）。",
                    "观察杯子洗牌。",
                    "点击正确的杯子。多答案模式下需选满全部目标。",
                    "全部选对得 1 分；揭示阶段会显示正确答案卡片。",
                ]),
                ("快捷操作", [
                    "结算页面 Same Again 用相同素材直接再玩。",
                    "Adjust 回到设置页面调整参数后继续。",
                    "游戏中途可按右上角 Exit 随时退出。",
                ]),
            ]
        return [
            ("Game Settings (left panel)", [
                "Answers: how many correct answers per round (1–5).",
                "Cups: total number of cups (at least Answers + 2).",
                "Rounds: how many rounds to play (3–20).",
                "Speed: shuffle speed, 5 levels from Slow to Insane.",
            ]),
            ("Materials (right panel)", [
                "Resources tab: browse the built-in library.",
                "  - Bright Spark: flashcards organised by topic (37 categories like Activities, Colours, Numbers).",
                "  - High Flyer: word lists and images organised by Level / Unit.",
                "  - Switch between Flashcards / Words to filter by type.",
                "  - Pick a category or unit, then click Use this material.",
                "Manually Type-in tab: type or import your own items.",
                "  - Type a word and press Enter to add it.",
                "  - Click Import to load a .txt file (one numbered word per line, e.g. 1. apple).",
                "  - Click Folder to load images from a folder.",
            ]),
            ("How to Play", [
                "Look carefully at the target answers (shown large during the intro).",
                "Watch the cups shuffle.",
                "Click the correct cup(s). In multi-answer mode, pick all targets.",
                "Get them all right to score 1 point. Reveal shows answer cards.",
            ]),
            ("Quick Actions", [
                "Scoreboard: Same Again replays with the same items.",
                "Adjust returns to settings to tweak parameters.",
                "Exit button (top-right) quits the game at any time.",
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
