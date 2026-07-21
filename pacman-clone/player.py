import pygame
from constants import *

class Player:
    def __init__(self, maze):
        self.maze = maze
        self.col = 14
        self.row = 28
        self.x = self.col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.row * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
        self.direction = STOP
        self.next_direction = STOP
        self.speed = PLAYER_SPEED
        self.arrived = True
        self.mouth_phase = 0.0
        self.mouth_dir = 0.04
        self.moving = False

    def set_direction(self, direction):
        if direction != STOP:
            self.next_direction = direction

    def can_move(self, col, row):
        tile = self.maze.get_tile(col % COLS, row)
        if tile in (DOT, EMPTY, PELLET, TUNNEL):
            return True
        if tile == GHOST_DOOR:
            return True
        return False

    def update(self):
        if self.arrived:
            nd = self.next_direction
            nc = (self.col + nd[0]) % COLS
            nr = self.row + nd[1]
            if nd != STOP and self.can_move(nc, nr):
                self.direction = nd
                fc = nc
                fr = nr
            else:
                fc = (self.col + self.direction[0]) % COLS
                fr = self.row + self.direction[1]
                if self.direction == STOP or not self.can_move(fc, fr):
                    self.direction = STOP
                    self.moving = False
                    return

            self.col = fc
            self.row = fr
            self.arrived = False

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
            self.moving = True

        self.mouth_phase += self.mouth_dir
        if self.mouth_phase > 0.5 or self.mouth_phase < 0.01:
            self.mouth_dir = -self.mouth_dir
            self.mouth_phase = max(0.01, min(0.5, self.mouth_phase))

    def draw(self, screen):
        cx, cy = int(self.x), int(self.y)
        radius = TILE_SIZE // 2 - 2
        mouth = self.mouth_phase * 0.5

        angle = 0
        if self.direction == UP:
            angle = 270
        elif self.direction == DOWN:
            angle = 90
        elif self.direction == LEFT:
            angle = 180
        elif self.direction == RIGHT or self.direction == STOP:
            angle = 0

        if self.moving:
            start = (angle + mouth * 90) * 3.14159 / 180
            end = (angle + 360 - mouth * 90) * 3.14159 / 180
            pygame.draw.arc(screen, YELLOW, (cx - radius, cy - radius, radius * 2, radius * 2),
                            start, end, radius)
            ex = cx + (radius // 3) * (self.direction[0] or 1)
            ey = cy + (radius // 3) * (self.direction[1] or 0)
            pygame.draw.circle(screen, BLACK, (ex, ey), 2)
        else:
            pygame.draw.circle(screen, YELLOW, (cx, cy), radius)
            pygame.draw.circle(screen, BLACK, (cx - 3, cy - 3), 2)
            pygame.draw.circle(screen, BLACK, (cx + 3, cy - 3), 2)

    def reset_position(self):
        self.col = 14
        self.row = 28
        self.x = self.col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.row * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
        self.direction = STOP
        self.next_direction = STOP
        self.arrived = True
        self.moving = False
