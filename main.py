import pygame
import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

from game.ui_components import SCREEN_W, SCREEN_H, BG_COLOR
from game.settings import SettingsScreen
from game.shell_game import ShellGame
from game.scoreboard import Scoreboard


def main():
    pygame.init()
    pygame.display.set_caption("Shell Cup Game")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    last_settings = None
    skip_settings = False  # set true to skip Settings screen and reuse last_settings

    while True:
        if skip_settings and last_settings is not None:
            settings = last_settings
            skip_settings = False
        else:
            settings_screen = SettingsScreen(screen, initial_settings=last_settings)
            settings = settings_screen.run()
            if settings is None:
                break
            last_settings = settings

        game = ShellGame(screen, settings)
        result = game.run()
        if result.get("quit"):
            break

        scoreboard = Scoreboard(screen, result)
        action = scoreboard.run()
        if action == "quit":
            break
        elif action == "replay":
            # Skip Settings, go straight back into ShellGame with same config
            skip_settings = True
        # action == "adjust": fall through and re-show Settings with last_settings

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
