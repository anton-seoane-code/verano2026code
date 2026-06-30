import pygame
from constants import *

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

OPPOSITES = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}

class Snake:
    def __init__(self):
        start_x = GRID_SIZE // 2
        start_y = GRID_SIZE // 2
        self.segments = [(start_x, start_y)]
        self.direction = "right"
        self.next_direction = "right"
        self.direction_queue = []
        self.grow_flag = False
        self.alive = True

    def set_direction(self, new_dir):
        if new_dir in OPPOSITES and new_dir != OPPOSITES.get(self.direction):
            if not self.direction_queue or new_dir != OPPOSITES.get(self.direction_queue[-1]):
                self.direction_queue.append(new_dir)

    def update(self):
        if not self.alive:
            return

        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)

        dx, dy = DIRECTIONS[self.direction]
        head = self.segments[0]
        new_head = (head[0] + dx, head[1] + dy)

        self.segments.insert(0, new_head)
        if not self.grow_flag:
            self.segments.pop()
        self.grow_flag = False

    def grow(self):
        self.grow_flag = True

    def check_self_collision(self):
        if len(self.segments) < 2:
            return False
        head = self.segments[0]
        return head in self.segments[1:]

    def check_wall_collision(self):
        head = self.segments[0]
        return (head[0] < 0 or head[0] >= GRID_SIZE or
                head[1] < 0 or head[1] >= GRID_SIZE)

    def get_head(self):
        return self.segments[0]

    def get_body_set(self):
        return set(self.segments)

    def draw(self, screen):
        for i, seg in enumerate(self.segments):
            rect = pygame.Rect(seg[0] * CELL_SIZE, seg[1] * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            if i == 0:
                pygame.draw.rect(screen, DARK_GREEN, rect)
                inner = rect.inflate(-4, -4)
                pygame.draw.rect(screen, GREEN, inner)
                eye_x = seg[0] * CELL_SIZE + (CELL_SIZE // 4) * 3
                eye_y = seg[1] * CELL_SIZE + CELL_SIZE // 4
                if self.direction == "right":
                    eye_x = seg[0] * CELL_SIZE + (CELL_SIZE // 4) * 3
                    eye_y = seg[1] * CELL_SIZE + CELL_SIZE // 4
                elif self.direction == "left":
                    eye_x = seg[0] * CELL_SIZE + CELL_SIZE // 4
                    eye_y = seg[1] * CELL_SIZE + CELL_SIZE // 4
                elif self.direction == "up":
                    eye_x = seg[0] * CELL_SIZE + CELL_SIZE // 4
                    eye_y = seg[1] * CELL_SIZE + CELL_SIZE // 4
                elif self.direction == "down":
                    eye_x = seg[0] * CELL_SIZE + CELL_SIZE // 4
                    eye_y = seg[1] * CELL_SIZE + (CELL_SIZE // 4) * 3
                pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 3)
                pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 1)
            else:
                pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, DARK_GREEN, rect, 1)
