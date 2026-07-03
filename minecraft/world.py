import numpy as np
from collections import defaultdict
from blocks import BLOCK_TYPES

CHUNK_SIZE = 16
WORLD_HEIGHT = 64
VIEW_DISTANCE = 6

def hash_noise(x, z, seed):
    h = seed * 374761393 + x * 668265263 + z * 1274126177
    h = (h ^ (h >> 13)) * 1274126177
    return (h ^ (h >> 16)) & 0x7fffffff

def smooth_noise(x, z, seed, freq):
    fx, fz = x * freq, z * freq
    ix, iz = int(fx), int(fz)
    fx -= ix
    fz -= iz
    sx = fx * fx * (3 - 2 * fx)
    sz = fz * fz * (3 - 2 * fz)
    v00 = hash_noise(ix, iz, seed) / 0x7fffffff
    v10 = hash_noise(ix + 1, iz, seed) / 0x7fffffff
    v01 = hash_noise(ix, iz + 1, seed) / 0x7fffffff
    v11 = hash_noise(ix + 1, iz + 1, seed) / 0x7fffffff
    v0 = v00 + (v10 - v00) * sx
    v1 = v01 + (v11 - v01) * sx
    return v0 + (v1 - v0) * sz

def simple_noise(x, z, seed=42):
    h = 0.0
    for i, (amp, freq) in enumerate([(24, 0.02), (12, 0.05), (6, 0.1), (3, 0.2)]):
        h += amp * (smooth_noise(x, z, seed + i * 100, freq) - 0.5) * 2
    return max(1, min(WORLD_HEIGHT - 1, int(h) + 28))

class Chunk:
    def __init__(self, cx, cz):
        self.cx, self.cz = cx, cz
        self.dirty = True
        self.mesh_verts = None
        self.mesh_tex = None

    def generate(self, seed):
        sx, sz = self.cx * CHUNK_SIZE, self.cz * CHUNK_SIZE
        self.blocks = np.zeros((CHUNK_SIZE, WORLD_HEIGHT, CHUNK_SIZE), dtype=np.uint8)
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                h = simple_noise(sx + x, sz + z)
                for y in range(h):
                    if y == h - 1:
                        self.blocks[x, y, z] = 1 if h > 5 else 6
                    elif y > h - 4:
                        self.blocks[x, y, z] = 2
                    else:
                        self.blocks[x, y, z] = 3
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                h = int(self.blocks[x, :, z].nonzero()[0][-1]) + 1 if self.blocks[x, :, z].any() else 0
                if h > 5 and hash_noise(sx + x, sz + z, seed + 999) % 20 == 0:
                    trunk_h = 3 + hash_noise(sx + x, sz + z, seed + 888) % 3
                    for ty in range(h, h + trunk_h):
                        if ty < WORLD_HEIGHT:
                            self.blocks[x, ty, z] = 4
                    leaf_start = h + trunk_h - 2
                    for lx in range(-2, 3):
                        for lz in range(-2, 3):
                            for ly in range(leaf_start, h + trunk_h + 1):
                                wx, wz = x + lx, z + lz
                                if 0 <= wx < CHUNK_SIZE and 0 <= wz < CHUNK_SIZE and ly < WORLD_HEIGHT:
                                    if abs(lx) == 2 and abs(lz) == 2 and (ly == leaf_start or ly == h + trunk_h):
                                        continue
                                    if self.blocks[wx, ly, wz] == 0:
                                        self.blocks[wx, ly, wz] = 8
        self.dirty = True

    def get_block(self, x, y, z):
        if 0 <= x < CHUNK_SIZE and 0 <= y < WORLD_HEIGHT and 0 <= z < CHUNK_SIZE:
            return self.blocks[x, y, z]
        return None

    def set_block(self, x, y, z, bid):
        if 0 <= x < CHUNK_SIZE and 0 <= y < WORLD_HEIGHT and 0 <= z < CHUNK_SIZE:
            self.blocks[x, y, z] = bid
            self.dirty = True

    def is_transparent(self, bid):
        return bid == 0 or (bid in BLOCK_TYPES and not BLOCK_TYPES[bid].get('solid', True))

    def build_mesh(self, world_get_block):
        if not self.dirty and self.mesh_verts is not None:
            return self.mesh_verts, self.mesh_tex
        verts = []
        tex = []
        for x in range(CHUNK_SIZE):
            for y in range(WORLD_HEIGHT):
                for z in range(CHUNK_SIZE):
                    bid = self.blocks[x, y, z]
                    if bid == 0 or bid not in BLOCK_TYPES:
                        continue
                    bt = BLOCK_TYPES[bid]
                    wx, wy, wz = self.cx * CHUNK_SIZE + x, y, self.cz * CHUNK_SIZE + z
                    if not world_get_block(wx, wy + 1, wz) or self.is_transparent(world_get_block(wx, wy + 1, wz)):
                        self._add_face(verts, tex, wx, wy, wz, 'top', bt['top'])
                    if not world_get_block(wx, wy - 1, wz) or self.is_transparent(world_get_block(wx, wy - 1, wz)):
                        self._add_face(verts, tex, wx, wy, wz, 'bottom', bt['bottom'])
                    if not world_get_block(wx + 1, wy, wz) or self.is_transparent(world_get_block(wx + 1, wy, wz)):
                        self._add_face(verts, tex, wx, wy, wz, 'right', bt['side'])
                    if not world_get_block(wx - 1, wy, wz) or self.is_transparent(world_get_block(wx - 1, wy, wz)):
                        self._add_face(verts, tex, wx, wy, wz, 'left', bt['side'])
                    if not world_get_block(wx, wy, wz + 1) or self.is_transparent(world_get_block(wx, wy, wz + 1)):
                        self._add_face(verts, tex, wx, wy, wz, 'front', bt['side'])
                    if not world_get_block(wx, wy, wz - 1) or self.is_transparent(world_get_block(wx, wy, wz - 1)):
                        self._add_face(verts, tex, wx, wy, wz, 'back', bt['side'])
        self.mesh_verts = np.array(verts, dtype=np.float32) if verts else np.array([], dtype=np.float32)
        self.mesh_tex = np.array(tex, dtype=np.float32) if tex else np.array([], dtype=np.float32)
        self.dirty = False
        return self.mesh_verts, self.mesh_tex

    def _add_face(self, verts, tex, x, y, z, face, tex_key):
        hw = 0.5
        faces = {
            'top': [(-hw, hw, -hw), (-hw, hw, hw), (hw, hw, hw), (-hw, hw, -hw), (hw, hw, hw), (hw, hw, -hw)],
            'bottom': [(-hw, -hw, hw), (-hw, -hw, -hw), (hw, -hw, -hw), (-hw, -hw, hw), (hw, -hw, -hw), (hw, -hw, hw)],
            'right': [(hw, -hw, -hw), (hw, -hw, hw), (hw, hw, hw), (hw, -hw, -hw), (hw, hw, hw), (hw, hw, -hw)],
            'left': [(-hw, -hw, hw), (-hw, -hw, -hw), (-hw, hw, -hw), (-hw, -hw, hw), (-hw, hw, -hw), (-hw, hw, hw)],
            'front': [(-hw, -hw, hw), (hw, -hw, hw), (hw, hw, hw), (-hw, -hw, hw), (hw, hw, hw), (-hw, hw, hw)],
            'back': [(hw, -hw, -hw), (-hw, -hw, -hw), (-hw, hw, -hw), (hw, -hw, -hw), (-hw, hw, -hw), (hw, hw, -hw)],
        }
        bid, variant = tex_key
        u = (bid * 16 + {'top': 0, 'side': 8, 'bottom': 0}[variant]) / 128.0
        v = 0
        uv = [(u, v + 0.25), (u + 0.125, v + 0.25), (u + 0.125, v), (u, v + 0.25), (u + 0.125, v), (u, v)]
        for fv in faces[face]:
            verts.extend([x + fv[0], y + fv[1], z + fv[2]])
        for uv_ in uv:
            tex.extend(uv_)


