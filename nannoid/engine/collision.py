import math
from pygame.rect import Rect
from constants import TW, TH

def loop_tilehits(level):
    tw, th = TW, TH
    tiles = level.tiles
    layer = level.layers[0]

    for s in level.sprites:
        if s.groups == 0:
            continue

        prev = s.prev
        cur = s.cur

        prevx, prevy = prev.x, prev.y
        prevw, prevh = prev.w, prev.h
        curx, cury = cur.x, cur.y
        curw, curh = cur.w, cur.h

        cur.y = prev.y
        cur.h = prev.h

        hits = []
        y = cur.top // th * th
        while y < cur.bottom:
            x = cur.left // tw * tw
            yy = y // th
            while x < cur.right:
                xx = x // tw
                if 0 <= yy < level.h and 0 <= xx < level.w:
                    t = tiles[layer[yy][xx]]
                    if t and (s.groups & t.agroups):
                        hits.append((xx, yy))
                x += tw
            y += th

        if hits:
            bh, bd = None, 256
            for hx, hy in hits:
                d = math.hypot(cur.centerx - (hx * TW + TW / 2), cur.centery - (hy * TH + TH / 2))
                if d < bd:
                    bd, bh = d, (hx, hy)
            if bh:
                xx, yy = bh
                t = tiles[layer[yy][xx]]
                if t and t.hit:
                    t.tx, t.ty = xx, yy
                    t.cur = Rect(xx * tw, yy * th, tw, th)
                    t.prev = Rect(t.cur)
                    t.hit(level, t, s)

        prev.x = cur.x
        prev.w = cur.w
        cur.y = cury
        cur.h = curh

        hits = []
        y = cur.top // th * th
        while y < cur.bottom:
            x = cur.left // tw * tw
            yy = y // th
            while x < cur.right:
                xx = x // tw
                if 0 <= yy < level.h and 0 <= xx < level.w:
                    t = tiles[layer[yy][xx]]
                    if t and (s.groups & t.agroups):
                        hits.append((xx, yy))
                x += tw
            y += th

        if hits:
            bh, bd = None, 256
            for hx, hy in hits:
                d = math.hypot(cur.centerx - (hx * TW + TW / 2), cur.centery - (hy * TH + TH / 2))
                if d < bd:
                    bd, bh = d, (hx, hy)
            if bh:
                xx, yy = bh
                t = tiles[layer[yy][xx]]
                if t and t.hit:
                    t.tx, t.ty = xx, yy
                    t.cur = Rect(xx * tw, yy * th, tw, th)
                    t.prev = Rect(t.cur)
                    t.hit(level, t, s)

        prev.x, prev.y = prevx, prevy

        if curx != cur.x:
            s.x = float(cur.x)
        if cury != cur.y:
            s.y = float(cur.y)

    for s in level.sprites:
        s.cur.x = int(s.x)
        s.cur.y = int(s.y)

def loop_spritehits(level):
    as_ = level.sprites[:]

    groups = {}
    for n in range(31):
        groups[1 << n] = []
    for s in as_:
        g = s.groups
        n = 1
        while g:
            if g & 1:
                groups[n].append(s)
            g >>= 1
            n <<= 1

    for s in as_:
        if s.agroups:
            g = s.agroups
            n = 1
            while g:
                if g & 1:
                    for b in groups[n]:
                        if s != b and (s.agroups & b.groups) and s.cur.colliderect(b.cur):
                            scurx, scury = s.cur.x, s.cur.y
                            bcurx, bcury = b.cur.x, b.cur.y
                            if s.hit:
                                s.hit(level, s, b)
                            if scurx != s.cur.x:
                                s.x = float(s.cur.x)
                            if scury != s.cur.y:
                                s.y = float(s.cur.y)
                            if bcurx != b.cur.x:
                                b.x = float(b.cur.x)
                            if bcury != b.cur.y:
                                b.y = float(b.cur.y)
                g >>= 1
                n <<= 1

    for s in as_:
        s.cur.x = int(s.x)
        s.cur.y = int(s.y)
