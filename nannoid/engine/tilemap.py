import pygame
from pygame.rect import Rect
from constants import TW, TH, W, H

class Tile:
    def __init__(self):
        self.image = None
        self.agroups = 0
        self.hit = None
        self.config = {}
        self.next = 0
        self.animate = 0
        self.tx = 0
        self.ty = 0

class Tilemap:
    def __init__(self):
        self.layers = []
        self.tiles = [None] * 4096
        self.w = 1
        self.h = 1
        self.origin = Rect(0, 0, 0, 0)
        self.bounds = None
        self.bkgr = None
        self.sprites = []
        self.images = {}
        self.removed = []

    def set(self, x, y, v):
        if 0 <= y < self.h and 0 <= x < self.w:
            if self.layers[0][y][x] != v:
                self.layers[0][y][x] = v

    def get(self, x, y):
        if 0 <= y < self.h and 0 <= x < self.w:
            return self.layers[0][y][x]
        return 0

    def add(self, s):
        self.sprites.append(s)

    def remove(self, s):
        if s in self.sprites:
            self.sprites.remove(s)
            self.removed.append(s)

    def resize(self, w, h):
        self.w = w
        self.h = h
        self.layers = [[[0] * w for _ in range(h)] for _ in range(5)]

    def tilesize(self):
        for t in self.tiles:
            if t is not None and t.image is not None:
                return t.image.get_width(), t.image.get_height()
        return TW, TH

    def dobounds(self, g):
        tw, th = self.tilesize()
        if self.bounds is None:
            self.bounds = Rect(0, 0, self.w * tw, self.h * th)
        origin = self.origin
        bounds = self.bounds
        if origin.left < bounds.left:
            origin.left = bounds.left
        if origin.top < bounds.top:
            origin.top = bounds.top
        origin.w = g.get_width()
        origin.h = g.get_height()
        if origin.right > bounds.right:
            origin.right = bounds.right
        if origin.bottom > bounds.bottom:
            origin.bottom = bounds.bottom

    def paint(self, g):
        self.dobounds(g)
        tw, th = self.tilesize()
        ox = self.origin.x
        oy = self.origin.y
        bg = self.bkgr

        w = g.get_width() // tw + 1
        h = g.get_height() // th + 1

        xi = ox // tw * tw
        yi = oy // th * th
        xf = ox + w * tw
        yf = oy + h * th

        bg_rect = Rect(0, 0, bg.get_width(), bg.get_height())
        if self.bounds and self.bounds.width > self.origin.width:
            bg_rect.left = (bg.get_width() - g.get_width()) * (self.origin.left - self.bounds.left) // (self.bounds.width - self.origin.width)
        if self.bounds and self.bounds.height > self.origin.height:
            bg_rect.top = (bg.get_height() - g.get_height()) * (self.origin.top - self.bounds.top) // (self.bounds.height - self.origin.height)

        yt = yi // th
        for y in range(yi - oy, yf - oy, th):
            xt = xi // tw
            for x in range(xi - ox, xf - ox, tw):
                tile = self.tiles[self.layers[0][yt][xt]]
                if tile and tile.image:
                    if tile.image.get_alpha() is not None:
                        g.blit(bg, (x, y), (bg_rect.left + x, bg_rect.top + y, tw, th))
                    g.blit(tile.image, (x, y))
                else:
                    g.blit(bg, (x, y), (bg_rect.left + x, bg_rect.top + y, tw, th))
                xt += 1
            yt += 1

        for s in self.sprites:
            g.blit(s.image, (s.cur.x + s.xoff - ox, s.cur.y + s.yoff - oy))
            s.updated = 0
            s.prev.x = s.cur.x
            s.prev.y = s.cur.y
            s.prev.w = s.cur.w
            s.prev.h = s.cur.h

        self.porigin = Rect(self.origin.x, self.origin.y, 0, 0)
