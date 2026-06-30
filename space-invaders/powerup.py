import random
import pygame
from constants import *

class PowerUp:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.speed = POWERUP_SPEED
        self.size = POWERUP_SIZE
        self.active = True
        self.timer = 0

    @classmethod
    def spawn_random(cls):
        kind = random.choice(["laser", "bullettime"])
        x = random.randint(POWERUP_SIZE, SCREEN_WIDTH - POWERUP_SIZE)
        y = random.randint(POWERUP_SIZE, SCREEN_HEIGHT // 2)
        return cls(x, y, kind)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT + self.size:
            self.active = False

    def draw(self, screen):
        color = LASER_BLUE if self.kind == "laser" else BULLET_TIME_RED
        rect = pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        inner = self.size - 3
        pygame.draw.rect(screen, color, rect.inflate(-4, -4))
        if self.kind == "laser":
            pts = [
                (self.x, self.y - inner),
                (self.x + inner, self.y),
                (self.x, self.y + inner),
                (self.x - inner, self.y),
            ]
        else:
            pts = [
                (self.x - inner, self.y - inner),
                (self.x + inner, self.y - inner),
                (self.x + inner, self.y + inner),
                (self.x - inner, self.y + inner),
            ]
        pygame.draw.polygon(screen, (255, 255, 255), pts, 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)
