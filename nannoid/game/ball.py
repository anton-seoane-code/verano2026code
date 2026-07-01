from math import cos, sin, atan2, pi
from random import randrange

import pygame
from constants import *
from engine.sprite import Sprite

class Ball(Sprite):
    def __init__(self, level, x, y, v):
        img = level.images.get("ball")
        super().__init__(img.image if img else pygame.Surface((12, 12)), x, y)
        if img:
            self.shape = img.shape
            self.tosprite(img)

        self.x = float(x)
        self.y = float(y)
        self.v = float(v)
        a = randrange(1, 1000)
        self.vx = cos(a) * v
        self.vy = sin(a) * v
        self.config = {'bouncy': 1}
        self.groups = level.string2groups("ball")
        self.agroups = 0
        self.update = ball_update
        self.caught = 0
        self.t = 0

def ball_speed(level, a, v):
    a.v = v
    if a.v > BALL_SPEED_MAX:
        a.v = BALL_SPEED_MAX
    an = atan2(a.vy, a.vx)
    a.vx = cos(an) * a.v
    a.vy = sin(an) * a.v

def item_angle(a):
    an = atan2(a.vy, a.vx)
    an = an * 360.0 / (2.0 * pi)
    an = int(an)
    m = an // 90
    n = an % 90
    d = 6
    if n < d:
        n = d
    if n > 90 - d:
        n = 90 - d
    an = m * 90 + n
    an = an * 2.0 * pi / 360.0
    a.vx = cos(an) * a.v
    a.vy = sin(an) * a.v

def ball_update(level, a, t):
    if a.caught == 0:
        a.x += a.vx * t
        a.y += a.vy * t
        a.t += t
        n = BALL_ACCEL_INTERVAL
        if level.sissy:
            n = BALL_ACCEL_INTERVAL_SISSY
        if a.t > n:
            ball_speed(level, a, a.v + BALL_ACCEL)
            a.t = 0
        item_angle(a)

        if a.y > TH * 35:
            level.remove(a)
            level.balls -= 1
            if level.balls <= 0:
                from game.paddle import paddle_update_boom
                for p in level.sprites:
                    if (p.groups & level.groups.get('player', 0)):
                        p.update = paddle_update_boom
                        p.frame = 0
                        level.listeners = {}
    else:
        a.cur.bottom = a.caught.cur.top
        a.x = a.caught.x + a.caught_x

def ball_new(level, x, y, v):
    b = Ball(level, x, y, v)
    level.add(b)
    level.balls += 1
    return b
