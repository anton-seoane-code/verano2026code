import random
from constants import SHAPES, PIECE_COLORS, PIECE_NAMES, GRID_COLS, WALL_KICKS

class Tetromino:
    def __init__(self, name=None):
        if name is None:
            name = random.choice(PIECE_NAMES)
        self.name = name
        self.rotation = 0
        self.shape = SHAPES[name]
        self.color = PIECE_COLORS[name]
        size = len(self.shape[0])
        self.col = GRID_COLS // 2 - size // 2
        self.row = 0

    def get_matrix(self):
        return self.shape[self.rotation]

    def get_size(self):
        return len(self.get_matrix())

    def get_cells(self):
        matrix = self.get_matrix()
        cells = []
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                if val:
                    cells.append((self.row + r, self.col + c))
        return cells

    def rotate(self, board, direction=1):
        old_rotation = self.rotation
        new_rotation = (self.rotation + direction) % 4
        kicks = WALL_KICKS if direction == 1 else WALL_KICKS

        for dc, dr in kicks:
            test_col = self.col + dc
            test_row = self.row + dr
            self.rotation = new_rotation
            self.col = test_col
            self.row = test_row
            if board.is_valid(self):
                return True
            self.rotation = old_rotation
            self.col = self.col - dc
            self.row = self.row - dr

        self.rotation = old_rotation
        return False

    def move(self, dx, dy, board):
        self.col += dx
        self.row += dy
        if board.is_valid(self):
            return True
        self.col -= dx
        self.row -= dy
        return False
