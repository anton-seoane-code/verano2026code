import pygame
import math
import random
from constants import *

class Ghost:
    def __init__(self, maze, start_col, start_row, color, ghost_type):
        self.maze = maze
        self.start_col = start_col
        self.start_row = start_row
        self.col = start_col
        self.row = start_row
        self.x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = start_row * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
        self.color = color
        self.ghost_type = ghost_type
        self.direction = UP
        self.speed = GHOST_SPEED
        self.mode = 'house'
        self.frightened_timer = 0
        self.in_house = True
        self.eaten = False
        self.leave_timer = 0
        self.arrived = True

    def _can_move(self, col, row):
        tile = self.maze.get_tile(col % COLS, row)
        if tile in (EMPTY, DOT, PELLET, TUNNEL):
            return True
        if self.mode == 'eaten' and tile == GHOST_DOOR:
            return True
        if tile == GHOST_INTERIOR:
            return True
        if tile == GHOST_DOOR:
            return self.mode in ('eaten', 'house')
        return False

    def _get_chase_target(self, player):
        if self.ghost_type == 'blinky':
            return (player.col, player.row)
        elif self.ghost_type == 'pinky':
            return ((player.col + player.direction[0] * 4) % COLS,
                    player.row + player.direction[1] * 4)
        elif self.ghost_type == 'inky':
            ahead = (player.col + player.direction[0] * 2,
                     player.row + player.direction[1] * 2)
            b = getattr(self, 'blinky_ref', None)
            if b:
                return ((ahead[0] + (ahead[0] - b.col)) % COLS,
                        ahead[1] + (ahead[1] - b.row))
            return ahead
        else:
            dist = math.hypot(self.col - player.col, self.row - player.row)
            if dist > 8:
                return (player.col, player.row)
            return (0, ROWS - 1)

    def _get_scatter_target(self):
        targets = {
            'blinky': (COLS - 1, 0),
            'pinky': (0, 0),
            'inky': (COLS - 1, ROWS - 1),
            'clyde': (0, ROWS - 1),
        }
        return targets.get(self.ghost_type, (0, 0))

    def set_leave_timer(self, frames):
        self.leave_timer = frames

    def toggle_mode(self, chase):
        if self.mode in ('chase', 'scatter'):
            self.mode = 'chase' if chase else 'scatter'
            self.direction = (-self.direction[0], -self.direction[1])

    def set_frightened(self, duration):
        if self.mode not in ('eaten', 'house'):
            self.mode = 'frightened'
            self.frightened_timer = duration
            self.direction = (-self.direction[0], -self.direction[1])

    def set_eaten(self):
        self.mode = 'eaten'
        self.eaten = True
        self.speed = GHOST_EATEN_SPEED

    def _pick_direction(self, target):
        possible = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        opposite = (-self.direction[0], -self.direction[1])
        if opposite in possible:
            possible.remove(opposite)

        random.shuffle(possible)

        best = None
        best_d = float('inf')

        for d in possible:
            nc = (self.col + d[0]) % COLS
            nr = self.row + d[1]
            if self._can_move(nc, nr):
                if self.mode == 'frightened':
                    if best is None or random.random() < 0.25:
                        best = d
                    continue
                if target:
                    dist = math.hypot(nc - target[0], nr - target[1])
                    if dist < best_d:
                        best_d = dist
                        best = d

        return best

    def update(self, player, blinky=None):
        if self.mode == 'house':
            self.leave_timer -= 1
            if self.leave_timer <= 0:
                self.mode = 'leaving'
            return

        if self.mode == 'frightened' and self.frightened_timer > 0:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = 'chase'

        if self.arrived:
            if self.mode == 'leaving':
                self.col = 14
                self.row = 13
                self.x = self.col * TILE_SIZE + TILE_SIZE // 2
                self.y = self.row * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
                self.mode = 'chase'
                self.direction = LEFT
                return

            if self.mode == 'eaten':
                if self.maze.get_tile(self.col % COLS, self.row) == GHOST_INTERIOR:
                    self.mode = 'house'
                    self.eaten = False
                    self.speed = GHOST_SPEED
                    self.leave_timer = 60
                    self.arrived = True
                    return

            target = None
            if self.mode == 'scatter':
                target = self._get_scatter_target()
            elif self.mode == 'chase':
                target = self._get_chase_target(player)
            elif self.mode == 'eaten':
                doors = self.maze.get_door_positions()
                target = doors[0] if doors else self.maze.get_ghost_house_center()

            chosen = self._pick_direction(target)
            if chosen:
                self.direction = chosen

            fc = (self.col + self.direction[0]) % COLS
            fr = self.row + self.direction[1]
            if self._can_move(fc, fr):
                self.col = fc
                self.row = fr
                self.arrived = False
            else:
                rev = (-self.direction[0], -self.direction[1])
                rc = (self.col + rev[0]) % COLS
                rr = self.row + rev[1]
                if self._can_move(rc, rr):
                    self.direction = rev
                    self.col = rc
                    self.row = rr
                    self.arrived = False
                else:
                    self.arrived = True
                    return

        tx = self.col * TILE_SIZE + TILE_SIZE // 2
        ty = self.row * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed

        crossed_x = (self.direction[0] > 0 and self.x >= tx) or \
                    (self.direction[0] < 0 and self.x <= tx) or \
                    (self.direction[0] == 0)
        crossed_y = (self.direction[1] > 0 and self.y >= ty) or \
                    (self.direction[1] < 0 and self.y <= ty) or \
                    (self.direction[1] == 0)

        if crossed_x and crossed_y:
            self.x = tx
            self.y = ty
            self.arrived = True

    def draw(self, screen):
        cx, cy = int(self.x), int(self.y)
        radius = TILE_SIZE // 2 - 2

        if self.mode == 'frightened':
            flash = self.frightened_timer < 120 and (self.frightened_timer // 10) % 2 == 0
            color = (255, 255, 255) if flash else (0, 0, 255)
        elif self.mode == 'eaten':
            self._draw_eyes(screen, cx, cy)
            return
        else:
            color = self.color

        pygame.draw.circle(screen, color, (cx, cy - radius // 3), radius)
        body = pygame.Rect(cx - radius, cy - radius // 3, radius * 2, radius * 1.2)
        pygame.draw.rect(screen, color, body)

        wave_w = max(radius * 2 // 3, 4)
        for i in range(3):
            wx = cx - radius + i * wave_w + wave_w // 2
            wy = cy + radius // 2
            pygame.draw.circle(screen, color, (wx, wy), wave_w // 2)

        self._draw_eyes(screen, cx, cy)

    def _draw_eyes(self, screen, cx, cy):
        pygame.draw.circle(screen, WHITE, (cx - 4, cy - 3), 4)
        pygame.draw.circle(screen, WHITE, (cx + 4, cy - 3), 4)
        d = self.direction
        ex1 = cx - 4 + d[0] * 2
        ey1 = cy - 3 + d[1] * 2
        ex2 = cx + 4 + d[0] * 2
        ey2 = cy - 3 + d[1] * 2
        pygame.draw.circle(screen, BLACK, (ex1, ey1), 2)
        pygame.draw.circle(screen, BLACK, (ex2, ey2), 2)

    def reset_position(self):
        self.col = self.start_col
        self.row = self.start_row
        self.x = self.start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_row * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
        self.direction = UP
        self.mode = 'house'
        self.frightened_timer = 0
        self.eaten = False
        self.speed = GHOST_SPEED
        self.arrived = True


def create_ghosts(maze):
    blinky = Ghost(maze, 14, 11, RED, 'blinky')
    pinky = Ghost(maze, 12, 11, PINK, 'pinky')
    inky = Ghost(maze, 15, 11, CYAN, 'inky')
    clyde = Ghost(maze, 12, 12, ORANGE, 'clyde')
    inky.blinky_ref = blinky
    return [blinky, pinky, inky, clyde]
