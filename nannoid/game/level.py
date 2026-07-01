import pygame
from pygame.locals import *
from pygame.rect import Rect

from constants import *
from engine.tilemap import Tilemap, Tile
from engine.sprite import Sprite
from engine.collision import loop_tilehits, loop_spritehits

def tile_death(level, tile_, sprite_):
    pass

def tile_block(level, tile_, sprite_):
    c = tile_.config
    if c.get('top') and sprite_.prev.bottom <= tile_.prev.top and sprite_.cur.bottom > tile_.cur.top:
        sprite_.cur.bottom = tile_.cur.top
        if sprite_.config and sprite_.config.get('bouncy'):
            sprite_.vy *= -1
    if c.get('left') and sprite_.prev.right <= tile_.prev.left and sprite_.cur.right > tile_.cur.left:
        sprite_.cur.right = tile_.cur.left
        if sprite_.config and sprite_.config.get('bouncy'):
            sprite_.vx *= -1
    if c.get('right') and sprite_.prev.left >= tile_.prev.right and sprite_.cur.left < tile_.cur.right:
        sprite_.cur.left = tile_.cur.right
        if sprite_.config and sprite_.config.get('bouncy'):
            sprite_.vx *= -1
    if c.get('bottom') and sprite_.prev.top >= tile_.prev.bottom and sprite_.cur.top < tile_.cur.bottom:
        sprite_.cur.top = tile_.cur.bottom
        if sprite_.config and sprite_.config.get('bouncy'):
            sprite_.vy *= -1
        if sprite_.config and sprite_.config.get('bouncydie'):
            level.remove(sprite_)
            level.lasers -= 1

    if sprite_.config and sprite_.config.get('junk'):
        return

    if c.get('explode'):
        block_explode(level, tile_)
    elif c.get('enext'):
        level.set(tile_.tx, tile_.ty, c['enext'])

def block_explode(level, tile_):
    c = tile_.config
    x, y = tile_.tx, tile_.ty
    n = level.get(x, y)
    level.set(x, y, c.get('enext', 0))

    if n == 7:
        level.clayer[y - 1][x] = -1 if y > 0 else 0
        level.clayer[y + 1][x] = -1 if y < level.h - 1 else 0
        level.clayer[y][x - 1] = -1 if x > 0 else 0
        level.clayer[y][x + 1] = -1 if x < level.w - 1 else 0
    elif n == 8:
        pass

    level.score += SCORE_BRICK
    level.blocks -= 1

def block_shadow(level, x, y):
    if x < 0 or y < 0 or x >= level.w or y >= level.h:
        return
    n = level.layers[2][y][x]
    m = 24
    if 0 < level.layers[0][y][x - 1] < 10:
        m += 1
    if y > 0 and 0 < level.layers[0][y - 1][x - 1] < 10:
        m += 2
    if y > 0 and 0 < level.layers[0][y - 1][x] < 10:
        m += 4
    if 0 < level.layers[0][y][x] < 10:
        m = 0
    if m != n:
        level.layers[2][y][x] = m

