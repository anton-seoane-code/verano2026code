import pygame
from constants import *
from snake import Snake
from food import RedFood, BlueBonus

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2006")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "start"
        self.score = 0
        self.high_score = 0
        self.move_timer = 0
        self.snake = Snake()
        self.red_food = RedFood()
        self.blue_bonus = BlueBonus()
        self.font_large = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def run(self):
        while self.running:
            if self.state == "start":
                self._start_screen()
            elif self.state == "playing":
                self._game_loop()
            elif self.state == "game_over":
                self._game_over_screen()
        pygame.quit()

    def _start_game(self):
        self.score = 0
        self.move_timer = 0
        self.snake = Snake()
        self.red_food = RedFood()
        self.blue_bonus = BlueBonus()

    def _game_loop(self):
        pass

    def _start_screen(self):
        pass

    def _game_over_screen(self):
        pass
