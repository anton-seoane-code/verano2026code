import pygame
from random import randrange, choice

from constants import *
from engine.sprite import Sprite

class Pill(Sprite):
    def __init__(self, level, x, y, t):
        key = f"pills.{t}"
        img = level.images.get(key)
        super().__init__(img.image if img else pygame.Surface((32, 16)), x, y)
        if img:
            self.shape = img.shape

        self.x = float(x)
        self.y = float(y)
        self.type = t
        self.vy = PILL_SPEED
        self.update = pill_update
        self.groups = level.string2groups("pill")
        self.agroups = 0

def pill_update(level, a, t):
    a.y += a.vy * t

def pill_new(level, x, y):
    t = choice(['e', 's', 'l', 'c', 'p', '3'])
    p = Pill(level, x, y, t)
    level.add(p)
    return p
