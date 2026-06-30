import pygame
import math
from constants import *

class Bullet:
    def __init__(self, x, y, angle, color, is_laser=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color
        self.is_laser = is_laser
        self.speed = BULLET_SPEED * 2 if is_laser else BULLET_SPEED
        self.size = BULLET_SIZE * 2 if is_laser else BULLET_SIZE
        self.active = True

    def update(self):
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed
        if (self.x < -self.size or self.x > SCREEN_WIDTH + self.size or
                self.y < -self.size or self.y > SCREEN_HEIGHT + self.size):
            self.active = False

    def draw(self, screen):
        if self.is_laser:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size - 1)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
