import pygame
from pygame.locals import *
from math import cos, sin, pi, atan2
from random import randrange

from constants import *
from engine.sprite import Sprite

PADDLE_Y = TH * 30

class Paddle(Sprite):
    def __init__(self, level, x, y):
        w = PADDLE_MEDIUM
        if level.sissy:
            w += PADDLE_LONGER
        img = level.images.get(f"paddle.p.{w}")
        if img is None:
            surf = pygame.Surface((w, 6), pygame.SRCALPHA)
            super().__init__(surf, x, y)
        else:
            super().__init__(img.image, x, y)
            self.shape = img.shape
            self.tosprite(img)

        self.vx = 0.0
        self.vy = 0.0
        self.cw = w
        self.dw = w
        self.cp = 'p'
        self.catch = 0
        self.laser = 0
        self.x = float(x)
        self.y = float(y)
        self.config = {'bouncy': 0}
        self.groups = level.string2groups("player")
        self.agroups = level.string2groups("ball,pill")
        self.update = paddle_update
        self.event = paddle_event
        self.hit = paddle_hit

    def change_width(self, level):
        if self.dw != self.cw:
            diff = self.dw - self.cw
            step = 2 if diff > 0 else -2
            self.cw += step
            if abs(self.dw - self.cw) < 2:
                self.cw = self.dw
            img_key = f"paddle.{self.cp}.{self.cw}"
            if img_key in level.images:
                self.tosprite(level.images[img_key])

def paddle_update(level, a, t):
    a.x += a.vx * t
    if a.dw != a.cw:
        step = 2 if a.dw > a.cw else -2
        a.cw += step
        if abs(a.dw - a.cw) < 2:
            a.cw = a.dw
        img_key = f"paddle.{a.cp}.{a.cw}"
        if img_key in level.images:
            a.tosprite(level.images[img_key])

    if level.balls == 0:
        a.update = paddle_update_boom
        a.frame = 0
        level.listeners = {}

def paddle_update_boom(level, a, t):
    a.frame += 1
    if a.frame == 16:
        level.remove(a)
        level.dead = 1
        return
    x, y = a.cur.centerx, a.cur.centery
    img_key = f"boom.{a.frame // 2 + 1}"
    if img_key in level.images:
        a.tosprite(level.images[img_key])
    a.cur.centerx, a.cur.centery = x, y

def paddle_event(level, a, e):
    shoot = 0
    if e.type == KEYDOWN:
        if e.key == K_LEFT:
            a.vx -= 600
        elif e.key == K_RIGHT:
            a.vx += 600
        elif e.key == K_ESCAPE:
            level.quit = 1
        elif e.key == K_SPACE:
            shoot = 1
        elif e.key == K_RETURN or e.key == K_p:
            pass
        elif e.key == K_F12:
            level.blocks = 0
    elif e.type == KEYUP:
        if e.key == K_LEFT:
            a.vx += 600
        elif e.key == K_RIGHT:
            a.vx -= 600
    elif e.type == MOUSEMOTION:
        a.cur.centerx = e.pos[0] + level.origin.x
        if a.cur.left < level.origin.x + TW:
            a.cur.left = level.origin.x + TW
        if a.cur.right > level.origin.x + TW * 19:
            a.cur.right = level.origin.x + TW * 19
        a.x = float(a.cur.x)
        a.y = float(a.cur.y)
    elif e.type == MOUSEBUTTONDOWN:
        shoot = 1

    if shoot:
        g = level.groups.get("ball", 0)
        for s in level.sprites[:]:
            if (s.groups & g) and hasattr(s, 'caught') and s.caught == a:
                if s.vy > 0:
                    s.vy = -s.vy
                s.caught = 0
        if a.laser and level.lasers == 0:
            from game.laser import laser_new
            laser_new(level, a)

def paddle_hit(level, a, b):
    if b.prev.bottom <= a.prev.bottom:
        gl = level.groups2list(b.groups)
        if 'ball' in gl:
            b.cur.bottom = a.cur.top
            v = (b.vx ** 2 + b.vy ** 2) ** 0.5
            p = float(b.cur.centerx - a.cur.x) / float(a.cur.width)
            n = pi + pi / 6 + p * pi * 4 / 6
            b.vx = cos(n) * v
            b.vy = sin(n) * v
            if a.catch:
                player_catch(level, a, b)
            level.hits = getattr(level, 'hits', 0) + 1
            level.score += SCORE_BALL_HIT
        elif 'pill' in gl:
            item_kill(level, a, b)

def player_catch(level, a, b):
    b.cur.bottom = a.cur.top
    b.caught = a
    b.caught_x = b.cur.x - a.cur.x
    if b.vy > 0:
        b.vy = -b.vy

def item_kill(level, a, b):
    if hasattr(b, 'killed'):
        return
    if (b.groups & level.groups.get('ball', 0)):
        level.balls -= 1
        if level.balls <= 0:
            for p in level.sprites:
                if (p.groups & level.groups.get('player', 0)):
                    level.lives -= 1
    level.remove(b)
    b.killed = 1

def paddle_new(level):
    p = Paddle(level, level.origin.x + 320 - PADDLE_MEDIUM // 2, PADDLE_Y)
    level.add(p)
    level.listeners[p] = p
    return p
