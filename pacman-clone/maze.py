import pygame
from constants import *

class Maze:
    def __init__(self):
        self.grid = []
        self.dots = 0
        self.pellets = []
        self.dot_positions = []
        self._load()

    def _load(self):
        for row_str in LAYOUT:
            row = []
            for ch in row_str:
                tile = TILE_MAP.get(ch, WALL)
                row.append(tile)
                if tile == DOT:
                    self.dots += 1
            self.grid.append(row)

        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == DOT:
                    self.dot_positions.append((c, r))
                elif self.grid[r][c] == PELLET:
                    self.pellets.append((c, r))

    def get_tile(self, col, row):
        if 0 <= col < COLS and 0 <= row < ROWS:
            return self.grid[row][col]
        return WALL

    def is_walkable(self, col, row, is_ghost=False):
        tile = self.get_tile(col, row)
        if tile in (DOT, EMPTY, PELLET, TUNNEL):
            return True
        if is_ghost and tile in (GHOST_INTERIOR, GHOST_DOOR):
            return True
        return False

    def remove_dot(self, col, row):
        if self.grid[row][col] == DOT:
            self.grid[row][col] = EMPTY
            self.dots -= 1
            return DOT_SCORE
        elif self.grid[row][col] == PELLET:
            self.grid[row][col] = EMPTY
            return PELLET_SCORE
        return 0

    def has_dot(self, col, row):
        return self.grid[row][col] in (DOT, PELLET)

    def draw(self, screen):
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.grid[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE + HUD_HEIGHT

                if tile == WALL:
                    pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, (0, 0, 60), (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
                elif tile == GHOST_WALL:
                    pygame.draw.rect(screen, DARK_BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, BLUE, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 1)
                elif tile == GHOST_INTERIOR:
                    pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == GHOST_DOOR:
                    pygame.draw.rect(screen, PINK, (x, y, TILE_SIZE, TILE_SIZE // 3))
                elif tile == DOT:
                    pygame.draw.circle(screen, DOT_COLOR, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 2)
                elif tile == PELLET:
                    pygame.draw.circle(screen, DOT_COLOR, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 6)
                elif tile == TUNNEL:
                    pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == EMPTY:
                    pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))

    def get_ghost_house_center(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == GHOST_INTERIOR:
                    return c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + HUD_HEIGHT + TILE_SIZE // 2
        return COLS * TILE_SIZE // 2, HUD_HEIGHT + ROWS * TILE_SIZE // 2

    def get_door_positions(self):
        doors = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == GHOST_DOOR:
                    doors.append((c, r))
        return doors
