import pygame
from random import randrange
from math import cos, sin, pi

from constants import *
from engine.sprite import Sprite
from game.ball import item_angle

class JunkEnemy(Sprite):
    def __init__(self, level, x, y):
        js = ['sphere', 'pyramid', 'cubes']
        img_name = js[level.junks_cur]
        img = level.images.get(f"{img_name}.1")
        super().__init__(img.image if img else pygame.Surface((32, 32)), x, y)
        if img:
            self.shape = img.shape

        self.x = float(x)
        self.y = float(y)
        self.img = img_name
        self.frame = 0
        self.imgframes = {'sphere': 24, 'pyramid': 16, 'cubes': 48}[img_name]
        self.v = float(randrange(JUNK_SPEED_MIN, JUNK_SPEED_MAX))
        an = randrange(0, 360) * 2.0 * pi / 360.0
        self.vx = cos(an) * self.v
        self.vy = sin(an) * self.v
        self.config = {'bouncy': 1, 'junk': 1}
        self.boom = 0
        self.update = junk_update
        self.hit = junk_hit
        self.groups = level.string2groups("junk")
        self.agroups = level.string2groups("ball,player,laser")
        level.junks += 1

def junk_update(level, a, t):
    a.frame += 1
    if not a.boom:
        img_key = f"{a.img}.{(a.frame % a.imgframes) + 1}"
        if img_key in level.images:
            a.tosprite(level.images[img_key])
        a.x += a.vx * t
        a.y += a.vy * t
        if level.sissy and a.y > TH * 20 and a.vy > 0:
            a.vy = -a.vy
    else:
        if a.frame == 16:
            level.remove(a)
            level.junks -= 1
            return
        img_key = f"boom.{a.frame // 2 + 1}"
        if img_key in level.images:
            a.tosprite(level.images[img_key])

def junk_hit(level, a, b):
    a.boom = 1
    a.frame = 0
    a.agroups = 0
    a.groups = 0
    if (b.groups & level.groups.get('ball', 0)):
        an = randrange(0, 100) * pi / 100.0
        b.vx = cos(an) * b.v
        b.vy = sin(an) * b.v
    if (b.groups & level.groups.get('laser', 0)):
        level.remove(b)
        level.lasers -= 1
    level.score += SCORE_JUNK

def junk_new(level):
    x = randrange(2, 21) * TW
    y = 1 * TH
    return JunkEnemy(level, x, y)
