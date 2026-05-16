import pygame
import random
import os
from game.animations import Cup, AnimationManager
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

        self._setup_cups()
        self._prepare_round()

    def _setup_cups(self):
        self.cups = []
        total_width = self.num_cups * 100 + (self.num_cups - 1) * 40
        start_x = (SCREEN_W - total_width) // 2 + 50
        cup_w = min(100, (SCREEN_W - 200) // self.num_cups)
        cup_h = int(cup_w * 1.3)
        y = SCREEN_H // 2 + 20

        for i in range(self.num_cups):
            x = start_x + i * (cup_w + 40)
            cup = Cup(x, y, cup_w, cup_h, i)
            self.cups.append(cup)

    def _prepare_round(self):
        if self.current_round >= self.num_rounds:
            self.state = "finished"
            return

        available = self.items if self.items else [{"type": "text", "content": "?", "hint": ""}]
        chosen_items = random.sample(available, min(self.num_cups, len(available)))
        if len(chosen_items) < self.num_cups:
            while len(chosen_items) < self.num_cups:
                chosen_items.append(random.choice(available))

        random.shuffle(chosen_items)
        for i, cup in enumerate(self.cups):
            item = chosen_items[i]
            cup.ball_type = item["type"]
            if item["type"] == "image":
                try:
                    img = pygame.image.load(item["content"])
                    cup.ball_content = img
                except:
                    cup.ball_type = "text"
                    cup.ball_content = "?"
            else:
                cup.ball_content = item["content"]

        target_idx = random.randint(0, self.num_cups - 1)
        self.target_cup = self.cups[target_idx]
        self.target_content = chosen_items[target_idx]["content"]
        self.target_hint = chosen_items[target_idx].get("hint", "")

        self._setup_cups()
        for i, cup in enumerate(self.cups):
            item = chosen_items[i]
            cup.ball_type = item["type"]
            if item["type"] == "image":
                try:
                    img = pygame.image.load(item["content"])
                    cup.ball_content = img
                except:
                    cup.ball_type = "text"
                    cup.ball_content = "?"
            else:
                cup.ball_content = item["content"]

        self.target_cup = self.cups[target_idx]
        self.state = "showing"
        self.anim = AnimationManager()
        self.anim.add_lift(self.cups, 500, 130)
        self.anim.add_pause(1500)
        self.anim.add_lower(self.cups, 500)
        self.anim.add_pause(300)

        num_swaps = self.num_cups + random.randint(2, 5)
        for _ in range(num_swaps):
            a, b = random.sample(range(self.num_cups), 2)
            self.anim.add_swap(self.cups[a], self.cups[b], self.swap_duration)
            self.anim.add_pause(100)

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
                    self.anim.add_lift([cup], 400, 130)
                    if not self.result_correct:
                        self.anim.add_pause(500)
                        self.anim.add_lift([self.target_cup], 400, 130)
                    self.anim.add_pause(1500)
                    break

    def _update(self, dt):
        self.anim.update(dt)

        if self.state == "showing" and self.anim.done:
            self.state = "guessing"

        elif self.state == "revealing" and self.anim.done:
            self.result_timer += dt
            if self.result_timer > 500:
                self.result_timer = 0
                self.current_round += 1
                for cup in self.cups:
                    cup.lifted = False
                    cup.lift_offset = 0
                self._prepare_round()

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
            else:
                display = self.target_content if isinstance(self.target_content, str) else "[图片]"
                prompt = f"请找到: {display}"
            prompt_surf = prompt_font.render(prompt, True, CANDY_PINK)
            self.screen.blit(prompt_surf, (SCREEN_W // 2 - prompt_surf.get_width() // 2, 70))

            hint_font = get_font(22)
            hint = hint_font.render("👆 点击你认为正确的杯子", True, DARK_GRAY)
            self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 60))

        elif self.state == "revealing":
            result_font = get_font(38)
            if self.result_correct:
                result_text = result_font.render("✓ 答对了！太棒了！", True, CANDY_GREEN)
            else:
                result_text = result_font.render("✗ 没猜对，看看正确位置~", True, CANDY_PINK)
            self.screen.blit(result_text, (SCREEN_W // 2 - result_text.get_width() // 2, 70))

        elif self.state == "showing":
            show_font = get_font(28)
            show_text = show_font.render("👀 仔细看好球的位置...", True, DARK_GRAY)
            self.screen.blit(show_text, (SCREEN_W // 2 - show_text.get_width() // 2, 70))

        show_ball = self.state == "showing" and any(c.lifted for c in self.cups)
        for cup in self.cups:
            cup.draw(self.screen, show_ball=(show_ball or (self.state == "revealing" and cup.lifted)))
