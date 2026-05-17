import pygame
import random
import os
from game.animations import Cup, AnimationManager
from game.icons import draw_check, draw_cross, draw_eye
from game.ui_components import (
    get_font, Button,
    BG_COLOR, BLACK, WHITE, CANDY_GREEN, CANDY_PINK, CANDY_BLUE,
    DARK_GRAY, SCREEN_W, SCREEN_H
)


class ShellGame:
    def __init__(self, screen, settings):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.settings = settings
        self.num_cups = settings["num_cups"]
        self.num_rounds = settings["num_rounds"]
        self.swap_duration = settings["swap_duration"]
        self.items = settings["items"]

        self.cups = []
        self.anim = AnimationManager()
        self.state = "init"
        self.current_round = 0
        self.score = 0
        self.target_cup = None
        self.target_content = None
        self.target_hint = ""
        self.selected_cup = None
        self.result_timer = 0
        self.show_result = False
        self.result_correct = False
        self.next_btn = None

        self._setup_cups()
        self._prepare_round()

    def _setup_cups(self):
        self.cups = []
        cup_w = min(110, (SCREEN_W - 200) // self.num_cups)
        cup_h = int(cup_w * 1.4)
        spacing = cup_w + 30
        total_width = self.num_cups * cup_w + (self.num_cups - 1) * 30
        start_x = (SCREEN_W - total_width) // 2 + cup_w // 2
        y = SCREEN_H // 2 + 40

        for i in range(self.num_cups):
            x = start_x + i * spacing
            cup = Cup(x, y, cup_w, cup_h)
            self.cups.append(cup)

    def _prepare_round(self):
        if self.current_round >= self.num_rounds:
            self.state = "finished"
            return

        # 重置杯子到初始位置
        self._setup_cups()

        # 从题库随机选一个作为本轮目标
        if self.items:
            target_item = random.choice(self.items)
        else:
            target_item = {"type": "text", "content": "?", "hint": ""}

        self.target_content = target_item["content"]
        self.target_hint = target_item.get("hint", "")

        # 随机选一个目标杯，把内容放进去
        target_idx = random.randint(0, self.num_cups - 1)
        self.target_cup = self.cups[target_idx]
        self.target_cup.ball_type = target_item["type"]
        if target_item["type"] == "image":
            try:
                img = pygame.image.load(target_item["content"])
                self.target_cup.ball_content = img
            except:
                self.target_cup.ball_type = "text"
                self.target_cup.ball_content = target_item["content"]
        else:
            self.target_cup.ball_content = target_item["content"]

        # 其他杯子保持空 (ball_content 为 None)

        # 动画：先全部升起展示球的位置，然后放下，然后交换
        self.state = "showing"
        self.anim = AnimationManager()
        self.anim.add_lift(self.cups, 400, 140)
        self.anim.add_pause(1200)
        self.anim.add_lower(self.cups, 400)
        self.anim.add_pause(300)

        num_swaps = self.num_cups + random.randint(2, 5)
        for _ in range(num_swaps):
            a, b = random.sample(range(self.num_cups), 2)
            self.anim.add_swap(self.cups[a], self.cups[b], self.swap_duration)
            self.anim.add_pause(80)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {"score": self.score, "total": self.current_round, "quit": True}
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event.pos)

            self._update(dt)
            self._draw()
            pygame.display.flip()

            if self.state == "finished":
                return {"score": self.score, "total": self.num_rounds, "quit": False}

        return {"score": self.score, "total": self.current_round, "quit": True}

    def _handle_click(self, pos):
        if self.state == "guessing":
            for cup in self.cups:
                cup_rect = pygame.Rect(
                    cup.x - cup.width // 2, cup.y, cup.width, cup.height
                )
                if cup_rect.collidepoint(pos):
                    self.selected_cup = cup
                    self.result_correct = (cup == self.target_cup)
                    if self.result_correct:
                        self.score += 1
                    self.state = "revealing"
                    self.anim = AnimationManager()
                    self.anim.add_lift([self.target_cup], 350, 140)
                    if not self.result_correct:
                        self.anim.add_pause(400)
                        self.anim.add_lift([cup], 350, 140)
                    self.anim.add_pause(1800)
                    break

        elif self.state == "result_shown":
            if self.next_btn and self.next_btn.is_clicked(pos, True):
                self.current_round += 1
                self._prepare_round()

    def _update(self, dt):
        self.anim.update(dt)
        mouse_pos = pygame.mouse.get_pos()
        if self.next_btn:
            self.next_btn.update(mouse_pos)

        if self.state == "showing" and self.anim.done:
            self.state = "guessing"

        elif self.state == "revealing" and self.anim.done:
            # 揭晓完成后等待玩家点击按钮
            self.state = "result_shown"
            is_last = self.current_round + 1 >= self.num_rounds
            btn_text = "查看结果" if is_last else "下一轮"
            self.next_btn = Button(
                SCREEN_W // 2 - 100, SCREEN_H - 80, 200, 55,
                btn_text, CANDY_GREEN, BLACK, 28
            )

    def _draw(self):
        self.screen.fill(BG_COLOR)

        # Round info
        info_font = get_font(28)
        round_text = info_font.render(
            f"第 {self.current_round + 1}/{self.num_rounds} 轮    得分: {self.score}",
            True, BLACK
        )
        self.screen.blit(round_text, (SCREEN_W // 2 - round_text.get_width() // 2, 20))

        if self.state == "guessing":
            prompt_font = get_font(34)
            if self.target_hint:
                prompt = f"请找到: {self.target_hint}"
            elif self.target_content is not None:
                display = self.target_content if isinstance(self.target_content, str) else "[图片]"
                prompt = f"请找到: {display}"
            else:
                prompt = "请找到目标!"
            prompt_surf = prompt_font.render(prompt, True, CANDY_PINK)
            self.screen.blit(prompt_surf, (SCREEN_W // 2 - prompt_surf.get_width() // 2, 70))

            hint_font = get_font(22)
            hint = hint_font.render("点击你认为藏着目标的杯子", True, DARK_GRAY)
            self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 60))

        elif self.state in ("revealing", "result_shown"):
            result_font = get_font(38)
            if self.result_correct:
                result_text = result_font.render("答对了! 太棒了!", True, CANDY_GREEN)
            else:
                result_text = result_font.render("没猜对, 看看正确位置~", True, CANDY_PINK)
            tx = SCREEN_W // 2 - result_text.get_width() // 2
            self.screen.blit(result_text, (tx, 70))
            # 画图标
            icon_x = tx - 35
            icon_y = 70 + result_text.get_height() // 2
            if self.result_correct:
                draw_check(self.screen, icon_x, icon_y, 24, CANDY_GREEN)
            else:
                draw_cross(self.screen, icon_x, icon_y, 24, CANDY_PINK)

            if self.state == "result_shown" and self.next_btn:
                self.next_btn.draw(self.screen)

        elif self.state == "showing":
            show_font = get_font(28)
            show_text = show_font.render("仔细看好目标在哪个杯子下面!", True, DARK_GRAY)
            tx = SCREEN_W // 2 - show_text.get_width() // 2
            self.screen.blit(show_text, (tx, 70))
            draw_eye(self.screen, tx - 25, 70 + show_text.get_height() // 2, 20, DARK_GRAY)

        # 绘制杯子
        for cup in self.cups:
            show = (self.state == "showing" and cup.lifted) or \
                   (self.state in ("revealing", "result_shown") and cup.lifted)
            cup.draw(self.screen, show_ball=show)
