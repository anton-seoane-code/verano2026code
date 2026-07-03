import pygame
import numpy as np
from world import WORLD_HEIGHT, CHUNK_SIZE

GRAVITY = -25.0
JUMP_SPEED = 8.0
SPEED = 5.0
SPRINT_MULT = 1.7
REACH = 6.0

class Player:
    def __init__(self, world):
        self.world = world
        self.pos = np.array([8.0, WORLD_HEIGHT + 2, 8.0], dtype=np.float64)
        self.velocity = np.zeros(3, dtype=np.float64)
        self.yaw = 0.0
        self.pitch = 0.0
        self.on_ground = False
        self.sprinting = False
        self.selected_block = 1
        self.mouse_grabbed = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.mouse_grabbed = not self.mouse_grabbed
                pygame.event.set_grab(self.mouse_grabbed)
                pygame.mouse.set_visible(not self.mouse_grabbed)
            elif event.key == pygame.K_SPACE and self.on_ground:
                self.velocity[1] = JUMP_SPEED
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_LSHIFT:
                self.sprinting = True
            elif event.key == pygame.K_1:
                self.selected_block = 1
            elif event.key == pygame.K_2:
                self.selected_block = 3
            elif event.key == pygame.K_3:
                self.selected_block = 5
            elif event.key == pygame.K_4:
                self.selected_block = 7
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LCTRL, pygame.K_LSHIFT):
                self.sprinting = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                hit = self.raycast()
                if hit:
                    bx, by, bz = hit['block']
                    self.world.set_block(bx, by, bz, 0)
            elif event.button == 3:
                hit = self.raycast()
                if hit:
                    bx, by, bz = hit['normal']
                    self.world.set_block(bx, by, bz, self.selected_block)
            elif event.button == 4:
                self.selected_block = max(1, self.selected_block - 1)
            elif event.button == 5:
                self.selected_block = min(7, self.selected_block + 1)

    def update(self, dt):
        dt = min(dt, 0.05)
        keys = pygame.key.get_pressed()
        dx, dz = 0.0, 0.0
        spd = SPEED * (SPRINT_MULT if self.sprinting else 1.0) * dt
        sin_yaw, cos_yaw = np.sin(self.yaw), np.cos(self.yaw)
        if keys[pygame.K_w]:
            dx -= sin_yaw * spd
            dz += cos_yaw * spd
        if keys[pygame.K_s]:
            dx += sin_yaw * spd
            dz -= cos_yaw * spd
        if keys[pygame.K_a]:
            dx -= cos_yaw * spd
            dz -= sin_yaw * spd
        if keys[pygame.K_d]:
            dx += cos_yaw * spd
            dz += sin_yaw * spd
        self.velocity[0] = dx / dt if dt > 0 else 0.0
        self.velocity[2] = dz / dt if dt > 0 else 0.0
        self.velocity[1] += GRAVITY * dt
        new_pos = self.pos + self.velocity * dt
        if self.collides(new_pos[0], self.pos[1], self.pos[2]):
            self.velocity[0] = 0
        else:
            self.pos[0] = new_pos[0]
        if self.collides(self.pos[0], new_pos[1], self.pos[2]):
            self.velocity[1] = 0
            self.on_ground = True
        else:
            self.pos[1] = new_pos[1]
            self.on_ground = False
        if self.collides(self.pos[0], self.pos[1], new_pos[2]):
            self.velocity[2] = 0
        else:
            self.pos[2] = new_pos[2]
        mx, my = pygame.mouse.get_rel()
        if self.mouse_grabbed:
            self.yaw += mx * 0.002
            self.pitch -= my * 0.002
            self.pitch = max(-np.pi / 2.2, min(np.pi / 2.2, self.pitch))

    def collides(self, x, y, z):
        hw, hh = 0.3, 1.0
        y_min = int(y - hh)
        y_max = int(y + hh)
        x_min = int(x - hw)
        x_max = int(x + hw)
        z_min = int(z - hw)
        z_max = int(z + hw)
        for dy in range(y_min, y_max + 1):
            if dy < 0 or dy >= WORLD_HEIGHT:
                continue
            for dx in range(x_min, x_max + 1):
                for dz in range(z_min, z_max + 1):
                    if self.world.get_block(dx, dy, dz) != 0:
                        return True
        return False

    def raycast(self):
        origin = self.pos.copy()
        origin[1] += 0.8
        direction = np.array([
            np.sin(self.yaw) * np.cos(self.pitch),
            np.sin(self.pitch),
            np.cos(self.yaw) * np.cos(self.pitch),
        ])
        direction = direction / np.linalg.norm(direction)
        x, y, z = origin
        dx, dy, dz = direction
        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
        step_z = 1 if dz > 0 else -1
        t_dx = abs(1.0 / dx) if dx != 0 else float('inf')
        t_dy = abs(1.0 / dy) if dy != 0 else float('inf')
        t_dz = abs(1.0 / dz) if dz != 0 else float('inf')
        bx, by, bz = int(x), int(y), int(z)
        t_max_x = ((bx + (1 if dx > 0 else 0)) - x) / dx if dx != 0 else float('inf')
        t_max_y = ((by + (1 if dy > 0 else 0)) - y) / dy if dy != 0 else float('inf')
        t_max_z = ((bz + (1 if dz > 0 else 0)) - z) / dz if dz != 0 else float('inf')
        prev_bx, prev_by, prev_bz = bx, by, bz
        for _ in range(int(REACH * 3)):
            if self.world.get_block(bx, by, bz) != 0:
                return {'block': (bx, by, bz), 'normal': (prev_bx, prev_by, prev_bz)}
            prev_bx, prev_by, prev_bz = bx, by, bz
            if t_max_x < t_max_y:
                if t_max_x > REACH:
                    break
                bx += step_x
                t_max_x += t_dx
            elif t_max_y < t_max_z:
                if t_max_y > REACH:
                    break
                by += step_y
                t_max_y += t_dy
            else:
                if t_max_z > REACH:
                    break
                bz += step_z
                t_max_z += t_dz
            if by < 0 or by >= WORLD_HEIGHT:
                break
        return None
