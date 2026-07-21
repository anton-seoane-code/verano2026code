import pygame
import pickle
import os
from constants import *

class Scoreboard:
    def __init__(self):
        self.scores = []
        self.load()

    def load(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, 'rb') as f:
                    self.scores = pickle.load(f)
            except:
                self.scores = []
        if not self.scores:
            self.scores = [("PAC", 10000, 1)]

    def save(self):
        with open(HIGH_SCORE_FILE, 'wb') as f:
            pickle.dump(self.scores[:5], f)

    def add_score(self, name, score, level):
        self.scores.append((name.upper()[:3], score, level))
        self.scores.sort(key=lambda x: -x[1])
        self.scores = self.scores[:5]
        self.save()
        return self.is_high_score(score)

    def is_high_score(self, score):
        if len(self.scores) < 5:
            return True
        return score > self.scores[-1][1]

    def get_high_score(self):
        if self.scores:
            return self.scores[0][1]
        return 0

    def draw(self, screen):
        font = pygame.font.Font(None, 20)
        title = font.render("HIGH SCORES", True, WHITE)
        screen.blit(title, (COLS * TILE_SIZE // 2 - title.get_width() // 2, HUD_HEIGHT + 20))

        for i, (name, score, level) in enumerate(self.scores[:5]):
            text = font.render(f"{i+1}. {name}  {score}  Lv{level}", True, YELLOW)
            screen.blit(text, (COLS * TILE_SIZE // 2 - text.get_width() // 2,
                               HUD_HEIGHT + 50 + i * 25))

    def draw_hud(self, screen, score, level, lives):
        font = pygame.font.Font(None, 28)
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        high_text = font.render(f"HIGH: {self.get_high_score()}", True, WHITE)
        level_text = font.render(f"LV {level}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(high_text, (SCREEN_WIDTH // 2 - high_text.get_width() // 2, 10))
        screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))

        for i in range(lives):
            pygame.draw.circle(screen, YELLOW, (30 + i * 25, SCREEN_HEIGHT - 15), 8)
            pygame.draw.arc(screen, BLACK, (30 + i * 25 - 5, SCREEN_HEIGHT - 23, 10, 10),
                            0.3, 5.98, 3)
