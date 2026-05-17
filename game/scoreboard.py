import pygame
from game.icons import draw_star, draw_cross
from game.ui_components import (
    Button, get_font,
    BG_COLOR, BLACK, CANDY_GREEN, CANDY_PINK, CANDY_BLUE,
    CANDY_YELLOW, CANDY_PURPLE, DARK_GRAY, SCREEN_W, SCREEN_H
)


class Scoreboard:
    def __init__(self, screen, result):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.score = result["score"]
        self.total = result["total"]
        self.ratio = self.score / max(1, self.total)

        self.replay_btn = Button(SCREEN_W // 2 - 220, SCREEN_H - 120, 200, 60, "再玩一次", CANDY_GREEN, BLACK, 30)
        self.quit_btn = Button(SCREEN_W // 2 + 20, SCREEN_H - 120, 200, 60, "退出游戏", CANDY_PINK, BLACK, 30)

    def run(self):
        while True:
            dt = self.clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            self.replay_btn.update(mouse_pos)
            self.quit_btn.update(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.replay_btn.is_clicked(event.pos, True):
                        return "replay"
                    if self.quit_btn.is_clicked(event.pos, True):
                        return "quit"

            self._draw()
            pygame.display.flip()

    def _draw(self):
        self.screen.fill(BG_COLOR)

        title_font = get_font(44)
        title = title_font.render("游戏结束!", True, CANDY_PURPLE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))

        score_font = get_font(60)
        score_text = score_font.render(f"{self.score} / {self.total}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_W // 2 - score_text.get_width() // 2, 200))

        msg = self._get_encouragement()
        msg_font = get_font(32)
        msg_surf = msg_font.render(msg, True, CANDY_GREEN if self.ratio >= 0.5 else CANDY_PINK)
        self.screen.blit(msg_surf, (SCREEN_W // 2 - msg_surf.get_width() // 2, 320))

        bar_w = 400
        bar_h = 30
        bar_x = SCREEN_W // 2 - bar_w // 2
        bar_y = 400
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=15)
        fill_w = int(bar_w * self.ratio)
        if fill_w > 0:
            color = CANDY_GREEN if self.ratio >= 0.7 else CANDY_YELLOW if self.ratio >= 0.4 else CANDY_PINK
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_w, bar_h), border_radius=15)

        star_count = self._get_star_count()
        star_size = 32
        total_w = star_count * (star_size * 2 + 10) - 10
        star_x = SCREEN_W // 2 - total_w // 2 + star_size
        star_y = 475
        color = CANDY_YELLOW if star_count > 0 else CANDY_PINK
        for i in range(max(1, star_count)):
            draw_star(self.screen, star_x + i * (star_size * 2 + 10), star_y, star_size, color)

        self.replay_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

    def _get_encouragement(self):
        if self.ratio >= 0.9:
            return "太厉害了！你是猜杯子大师！"
        elif self.ratio >= 0.7:
            return "非常棒！眼力很好哦！"
        elif self.ratio >= 0.5:
            return "不错不错，继续加油！"
        elif self.ratio >= 0.3:
            return "别灰心，多练习就会更好！"
        else:
            return "加油！下次一定能猜对更多！"

    def _get_star_count(self):
        if self.ratio >= 0.9:
            return 3
        elif self.ratio >= 0.7:
            return 2
        elif self.ratio >= 0.4:
            return 1
        else:
            return 0
