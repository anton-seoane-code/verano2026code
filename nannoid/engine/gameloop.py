import pygame
from pygame.locals import *
from constants import FPS, SPEED

class GameLoop:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = False
        self.state = None
        self.states = {}

    def run(self):
        self.running = True
        while self.running:
            if self.state:
                self.state = self.state()
            else:
                self.running = False

    def quit(self):
        self.running = False

def loop_events(level):
    for e in pygame.event.get():
        if e.type == QUIT:
            level.quit = 1
            return
        if hasattr(level, 'listeners'):
            for l in list(level.listeners.values()):
                if hasattr(l, 'event'):
                    l.event(level, l, e)

def loop_spriteupdate(level):
    ft = 1000.0 / FPS
    tt = ft * SPEED / 1000.0
    for s in level.sprites[:]:
        if hasattr(s, 'update') and s.update:
            curx, cury = s.cur.x, s.cur.y
            s.update(level, s, tt)
            if curx != s.cur.x:
                s.x = float(s.cur.x)
            if cury != s.cur.y:
                s.y = float(s.cur.y)
            s.cur.x = int(s.x)
            s.cur.y = int(s.y)

def loop_delay(level):
    ft = 1000.0 / FPS
    if not hasattr(level, '_nt') or not level._nt:
        level._nt = float(pygame.time.get_ticks())
        level._nt += ft
    ct = pygame.time.get_ticks()
    if ct < level._nt:
        pygame.time.wait(int(level._nt - ct))
        level._nt += ft
    else:
        level._nt = float(ct) + ft

def loop_update(level):
    for s in level.sprites:
        if s.cur.x != s.prev.x or s.cur.y != s.prev.y:
            s.updated = 1
    level.paint(level.screen)
    pygame.display.flip()

def game_loop(level):
    loop_events(level)
    loop_spriteupdate(level)
    from engine.collision import loop_tilehits, loop_spritehits
    loop_tilehits(level)
    loop_spritehits(level)
    loop_delay(level)
    loop_update(level)
