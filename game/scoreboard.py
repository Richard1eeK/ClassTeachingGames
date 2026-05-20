import pygame
import math

from game import theme as T
from game.theme import SCREEN_W, SCREEN_H
from game.icons import draw_star, draw_cross, draw_replay, draw_door, draw_gear
from game.animations import ease_out_back, ease_out_elastic
from game.effects import EffectsManager
from game.decorations import (
    get_wood_background, draw_parchment_card, draw_wood_plank,
    make_floating_decorations, update_floating_decorations,
    draw_floating_decorations,
)
from game.ui_components import (
    Button, get_font, render_text_outlined, WoodSign,
)


class Scoreboard:
    def __init__(self, screen, result):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.score = result["score"]
        self.total = result["total"]
        self.ratio = self.score / max(1, self.total)

        # Three buttons: Same Again (replay) / Adjust Settings / Quit
        btn_w = 230
        btn_h = 64
        gap = 20
        total_w = btn_w * 3 + gap * 2
        start_x = SCREEN_W // 2 - total_w // 2
        btn_y = SCREEN_H - 110

        self.replay_btn = Button(start_x, btn_y, btn_w, btn_h,
                                 "Same Again", T.SV_BLUE, T.TEXT_LIGHT,
                                 T.FONT_HEADING, icon=draw_replay)
        self.adjust_btn = Button(start_x + btn_w + gap, btn_y, btn_w, btn_h,
                                 "Adjust", T.SV_GREEN, T.TEXT_LIGHT,
                                 T.FONT_HEADING, icon=draw_gear)
        self.quit_btn = Button(start_x + (btn_w + gap) * 2, btn_y, btn_w, btn_h,
                               "Quit", T.SV_RED, T.TEXT_LIGHT,
                               T.FONT_HEADING, icon=draw_door)

        self.title_sign = WoodSign(SCREEN_W // 2 - 240, 60, 480, 80,
                                   "Game Over!", font_size=T.FONT_TITLE)

        self.decorations = make_floating_decorations(20, SCREEN_W, SCREEN_H, seed=37)

        self.effects = EffectsManager()
        self.elapsed = 0.0
        # animation timing constants (ms)
        self.score_anim_start = 350
        self.score_anim_dur = 700
        self.bar_anim_start = 1100
        self.bar_anim_dur = 800
        self.star_anim_start = 1900
        self.star_step = 220
        self.star_anim_dur = 600

        self._stars_burst = [False, False, False]

        self.target_star_count = self._get_star_count()

    def run(self):
        while True:
            dt = self.clock.tick(60)
            self.elapsed += dt
            mouse_pos = pygame.mouse.get_pos()
            self.replay_btn.update(mouse_pos, dt)
            self.adjust_btn.update(mouse_pos, dt)
            self.quit_btn.update(mouse_pos, dt)
            self.effects.update(dt)
            update_floating_decorations(self.decorations, dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.replay_btn.is_clicked(event.pos, True):
                        return "replay"
                    if self.adjust_btn.is_clicked(event.pos, True):
                        return "adjust"
                    if self.quit_btn.is_clicked(event.pos, True):
                        return "quit"

            self._spawn_star_bursts()
            self._draw()
            pygame.display.flip()

    def _spawn_star_bursts(self):
        for i in range(self.target_star_count):
            t_start = self.star_anim_start + i * self.star_step
            if self.elapsed >= t_start + self.star_anim_dur * 0.55 and not self._stars_burst[i]:
                star_x, star_y = self._star_position(i)
                self.effects.burst_stars(star_x, star_y, count=10, color=T.GOLD)
                self._stars_burst[i] = True

    def _star_position(self, i):
        star_size = 36
        spacing = star_size * 2 + 22
        total_w = self.target_star_count * spacing - (spacing - star_size * 2)
        if self.target_star_count == 0:
            total_w = star_size * 2
        start_x = SCREEN_W // 2 - total_w // 2 + star_size
        return start_x + i * spacing, 510

    def _draw(self):
        bg = get_wood_background(SCREEN_W, SCREEN_H)
        self.screen.blit(bg, (0, 0))
        draw_floating_decorations(self.screen, self.decorations, SCREEN_W, SCREEN_H)

        self.title_sign.draw(self.screen)

        # Center parchment card
        card_rect = pygame.Rect(SCREEN_W // 2 - 360, 170, 720, 380)
        draw_parchment_card(self.screen, card_rect)

        self._draw_score(card_rect)
        self._draw_message(card_rect)
        self._draw_progress_bar(card_rect)
        self._draw_stars()

        self.effects.draw(self.screen)

        self.replay_btn.draw(self.screen)
        self.adjust_btn.draw(self.screen)
        self.quit_btn.draw(self.screen)

    def _draw_score(self, card_rect):
        # Score number with spring entry
        t_raw = (self.elapsed - self.score_anim_start) / self.score_anim_dur
        t = max(0.0, min(1.0, t_raw))
        if t_raw < 0:
            scale = 0.0
        else:
            scale = ease_out_back(t)

        if scale <= 0.01:
            return
        font_size = int(72 * scale)
        if font_size < 8:
            return
        text_str = f"{self.score} / {self.total}"
        # render with outlined text (bigger outline for impact)
        from game.ui_components import render_text_outlined
        score_surf = render_text_outlined(
            text_str, font_size, T.GOLD,
            outline_color=T.WOOD_DARK, outline_w=3, bold=True,
        )
        x = card_rect.centerx - score_surf.get_width() // 2
        y = card_rect.y + 40
        self.screen.blit(score_surf, (x, y))

    def _draw_message(self, card_rect):
        if self.elapsed < self.score_anim_start + 200:
            return
        msg = self._get_encouragement()
        color = T.SV_GREEN_DARK if self.ratio >= 0.5 else T.SV_RED_DARK
        msg_surf = render_text_outlined(
            msg, T.FONT_HEADING, color,
            outline_color=T.PARCHMENT, outline_w=1, bold=True,
        )
        self.screen.blit(msg_surf, (
            card_rect.centerx - msg_surf.get_width() // 2,
            card_rect.y + 150,
        ))

    def _draw_progress_bar(self, card_rect):
        bar_w = 480
        bar_h = 26
        bar_x = card_rect.centerx - bar_w // 2
        bar_y = card_rect.y + 230

        # frame
        frame = pygame.Rect(bar_x - 4, bar_y - 4, bar_w + 8, bar_h + 8)
        pygame.draw.rect(self.screen, T.WOOD_DARK, frame, border_radius=15)
        pygame.draw.rect(self.screen, T.WOOD_BROWN, frame, 2, border_radius=15)
        pygame.draw.rect(self.screen, T.PARCHMENT_DARK,
                         (bar_x, bar_y, bar_w, bar_h), border_radius=12)

        # fill
        t_raw = (self.elapsed - self.bar_anim_start) / self.bar_anim_dur
        t = max(0.0, min(1.0, t_raw))
        if t > 0:
            fill_w = int(bar_w * self.ratio * t)
            if fill_w > 0:
                if self.ratio >= 0.7:
                    color = T.SV_GREEN
                    color_dark = T.SV_GREEN_DARK
                elif self.ratio >= 0.4:
                    color = T.GOLD
                    color_dark = T.GOLD_DARK
                else:
                    color = T.SV_RED
                    color_dark = T.SV_RED_DARK
                pygame.draw.rect(self.screen, color_dark,
                                 (bar_x, bar_y, fill_w, bar_h), border_radius=12)
                # top highlight
                pygame.draw.rect(self.screen, color,
                                 (bar_x + 2, bar_y + 3, max(0, fill_w - 4), bar_h // 2),
                                 border_radius=10)

                # animated shimmer sweeping across the bar
                sweep_period = 1500
                sweep_t = (self.elapsed % sweep_period) / sweep_period
                sweep_x = bar_x + int(sweep_t * (bar_w + 60)) - 30
                shimmer = pygame.Surface((50, bar_h), pygame.SRCALPHA)
                for sx in range(50):
                    alpha = int(80 * math.sin(sx / 50 * math.pi))
                    pygame.draw.line(shimmer, (255, 255, 255, alpha),
                                     (sx, 0), (sx, bar_h))
                shimmer_clip = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
                shimmer_clip.blit(shimmer, (sweep_x - bar_x, 0))
                # mask to fill area
                mask = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255),
                                 (0, 0, fill_w, bar_h), border_radius=12)
                shimmer_clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                self.screen.blit(shimmer_clip, (bar_x, bar_y))

    def _draw_stars(self):
        if self.target_star_count == 0:
            # show 1 grey star
            star_x, star_y = self._star_position(0)
            self.target_star_count_for_layout = 1
            draw_star(self.screen, star_x, star_y, 30, T.PARCHMENT_DARK,
                      filled=True, outline=T.WOOD_BROWN)
            return

        for i in range(self.target_star_count):
            t_start = self.star_anim_start + i * self.star_step
            t_raw = (self.elapsed - t_start) / self.star_anim_dur
            t = max(0.0, min(1.0, t_raw))
            if t <= 0:
                continue
            # elastic pop
            scale = ease_out_elastic(t)
            size = max(1, int(36 * max(0, scale)))
            star_x, star_y = self._star_position(i)
            # gold glow behind
            if t > 0.4:
                glow_r = int(size * 1.4)
                glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                for k in range(5):
                    alpha = int(40 * (1 - k / 5))
                    pygame.draw.circle(glow,
                                       (T.GOLD_LIGHT[0], T.GOLD_LIGHT[1], T.GOLD_LIGHT[2], alpha),
                                       (glow_r, glow_r), glow_r - k * 4)
                self.screen.blit(glow, (star_x - glow_r, star_y - glow_r))
            draw_star(self.screen, star_x, star_y, size, T.GOLD,
                      filled=True, outline=T.WOOD_DARK)

    def _get_encouragement(self):
        if self.ratio >= 0.9:
            return "Amazing! You're a Shell Cup Master!"
        elif self.ratio >= 0.7:
            return "Great job! Sharp eyes!"
        elif self.ratio >= 0.5:
            return "Not bad, keep it up!"
        elif self.ratio >= 0.3:
            return "Don't give up, practice makes perfect!"
        else:
            return "Keep trying, you'll get better!"

    def _get_star_count(self):
        if self.ratio >= 0.9:
            return 3
        elif self.ratio >= 0.7:
            return 2
        elif self.ratio >= 0.4:
            return 1
        else:
            return 0
