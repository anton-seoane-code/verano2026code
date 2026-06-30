import random
import pygame
from constants import *

class RedFood:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = True

    def respawn(self, snake_body):
        while True:
            self.x = random.randint(0, GRID_SIZE - 1)
            self.y = random.randint(0, GRID_SIZE - 1)
            if (self.x, self.y) not in snake_body:
                break
        self.active = True

    def draw(self, screen):
        if not self.active:
            return
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(screen, RED, inner)
        pygame.draw.rect(screen, (180, 0, 0), rect, 2)
        cx = self.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, YELLOW, (cx, cy), 3)

    def get_pos(self):
        return (self.x, self.y)


class BlueBonus:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = False
        self.timer = 0

    def spawn(self, snake_body):
        if self.active:
            return
        while True:
            self.x = random.randint(0, GRID_SIZE - 1)
            self.y = random.randint(0, GRID_SIZE - 1)
            if (self.x, self.y) not in snake_body and (self.x, self.y) != (0, 0):
                break
        self.active = True
        self.timer = BLUE_BONUS_DURATION

    def update(self):
        if not self.active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE,
                           CELL_SIZE, CELL_SIZE)
        inner = rect.inflate(-4, -4)
        blink = (self.timer // 5) % 2 == 0
        color = BLUE if not blink else (200, 200, 255)
        pygame.draw.rect(screen, color, inner)
        pygame.draw.rect(screen, (0, 0, 180), rect, 2)
        cx = self.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, WHITE, (cx, cy), 4)
        pygame.draw.circle(screen, color, (cx, cy), 2)

    def get_pos(self):
        return (self.x, self.y)
