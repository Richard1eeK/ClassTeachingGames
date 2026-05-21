import pygame
import random

from game import theme as T
from game.theme import SCREEN_W, SCREEN_H
from game.animations import Cup, AnimationManager, IntroBall
from game.icons import draw_check, draw_cross, draw_eye, draw_star, draw_heart, draw_door
from game.effects import EffectsManager
from game.decorations import (
    get_wood_background, draw_parchment_card, draw_wood_plank,
    draw_speech_bubble, make_floating_decorations,
    update_floating_decorations, draw_floating_decorations,
)
from game.ui_components import (
    Button, get_font, render_text_outlined,
)


class ShellGame:
    def __init__(self, screen, settings):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.settings = settings
        self.num_cups = settings["num_cups"]
        self.num_rounds = settings["num_rounds"]
        self.swap_duration = settings["swap_duration"]
        self.speed_level = settings.get("speed_level", 2)
        self.items = settings["items"]

        self.cups = []
        self.anim = AnimationManager()
        self.effects = EffectsManager()
        self.state = "init"
        self.current_round = 0
        self.score = 0
        self.target_cup = None
        self.target_content = None
        self.target_hint = ""
        self.target_type = "text"
        self.selected_cup = None
        self.show_result = False
        self.result_correct = False
        self.next_btn = None
        self.intro_ball = None
        self.intro_active = False  # True while showing/flying the big ball

        # HUD Exit button (placed during _draw_hud now needs Button object for clicks)
        self.exit_btn = Button(
            SCREEN_W - 116, 22, 86, 36,
            "Exit", T.SV_RED, T.TEXT_LIGHT, T.FONT_CAPTION, icon=draw_door,
        )

        # Background floats and bubble bob
        self.decorations = make_floating_decorations(12, SCREEN_W, SCREEN_H, seed=23)
        self.bubble_phase = 0.0

        self._setup_cups()
        self._prepare_round()

    def _setup_cups(self):
        self.cups = []
        cup_w = min(96, (SCREEN_W - 220) // self.num_cups)
        cup_h = int(cup_w * 1.25)
        gap = 24
        spacing = cup_w + gap
        total_width = self.num_cups * cup_w + (self.num_cups - 1) * gap
        start_x = (SCREEN_W - total_width) // 2 + cup_w // 2
        y = SCREEN_H // 2 + 38

        for i in range(self.num_cups):
            x = start_x + i * spacing
            cup = Cup(x, y, cup_w, cup_h)
            self.cups.append(cup)

    def _prepare_round(self):
        if self.current_round >= self.num_rounds:
            self.state = "finished"
            return

        self._setup_cups()

        if self.items:
            target_item = random.choice(self.items)
        else:
            target_item = {"type": "text", "content": "?", "hint": ""}

        self.target_content = target_item["content"]
        self.target_hint = target_item.get("hint", "")
        self.target_type = target_item["type"]

        target_idx = random.randint(0, self.num_cups - 1)
        self.target_cup = self.cups[target_idx]
        self.target_cup.ball_type = target_item["type"]
        loaded_image = None
        if target_item["type"] == "image":
            try:
                img = pygame.image.load(target_item["content"])
                self.target_cup.ball_content = img
                loaded_image = img
            except Exception:
                self.target_cup.ball_type = "text"
                self.target_cup.ball_content = target_item["content"]
                self.target_type = "text"
        else:
            self.target_cup.ball_content = target_item["content"]

        self.state = "intro"
        self.intro_active = True
        self.anim = AnimationManager()
        self.next_btn = None

        # Build the intro ball
        ball_radius = min(self.target_cup.width // 3, 35)
        intro_content = loaded_image if self.target_type == "image" else self.target_content
        self.intro_ball = IntroBall(
            x=SCREEN_W // 2,
            y=SCREEN_H // 2 - 60,
            base_radius=ball_radius,
            content=intro_content,
            content_type=self.target_type,
        )
        self.intro_ball.scale = 2.8
        self.intro_ball.alpha = 0.0
        self.intro_ball.visible = False

        # Phase 1: lift cups so empty bottoms show, then show big ball
        self.anim.add_lift(self.cups, 300, 140)
        self.anim.add_intro_show(self.intro_ball, duration_ms=2000, fade_in_ms=400)
        # Phase 2: fly ball into target cup, then lower cups
        self.anim.add_intro_fly(self.intro_ball, self.target_cup, duration_ms=850,
                                end_scale=1.0, arc_height=160)
        self.anim.add_pause(150)
        self.anim.add_lower(self.cups, 320)
        self.anim.add_pause(250)

        # Phase 3: original showing/swap sequence (unchanged behavior)
        if self.speed_level >= 5:
            num_scrambles = self.num_cups * 3 + random.randint(5, 10)
            for _ in range(num_scrambles):
                self.anim.add_scramble(self.cups, self.swap_duration)
                self.anim.add_pause(25)
        elif self.speed_level >= 4:
            num_swaps = self.num_cups * 2 + random.randint(3, 7)
            for _ in range(num_swaps):
                a, b = random.sample(range(self.num_cups), 2)
                self.anim.add_swap(self.cups[a], self.cups[b], self.swap_duration)
                self.anim.add_pause(50)
        else:
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
                # 'finished' can be reached either by completing all rounds
                # or by clicking Exit mid-game; current_round reflects how
                # many rounds were actually completed.
                completed = self.current_round
                if completed >= self.num_rounds:
                    completed = self.num_rounds
                return {"score": self.score, "total": completed, "quit": False}

        return {"score": self.score, "total": self.current_round, "quit": True}

    def _handle_click(self, pos):
        # Exit button is reachable from any active state
        if self.state != "finished" and self.exit_btn.is_clicked(pos, True):
            # If the user was on the result screen, count that round as completed.
            if self.state == "result_shown":
                self.current_round += 1
            self.state = "finished"
            return

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
                    if self.result_correct:
                        # lift the chosen (== target) cup with glow
                        self.anim.add_lift([self.target_cup], 350, 140)
                        self.anim.add_glow(self.target_cup, 1200, peak=1.0)
                        self.anim.add_pause(1400)
                        self.effects.burst_correct(cup.x, cup.y + 20)
                        self.effects.add_text(cup.x, cup.y - 10, "+1 ⭐", T.GOLD_DARK, T.FONT_HEADING)
                        self.effects.add_flash(T.GOLD_LIGHT, alpha=80)
                    else:
                        # shake wrong, then reveal correct
                        self.anim.add_shake(cup, 500, intensity=12)
                        self.anim.add_lift([cup], 250, 140)
                        self.anim.add_pause(300)
                        self.anim.add_lift([self.target_cup], 350, 140)
                        self.anim.add_glow(self.target_cup, 1200, peak=0.7)
                        self.anim.add_pause(1300)
                        self.effects.burst_wrong(cup.x, cup.y + 20)
                        self.effects.add_shake(amount=8, duration=240)
                    break

        elif self.state == "result_shown":
            if self.next_btn and self.next_btn.is_clicked(pos, True):
                self.current_round += 1
                self._prepare_round()

    def _update(self, dt):
        self.anim.update(dt)
        self.effects.update(dt)
        update_floating_decorations(self.decorations, dt)
        self.bubble_phase += dt * 0.003

        mouse_pos = pygame.mouse.get_pos()
        self.exit_btn.update(mouse_pos, dt)
        if self.next_btn:
            self.next_btn.update(mouse_pos, dt)

        if self.state == "intro" and self.anim.done:
            self.state = "showing"
            self.intro_active = False
        elif self.state == "showing" and self.anim.done:
            self.state = "guessing"

        elif self.state == "revealing" and self.anim.done:
            self.state = "result_shown"
            is_last = self.current_round + 1 >= self.num_rounds
            btn_text = "View Results" if is_last else "Next Round"
            self.next_btn = Button(
                SCREEN_W // 2 - 100, SCREEN_H - 76, 200, 50,
                btn_text, T.SV_GREEN, T.TEXT_LIGHT, T.FONT_HEADING,
            )

    def _draw(self):
        bg = get_wood_background(SCREEN_W, SCREEN_H)
        self.screen.blit(bg, (0, 0))
        draw_floating_decorations(self.screen, self.decorations, SCREEN_W, SCREEN_H)

        # Apply effect-based screen shake (offset everything below)
        sx, sy = self.effects.get_shake_offset()

        layer = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self._draw_hud(layer)
        self._draw_status(layer)
        self._draw_cups(layer)

        # Intro overlay: dim background + draw the big ball above cups
        if self.state == "intro" and self.intro_ball is not None:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((30, 18, 10, 120))
            layer.blit(overlay, (0, 0))
            # "Memorize this!" caption while ball is held large at center
            if self.intro_ball.scale > 1.4:
                cap = render_text_outlined(
                    "Memorize this!", T.FONT_HEADING, T.GOLD_LIGHT,
                    outline_color=T.WOOD_DARK, outline_w=2, bold=True,
                )
                cap.set_alpha(int(255 * self.intro_ball.alpha))
                layer.blit(cap, (
                    SCREEN_W // 2 - cap.get_width() // 2,
                    SCREEN_H // 2 - 60 - int(self.intro_ball.base_radius * self.intro_ball.scale) - 50,
                ))
            self.intro_ball.draw(layer)

        self.effects.draw(layer)

        self.screen.blit(layer, (sx, sy))

        if self.state == "result_shown" and self.next_btn:
            self.next_btn.draw(self.screen)

        # Exit button is always on top, untouched by screen shake
        self.exit_btn.draw(self.screen)

    def _draw_hud(self, surface):
        # Top wood plank with round + score
        bar = pygame.Rect(34, 14, SCREEN_W - 68, 48)
        draw_wood_plank(surface, bar, color=T.WOOD_BROWN, radius=T.RADIUS_MD)

        # Round dots (left)
        dot_x = bar.x + 24
        dot_y = bar.centery
        round_label = render_text_outlined(
            "Round", T.FONT_BODY, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True,
        )
        surface.blit(round_label, (dot_x, dot_y - round_label.get_height() // 2))
        dot_x += round_label.get_width() + 12
        dot_r = 7
        for i in range(self.num_rounds):
            color = T.GOLD if i < self.current_round else (
                T.GOLD_LIGHT if i == self.current_round else T.PARCHMENT_DARK
            )
            outline = T.WOOD_DARK
            if i == self.current_round and self.state != "finished":
                pygame.draw.circle(surface, T.GOLD_LIGHT, (dot_x, dot_y), dot_r + 3)
            pygame.draw.circle(surface, color, (dot_x, dot_y), dot_r)
            pygame.draw.circle(surface, outline, (dot_x, dot_y), dot_r, 2)
            dot_x += dot_r * 2 + 6

        # Score (right) — leave room for Exit button at far right
        score_text = render_text_outlined(
            f"Score: {self.score}", T.FONT_BODY, T.TEXT_LIGHT,
            outline_color=T.WOOD_DARK, outline_w=2, bold=True,
        )
        score_x = bar.right - score_text.get_width() - 150
        surface.blit(score_text, (score_x, bar.centery - score_text.get_height() // 2))
        # star icon to right of score
        draw_star(surface, score_x + score_text.get_width() + 18, bar.centery,
                  14, T.GOLD, outline=T.WOOD_DARK)

    def _draw_status(self, surface):
        # During intro, the big ball + caption take center stage; skip bubble
        if self.state == "intro":
            return

        # Speech bubble for status, bobbing slightly
        import math
        bob = int(math.sin(self.bubble_phase) * 3)
        bubble_w = 430
        bubble_h = 74
        bubble_rect = pygame.Rect(
            SCREEN_W // 2 - bubble_w // 2,
            86 + bob,
            bubble_w, bubble_h,
        )

        if self.state == "showing":
            text = "Watch the cup that hides the target..."
            color = T.TEXT_BROWN
            draw_speech_bubble(surface, bubble_rect, fill=T.PARCHMENT,
                               border=T.WOOD_DARK, tail="bottom")
            draw_eye(surface, bubble_rect.x + 30, bubble_rect.centery, 18, T.TEXT_BROWN)
            text_surf = render_text_outlined(text, T.FONT_BODY, color,
                                              outline_color=T.PARCHMENT, outline_w=1, bold=True)
            surface.blit(text_surf, (
                bubble_rect.centerx - text_surf.get_width() // 2 + 16,
                bubble_rect.centery - text_surf.get_height() // 2,
            ))

        elif self.state == "guessing":
            if self.target_hint:
                text = f"Find: {self.target_hint}"
            elif self.target_content is not None:
                display = self.target_content if isinstance(self.target_content, str) else "[Image]"
                text = f"Find: {display}"
            else:
                text = "Find the target!"
            draw_speech_bubble(surface, bubble_rect, fill=T.PARCHMENT,
                               border=T.WOOD_DARK, tail="bottom")
            text_surf = render_text_outlined(text, T.FONT_BODY, T.SV_BLUE_DARK,
                                             outline_color=T.PARCHMENT, outline_w=1, bold=True)
            surface.blit(text_surf, (
                bubble_rect.centerx - text_surf.get_width() // 2,
                bubble_rect.centery - text_surf.get_height() // 2,
            ))

            hint = render_text_outlined(
                "Click the cup hiding the target",
                T.FONT_CAPTION, T.TEXT_MUTED,
                outline_color=T.CREAM_BG, outline_w=1, bold=False,
            )
            surface.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 50))

        elif self.state in ("revealing", "result_shown"):
            if self.result_correct:
                text = "Correct! Well done!"
                color = T.SV_GREEN_DARK
                bg_fill = T.PARCHMENT
            else:
                text = "Not quite — here's the right cup."
                color = T.SV_RED_DARK
                bg_fill = T.PARCHMENT
            draw_speech_bubble(surface, bubble_rect, fill=bg_fill,
                               border=T.WOOD_DARK, tail="bottom")
            text_surf = render_text_outlined(text, T.FONT_BODY, color,
                                             outline_color=T.PARCHMENT, outline_w=1, bold=True)
            tx = bubble_rect.centerx - text_surf.get_width() // 2 + 18
            ty = bubble_rect.centery - text_surf.get_height() // 2
            surface.blit(text_surf, (tx, ty))
            if self.result_correct:
                draw_check(surface, tx - 22, bubble_rect.centery, 18, T.SV_GREEN_DARK)
            else:
                draw_cross(surface, tx - 22, bubble_rect.centery, 18, T.SV_RED_DARK)

    def _draw_cups(self, surface):
        # Ground line under cups (subtle wood plank shelf)
        ground_y = self.cups[0].y + self.cups[0].height + 12 if self.cups else SCREEN_H - 120
        shelf_rect = pygame.Rect(72, ground_y, SCREEN_W - 144, 10)
        pygame.draw.rect(surface, T.WOOD_DARK, shelf_rect.move(3, 4))
        pygame.draw.rect(surface, T.WOOD_BROWN, shelf_rect)
        pygame.draw.rect(surface, T.WOOD_DARK, shelf_rect, 2)

        for cup in self.cups:
            show = (
                (self.state == "showing" and cup.lifted)
                or (self.state in ("revealing", "result_shown") and cup.lifted)
            )
            cup.draw(surface, show_ball=show)
