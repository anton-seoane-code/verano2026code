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
            except Exception:
                self.scores = []
        if not self.scores:
            self.scores = [("AAA", 1000, 1)]

    def save(self):
        with open(HIGH_SCORE_FILE, 'wb') as f:
            pickle.dump(self.scores[:5], f)

    def add_score(self, name, score, level):
        self.scores.append((name.upper()[:3], score, level))
        self.scores.sort(key=lambda x: -x[1])
        self.scores = self.scores[:5]
        self.save()

    def is_high_score(self, score):
        if len(self.scores) < 5:
            return True
        return score > self.scores[-1][1]

    def get_high_score(self):
        if self.scores:
            return self.scores[0][1]
        return 0

    def draw(self, screen, title="HIGH SCORES"):
        font = pygame.font.Font(None, 36)
        title_surf = font.render(title, True, WHITE)
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 80))

        font = pygame.font.Font(None, 28)
        for i, (name, score, level) in enumerate(self.scores):
            color = YELLOW if i == 0 else WHITE
            text = font.render(f"{i+1}. {name}  {score}  Lv{level}", True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 140 + i * 35))

        font = pygame.font.Font(None, 24)
        prompt = font.render("Press any key to continue", True, GRAY)
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT - 60))

    def draw_name_entry(self, screen, name, blink_frame):
        font = pygame.font.Font(None, 48)
        prompt = font.render("NEW HIGH SCORE!", True, YELLOW)
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 150))

        font = pygame.font.Font(None, 64)
        display = name + ('_' if blink_frame % 30 < 15 else ' ')
        name_surf = font.render(display, True, WHITE)
        screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, 220))

        font = pygame.font.Font(None, 24)
        instr = font.render("Enter your name (3 letters)", True, GRAY)
        screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, 290))
