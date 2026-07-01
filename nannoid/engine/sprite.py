import pygame
from pygame.rect import Rect

class Sprite:
    def __init__(self, image, x, y):
        self.image = image
        self.cur = Rect(x, y, image.get_width(), image.get_height())
        self.prev = Rect(x, y, image.get_width(), image.get_height())
        self.x = float(x)
        self.y = float(y)

        self.groups = 0
        self.agroups = 0
        self.updated = 1

        self.xoff = 0
        self.yoff = 0

        self.update = None
        self.hit = None
        self.event = None

    def tosprite(self, s):
        self.image = s.image
        self.xoff = -s.shape.x
        self.yoff = -s.shape.y
        self.cur.w = s.shape.w
        self.cur.h = s.shape.h
