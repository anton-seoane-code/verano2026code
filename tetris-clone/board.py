from constants import *

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    def is_valid_cells(self, cells):
        for r, c in cells:
            if r < 0 or r >= GRID_ROWS or c < 0 or c >= GRID_COLS:
                return False
            if self.grid[r][c] is not None:
                return False
        return True

    def is_valid(self, tetromino):
        return self.is_valid_cells(tetromino.get_cells())

    def lock(self, tetromino):
        for r, c in tetromino.get_cells():
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                self.grid[r][c] = tetromino.color

    def clear_lines(self):
        cleared = 0
        for r in range(GRID_ROWS - 1, -1, -1):
            if all(self.grid[r][c] is not None for c in range(GRID_COLS)):
                del self.grid[r]
                self.grid.insert(0, [None for _ in range(GRID_COLS)])
                cleared += 1
        return cleared

    def is_game_over(self):
        return any(self.grid[0][c] is not None for c in range(GRID_COLS))
