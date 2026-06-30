import math
import random
import pygame
from constants import *

class Alien:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = ALIEN_SIZE
        self.speed = ALIEN_SPEED
        self.active = True
        self.angle = random.uniform(0, 360)
        self.change_timer = random.randint(30, 120)
        self.rotation = 0

    def update(self, players):
        self.change_timer -= 1
        if self.change_timer <= 0:
            self.angle = random.uniform(0, 360)
            self.change_timer = random.randint(30, 120)

        target = self._find_target(players)
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            target_angle = math.degrees(math.atan2(-dy, dx))
            diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += diff * 0.05

        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed

        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))

    def _find_target(self, players):
        if not players:
            return None
        closest = None
        min_dist = float("inf")
        for p in players:
            if p.alive:
                d = math.hypot(p.x - self.x, p.y - self.y)
                if d < min_dist:
                    min_dist = d
                    closest = p
        return closest

    def draw(self, screen):
        if not self.active:
            return
        self.rotation = (self.rotation + 2) % 360
        rad = math.radians(self.rotation)

        pts = []
        for i in range(6):
            a = rad + math.radians(60 * i)
            r = self.size if i % 2 == 0 else self.size * 0.6
            pts.append((self.x + math.cos(a) * r,
                        self.y + math.sin(a) * r))
        pygame.draw.polygon(screen, self.color, pts)
        pygame.draw.polygon(screen, WHITE, pts, 1)

        eye_rad = math.radians(self.rotation)
        eye_x = self.x + math.cos(eye_rad) * 4
        eye_y = self.y + math.sin(eye_rad) * 4
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)
