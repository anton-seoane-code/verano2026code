import pygame

from constants import *
from engine.sprite import Sprite

class Laser(Sprite):
    def __init__(self, level, x, y):
        img = level.images.get("laser")
        super().__init__(img.image if img else pygame.Surface((6, 12)), x, y)
        if img:
            self.shape = img.shape

        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = -float(LASER_SPEED)
        self.update = laser_update
        self.groups = level.string2groups("laser")
        self.config = {'bouncy': 0, 'bouncydie': 1}
        level.add(self)
        level.lasers += 1

def laser_update(level, a, t):
    a.x += a.vx * t
    a.y += a.vy * t

def laser_new(level, paddle):
    Laser(level, paddle.cur.left, paddle.cur.top)
    Laser(level, paddle.cur.right - 6, paddle.cur.top)
    level.lasers = 2
