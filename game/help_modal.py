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
        self.scroll_offset: int = 0
        self._content_height: int = 0
        self.btn_rect: pygame.Rect = pygame.Rect(SCREEN_W - 96, 56, 46, 46)
        self.modal_rect: pygame.Rect = pygame.Rect(132, 76, 760, 616)
        self.lang_btn: Button = Button(self.modal_rect.right - 150, self.modal_rect.y + 24,
                                        92, 38, "中文", T.SV_BLUE, T.TEXT_LIGHT, T.FONT_CAPTION)
        self.close_btn: Button = Button(self.modal_rect.right - 50, self.modal_rect.y + 24,
                                         32, 38, "X", T.SV_RED, T.TEXT_LIGHT, T.FONT_CAPTION)
        # Scroll indicator
        self._scroll_hint_timer: float = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events when modal is open."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.open = False
            return
        if event.type == pygame.MOUSEWHEEL:
            content_area_h = self.modal_rect.height - 110
            max_scroll = max(0, self._content_height - content_area_h)
            self.scroll_offset = max(0, min(max_scroll,
                                            self.scroll_offset - event.y * 30))
            self._scroll_hint_timer = 1200
            return
        # macOS trackpad button 4/5 scroll
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            content_area_h = self.modal_rect.height - 110
            max_scroll = max(0, self._content_height - content_area_h)
            direction = 1 if event.button == 4 else -1
            self.scroll_offset = max(0, min(max_scroll,
                                            self.scroll_offset - direction * 30))
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        pos = event.pos
        if self.close_btn.is_clicked(pos, True):
            self.open = False
        elif self.lang_btn.is_clicked(pos, True):
            self.lang = "zh" if self.lang == "en" else "en"
            self.scroll_offset = 0

    def update(self, mouse_pos: Tuple[int, int], dt: int) -> None:
        """Update button hover states."""
        if self._scroll_hint_timer > 0:
            self._scroll_hint_timer -= dt
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
                ("游戏设置", [
                    "Answers：每轮正确答案数量（1~5）。",
                    "Cups：杯子总数（至少 Answers + 2）。",
                    "Rounds：游戏轮数（3~20）。",
                    "Speed：洗牌速度（Slow → Insane 共 5 档）。",
                ]),
                ("素材来源", [
                    "Resources 标签：浏览内置材料库。",
                    "  Bright Spark — 37 个词汇类别闪卡。",
                    "  High Flyer — 按 Level / Unit 组织的文字与图片。",
                    "  切换 Flashcards / Words 筛选类型。",
                    "  点击条目 → Use this material 即可加载。",
                    "Manually Type-in 标签：手动输入或导入。",
                    "  打字 + Enter 添加；Import 导入 .txt 词库；",
                    "  Folder 导入图片文件夹。",
                ]),
                ("怎么玩", [
                    "Intro 阶段认真看放大展示的目标答案。",
                    "观察杯子洗牌，点击正确的杯子。",
                    "多答案模式需选满全部目标后统一判定。",
                    "全部选对得 1 分，揭示阶段显示正确答案卡。",
                ]),
                ("快捷操作", [
                    "结算页 Same Again 用相同素材直接再玩。",
                    "Adjust 回到设置页调整参数后继续。",
                    "右上角 Exit 可随时退出当前游戏。",
                ]),
            ]
        return [
            ("Game Settings", [
                "Answers: correct targets per round (1–5).",
                "Cups: total cups (at least Answers + 2).",
                "Rounds: number of rounds (3–20).",
                "Speed: shuffle pace, 5 levels Slow → Insane.",
            ]),
            ("Materials", [
                "Resources tab: browse the built-in library.",
                "  Bright Spark — 37 topic-based flashcard sets.",
                "  High Flyer — words & images by Level / Unit.",
                "  Switch Flashcards / Words to filter by type.",
                "  Pick an entry → Use this material to load.",
                "Manually Type-in tab: type or import items.",
                "  Type + Enter to add; Import to load a .txt list.",
                "  Folder to load an image folder.",
            ]),
            ("How to Play", [
                "Study the target cards shown large during intro.",
                "Watch the cups shuffle, then click your guess.",
                "Multi-answer: pick all targets before judging.",
                "All correct = 1 point. Reveal shows answer cards.",
            ]),
            ("Quick Actions", [
                "Same Again replays with the same items.",
                "Adjust returns to Settings to tweak parameters.",
                "Exit (top-right) quits the game at any time.",
            ]),
        ]

    def _draw_sections(self, screen: pygame.Surface, x: int, y: int, max_w: int) -> None:
        """Draw help content sections with clipping and scroll."""
        content_area = pygame.Rect(
            self.modal_rect.x + 20, self.modal_rect.y + 90,
            self.modal_rect.width - 40, self.modal_rect.height - 110,
        )
        prev_clip = screen.get_clip()
        screen.set_clip(content_area)

        base_y = y - self.scroll_offset
        draw_y = base_y
        for section_title, lines in self._get_content():
            title = render_text_outlined(
                section_title, T.FONT_BODY, T.TEXT_DARK,
                outline_color=T.PARCHMENT, outline_w=1, bold=True,
            )
            screen.blit(title, (x, draw_y))
            draw_y += 28
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
                    screen.blit(surf, (x + 18, draw_y))
                    draw_y += 20
                draw_y += 1
            draw_y += 10

        self._content_height = draw_y - base_y + self.scroll_offset

        screen.set_clip(prev_clip)

        # Scroll indicator
        content_h = content_area.height
        if self._content_height > content_h:
            bar_h = max(30, int(content_h * content_h / self._content_height))
            max_scroll = self._content_height - content_h
            bar_y = content_area.y + int(
                (content_h - bar_h) * self.scroll_offset / max_scroll
            ) if max_scroll > 0 else content_area.y
            bar_rect = pygame.Rect(content_area.right - 8, bar_y, 6, bar_h)
            alpha = min(180, max(60, int(self._scroll_hint_timer / 4))) if self._scroll_hint_timer > 0 else 80
            bar_surf = pygame.Surface((6, bar_h), pygame.SRCALPHA)
            bar_surf.fill((*T.WOOD_DARK, alpha))
            screen.blit(bar_surf, (bar_rect.x, bar_rect.y))

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
