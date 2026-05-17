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

    while True:
        settings_screen = SettingsScreen(screen)
        settings = settings_screen.run()
        if settings is None:
            break

        game = ShellGame(screen, settings)
        result = game.run()
        if result.get("quit"):
            break

        scoreboard = Scoreboard(screen, result)
        action = scoreboard.run()
        if action == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