class World:
    def __init__(self, seed=42):
        self.chunks = {}
        self.seed = seed

    def get_chunk(self, cx, cz):
        key = (cx, cz)
        if key not in self.chunks:
            c = Chunk(cx, cz)
            c.generate(self.seed)
            self.chunks[key] = c
        return self.chunks[key]

    def get_block(self, x, y, z):
        if y < 0 or y >= WORLD_HEIGHT:
            return 0
        cx = x // CHUNK_SIZE
        cz = z // CHUNK_SIZE
        lx = x % CHUNK_SIZE
        lz = z % CHUNK_SIZE
        c = self.get_chunk(cx, cz)
        return c.blocks[lx, y, lz] if c else 0

    def set_block(self, x, y, z, bid):
        if y < 0 or y >= WORLD_HEIGHT:
            return
        cx = x // CHUNK_SIZE
        cz = z // CHUNK_SIZE
        lx = x % CHUNK_SIZE
        lz = z % CHUNK_SIZE
        c = self.chunks.get((cx, cz))
        if c:
            c.set_block(lx, y, lz, bid)
            for dcx, dcz in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                nc = self.chunks.get((cx + dcx, cz + dcz))
                if nc:
                    nc.dirty = True

    def get_chunks_in_range(self, px, pz):
        result = []
        cx0 = int(px // CHUNK_SIZE) - VIEW_DISTANCE
        cz0 = int(pz // CHUNK_SIZE) - VIEW_DISTANCE
        for dx in range(VIEW_DISTANCE * 2 + 1):
            for dz in range(VIEW_DISTANCE * 2 + 1):
                cx, cz = cx0 + dx, cz0 + dz
                c = self.get_chunk(cx, cz)
                result.append((c, c.build_mesh(self.get_block)))
        return result