class Level(Tilemap):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.lives = LIVES
        self.balls = 0
        self.blocks = 0
        self.junks = 0
        self.lasers = 0
        self.dead = 0
        self.quit = 0
        self.sissy = 0
        self.cur = 1
        self.screen = None
        self.bkgr_fname = None
        self.music_fname = None
        self.level_fname = None
        self.listeners = {}
        self.groups = {}
        self.next_tile = []
        self.junks_cur = 0
        self.frame = 0

    def string2groups(self, s):
        return self.list2groups(s.split(","))

    def list2groups(self, igroups):
        for s in igroups:
            if s not in self.groups:
                self.groups[s] = 2 ** len(self.groups)
        v = 0
        for s, n in self.groups.items():
            if s in igroups:
                v |= n
        return v

    def groups2list(self, groups):
        v = []
        for s, n in self.groups.items():
            if n & groups:
                v.append(s)
        return v

    def load(self):
        with open(self.level_fname) as f:
            self.bkgr_fname = f.readline().strip()
            self.music_fname = f.readline().strip()
            f.readline()
            w, h = map(int, f.readline().split())
            self.resize(w, h)
            f.readline()
            for y in range(self.h):
                vals = list(map(int, f.readline().split()))
                for x in range(min(len(vals), self.w)):
                    self.layers[0][y][x] = vals[x]
            f.readline()
            for y in range(self.h):
                vals = list(map(int, f.readline().split()))
                for x in range(min(len(vals), self.w)):
                    self.layers[3][y][x] = vals[x]

    def init(self):
        l0 = [row[:] for row in self.layers[0]]
        clayer_data = [row[:] for row in self.layers[3]]
        orig_w, orig_h = self.w, self.h
        self.resize(GRID_W, GRID_H)

        for y in range(GAME_H):
            for x in range(GAME_W):
                if y < len(l0) and x < len(l0[0]):
                    self.layers[0][y + 3][x + 2] = l0[y][x]
                    if y < len(clayer_data) and x < len(clayer_data[0]):
                        self.layers[3][y + 3][x + 2] = clayer_data[y][x]

        for x in range(self.w):
            self.layers[0][0][x] = 14
            self.layers[0][1][x] = 13
            self.layers[0][2][x] = 13
            self.layers[0][35][x] = 15

        for y in range(self.h):
            self.layers[0][y][2] = 14
            self.layers[0][y][21] = 14

        self.clayer = self.layers[3]

        self.origin.x = ORIGIN_X
        self.origin.y = ORIGIN_Y

        self.blocks = 0
        for y in range(self.h):
            for x in range(self.w):
                t = self.tiles[self.layers[0][y][x]]
                if t and t.config.get('explode'):
                    self.blocks += 1

        self.next_tile = list(range(256))
        for n, t in enumerate(self.tiles):
            if t:
                self.next_tile[n] = t.config.get("next", n)

    def init_graphics(self, tiles_fname="tiles.png", alpha_fname=ALPHA_PATH):
        import os.path
        from assets.images_registry import images

        if self.bkgr is None and self.bkgr_fname:
            bkgr_path = f"{IMAGE_DIR}/{self.bkgr_fname}"
            if os.path.exists(bkgr_path):
                self.bkgr = pygame.image.load(bkgr_path).convert()
            else:
                bkgr_base = os.path.basename(self.bkgr_fname)
                alt_path = f"{IMAGE_DIR}/{bkgr_base}"
                if os.path.exists(alt_path):
                    self.bkgr = pygame.image.load(alt_path).convert()
                else:
                    self.bkgr = pygame.Surface((W, H))

        with open(alpha_fname) as f:
            alphas = [f.readline().strip().split() for _ in range(128)]

        img_path = f"{IMAGE_DIR}/{tiles_fname}"
        if not os.path.exists(img_path):
            img_path = f"{IMAGE_DIR}/tiles.png"

        aimg = pygame.image.load(img_path).convert_alpha()
        oimg = pygame.image.load(img_path).convert()

        for n in range(128):
            anum, atype = alphas[n]
            t = Tile()
            if atype == 'trans':
                t.image = None
            elif atype == 'opaque':
                t.image = oimg.subsurface((n % 8) * TW, (n // 8) * TH, TW, TH)
            elif atype == 'mixed':
                t.image = aimg.subsurface((n % 8) * TW, (n // 8) * TH, TW, TH)

            if n < len(tiles) and tiles[n]:
                agroups, hit, config = tiles[n]
                if agroups:
                    t.agroups = self.string2groups(agroups)
                if hit:
                    t.hit = hit
                if config:
                    t.config = config
                    t.next = config.get('next', n)
                else:
                    t.config = {}
                    t.next = n
                t.animate = 1 if t.next != n else 0
            else:
                t.agroups, t.hit, t.config = 0, None, {}
                t.next = n
                t.animate = 0

            self.tiles[n] = t

        iloader = {}
        for k, (fname, location, shape) in images.items():
            fpath = f"{IMAGE_DIR}/{fname}"
            if fpath not in iloader:
                iloader[fpath] = pygame.image.load(fpath).convert_alpha()
            img = iloader[fpath]
            e = Sprite(img.subsurface(location), 0, 0)
            e.shape = Rect(shape)
            self.images[k] = e

        from constants import PADDLE_SMALL, PADDLE_MEDIUM, PADDLE_LONGER, PADDLE_LONGEST
        for p in ['l', 'w', '3', 'c', 'e', 's', 'x', 'p']:
            key = f'paddles.{p}'
            if key not in self.images:
                continue
            img = self.images[key].image
            l = img.subsurface((0, 0, 6, 6))
            m = img.subsurface((6, 0, 6, 6))
            r = img.subsurface((12, 0, 6, 6))
            for w in range(PADDLE_SMALL, PADDLE_LONGEST + 1):
                pimg = pygame.Surface((w, 6), pygame.SRCALPHA)
                pimg.blit(l, (0, 0))
                pimg.blit(pygame.transform.scale(m, (w - 12, 6)), (6, 0))
                pimg.blit(r, (w - 6, 0))
                e = Sprite(pimg, 0, 0)
                e.shape = Rect(0, 0, pimg.get_width(), pimg.get_height())
                self.images[f"paddle.{p}.{w}"] = e

    def start(self):
        self.sprites = []
        self.removed = []
        self.listeners = {}

        self.dead = 0
        self.balls = 0
        self.junks = 0
        self.lasers = 0

        from game.paddle import paddle_new, player_catch
        from game.ball import ball_new
        from constants import BALL_SPEED_START

        p = paddle_new(self)
        b = ball_new(self, p.cur.centerx, p.cur.top, BALL_SPEED_START)
        b.cur.bottom = p.cur.top
        b.y = float(b.cur.y)
        b.vx, b.vy = 0.0, -float(BALL_SPEED_START)
        player_catch(self, p, b)

    def sparkle(self):
        for y in range(self.h):
            for x in range(self.w):
                n = self.get(x, y)
                if n == 6:
                    self.set(x, y, 32)
                if n == 8:
                    self.set(x, y, 48)

    def loop(self):
        from engine.gameloop import loop_events, loop_spriteupdate, loop_delay
        from engine.collision import loop_tilehits, loop_spritehits

        loop_events(self)
        loop_spriteupdate(self)
        loop_tilehits(self)
        loop_spritehits(self)

        layer = self.layers[0]
        next_tile = self.next_tile
        for y in range(self.h):
            for x in range(self.w):
                n = layer[y][x]
                nn = next_tile[n]
                if nn != n:
                    layer[y][x] = nn
                    if layer[y][x] == 0:
                        pass

        for y in range(self.h):
            for x in range(self.w):
                if self.clayer and self.clayer[y][x] == -1:
                    n = layer[y][x]
                    t = self.tiles[n]
                    if t and t.config.get('explode'):
                        block_explode(self, t)
                    elif t and t.config.get('enext'):
                        self.set(x, y, t.config['enext'])
                    self.clayer[y][x] = 0

        loop_delay(self)

        for s in self.sprites:
            if s.cur.x != s.prev.x or s.cur.y != s.prev.y:
                s.updated = 1
        self.paint(self.screen)
        pygame.display.flip()
        self.frame += 1

tiles = [(0, 0, 0) for _ in range(256)]

tiles[0] = (0, 0, 0)
tiles[1] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[2] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[3] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[4] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[5] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[6] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 32, 'explode': 0})
tiles[7] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[8] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 40, 'explode': 1})
tiles[9] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[13] = ('ball,player,junk,laser', tile_block, {'top': 0, 'left': 0, 'right': 0, 'bottom': 1, 'enext': 13})
tiles[14] = ('ball,player,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'enext': 14})
tiles[15] = ('ball,pill,junk,laser', tile_death, {})

tiles[16] = (0, 0, {'next': 17})
tiles[17] = (0, 0, {'next': 18})
tiles[18] = (0, 0, {'next': 19})
tiles[19] = (0, 0, {'next': 20})
tiles[20] = (0, 0, {'next': 21})
tiles[21] = (0, 0, {'next': 22})
tiles[22] = (0, 0, {'next': 23})
tiles[23] = (0, 0, {'next': 0})

tiles[32] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 33})
tiles[33] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 34})
tiles[34] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 35})
tiles[35] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 36})
tiles[36] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 37})
tiles[37] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 38})
tiles[38] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 39})
tiles[39] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 6})

tiles[40] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 41, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[41] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 42, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[42] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 43, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[43] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 44, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[44] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 45, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[45] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 46, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[46] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 47, 'enext': 16, 'explode': 1, 'pill': 1})
tiles[47] = ('ball,junk,laser', tile_block, {'top': 1, 'left': 1, 'right': 1, 'bottom': 1, 'next': 9, 'enext': 16, 'explode': 1, 'pill': 1})
