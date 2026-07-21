import pygame
import random
from constants import *
from board import Board
from tetromino import Tetromino
from scoreboard import Scoreboard

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.scoreboard = Scoreboard()
        self.reset_game()
        self.state = "MENU"

    def reset_game(self):
        self.board = Board()
        self.score = 0
        self.level = 1
        self.lines = 0
        self.bag = []
        self.current_piece = None
        self.next_piece = None
        self.hold_piece = None
        self.can_hold = True
        self.drop_timer = 0
        self.lock_timer = 0
        self.is_locking = False
        self.blink_frame = 0
        self.name_entry = ""
        self.fill_bag()
        self.next_piece = self.spawn_piece()
        self.current_piece = self.spawn_piece()

    def fill_bag(self):
        if not self.bag:
            self.bag = PIECE_NAMES[:]
            random.shuffle(self.bag)

    def spawn_piece(self):
        self.fill_bag()
        name = self.bag.pop(0)
        return Tetromino(name)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    self.state = "PLAYING"
                    self.reset_game()
                elif self.state == "PLAYING":
                    if event.key == pygame.K_LEFT:
                        self.current_piece.move(-1, 0, self.board)
                        if self.is_locking:
                            self.lock_timer = 0
                    elif event.key == pygame.K_RIGHT:
                        self.current_piece.move(1, 0, self.board)
                        if self.is_locking:
                            self.lock_timer = 0
                    elif event.key == pygame.K_UP:
                        self.current_piece.rotate(self.board, 1)
                        if self.is_locking:
                            self.lock_timer = 0
                    elif event.key == pygame.K_z:
                        self.current_piece.rotate(self.board, -1)
                        if self.is_locking:
                            self.lock_timer = 0
                    elif event.key == pygame.K_DOWN:
                        if self.current_piece.move(0, 1, self.board):
                            self.score += 1
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_c:
                        self.hold()
                elif self.state == "GAME_OVER":
                    if self.scoreboard.is_high_score(self.score):
                        self.state = "NAME_ENTRY"
                        self.name_entry = ""
                    else:
                        self.state = "SCOREBOARD"
                elif self.state == "NAME_ENTRY":
                    if event.key == pygame.K_RETURN and len(self.name_entry) == 3:
                        self.scoreboard.add_score(self.name_entry, self.score, self.level)
                        self.state = "SCOREBOARD"
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_entry = self.name_entry[:-1]
                    elif event.unicode and event.unicode.isalpha() and len(self.name_entry) < 3:
                        self.name_entry += event.unicode.upper()
                elif self.state == "SCOREBOARD":
                    self.state = "MENU"
        return True

    def hard_drop(self):
        while self.current_piece.move(0, 1, self.board):
            self.score += 2
        self.lock_piece()

    def hold(self):
        if not self.can_hold:
            return
        self.can_hold = False
        if self.hold_piece is None:
            self.hold_piece = Tetromino(self.current_piece.name)
            self.current_piece = self.next_piece
            self.next_piece = self.spawn_piece()
        else:
            name = self.current_piece.name
            self.current_piece = Tetromino(self.hold_piece.name)
            self.hold_piece = Tetromino(name)

    def lock_piece(self):
        self.board.lock(self.current_piece)
        cleared = self.board.clear_lines()
        if cleared:
            self.score += LINE_SCORES[cleared] * self.level
            self.lines += cleared
            new_level = self.lines // LINES_PER_LEVEL + 1
            if new_level > self.level:
                self.level = new_level
                self.state = "LEVEL_TRANSITION"
                self.transition_timer = 1500
        self.can_hold = True
        self.current_piece = self.next_piece
        self.next_piece = self.spawn_piece()
        self.is_locking = False
        self.lock_timer = 0
        self.drop_timer = 0
        if not self.board.is_valid(self.current_piece):
            self.state = "GAME_OVER"

    def update(self, dt):
        if self.state == "LEVEL_TRANSITION":
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.state = "PLAYING"
            return

        if self.state != "PLAYING":
            self.blink_frame += 1
            return

        if self.is_locking:
            down_cells = [(r + 1, c) for r, c in self.current_piece.get_cells()]
            if self.board.is_valid_cells(down_cells):
                self.is_locking = False
                self.lock_timer = 0

        speed = LEVEL_SPEEDS[min(self.level - 1, len(LEVEL_SPEEDS) - 1)]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            speed = SOFT_DROP_SPEED

        self.drop_timer += dt
        if self.drop_timer >= speed:
            self.drop_timer = 0
            if not self.current_piece.move(0, 1, self.board):
                self.is_locking = True
            elif keys[pygame.K_DOWN]:
                self.score += 1

        if self.is_locking:
            self.lock_timer += dt
            if self.lock_timer >= LOCK_DELAY:
                self.lock_piece()

    def render(self):
        self.screen.fill(BLACK)

        if self.state == "MENU":
            self.render_menu()
        elif self.state in ("PLAYING", "LEVEL_TRANSITION", "GAME_OVER", "NAME_ENTRY"):
            self.render_game()
            if self.state == "LEVEL_TRANSITION":
                self.render_level_transition()
            elif self.state == "GAME_OVER":
                self.render_game_over()
            elif self.state == "NAME_ENTRY":
                self.render_game_over()
                self.scoreboard.draw_name_entry(self.screen, self.name_entry, self.blink_frame)
        elif self.state == "SCOREBOARD":
            self.scoreboard.draw(self.screen)

        pygame.display.flip()

    def render_menu(self):
        font = pygame.font.Font(None, 64)
        title = font.render("TETRIS", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        font = pygame.font.Font(None, 28)
        instr = font.render("Press any key to start", True, WHITE)
        self.screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, 250))

        self.scoreboard.draw(self.screen, "HIGH SCORES")

    def render_game(self):
        grid_rect = pygame.Rect(GRID_X, GRID_Y, GRID_COLS * TILE_SIZE, GRID_ROWS * TILE_SIZE)
        pygame.draw.rect(self.screen, DARK_GRAY, grid_rect)
        pygame.draw.rect(self.screen, GRAY, grid_rect, 1)

        for r in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY,
                           (GRID_X, GRID_Y + r * TILE_SIZE),
                           (GRID_X + GRID_COLS * TILE_SIZE, GRID_Y + r * TILE_SIZE))
        for c in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, LIGHT_GRAY,
                           (GRID_X + c * TILE_SIZE, GRID_Y),
                           (GRID_X + c * TILE_SIZE, GRID_Y + GRID_ROWS * TILE_SIZE))

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.board.grid[r][c] is not None:
                    self.draw_block(self.board.grid[r][c], r, c)

        if self.current_piece:
            ghost = self.get_ghost_position()
            for r, c in ghost:
                self.draw_ghost_block(self.current_piece.color, r, c)

            for r, c in self.current_piece.get_cells():
                self.draw_block(self.current_piece.color, r, c)

        self.render_sidebar()

    def get_ghost_position(self):
        ghost = Tetromino(self.current_piece.name)
        ghost.row = self.current_piece.row
        ghost.col = self.current_piece.col
        ghost.rotation = self.current_piece.rotation
        while ghost.move(0, 1, self.board):
            pass
        return ghost.get_cells()

    def draw_block(self, color, row, col):
        x = GRID_X + col * TILE_SIZE
        y = GRID_Y + row * TILE_SIZE
        rect = pygame.Rect(x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2)
        pygame.draw.rect(self.screen, color, rect)
        lighter = tuple(min(255, c + 60) for c in color)
        pygame.draw.rect(self.screen, lighter, pygame.Rect(x + 1, y + 1, TILE_SIZE - 2, 3))
        pygame.draw.rect(self.screen, lighter, pygame.Rect(x + 1, y + 1, 3, TILE_SIZE - 2))

    def draw_ghost_block(self, color, row, col):
        x = GRID_X + col * TILE_SIZE
        y = GRID_Y + row * TILE_SIZE
        ghost_color = tuple(c // 3 for c in color)
        rect = pygame.Rect(x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2)
        pygame.draw.rect(self.screen, ghost_color, rect, 1)

    def render_sidebar(self):
        font = pygame.font.Font(None, 24)

        score_label = font.render("SCORE", True, WHITE)
        self.screen.blit(score_label, (SIDEBAR_X, GRID_Y))
        score_val = font.render(str(self.score), True, CYAN)
        self.screen.blit(score_val, (SIDEBAR_X, GRID_Y + 25))

        lvl_label = font.render("LEVEL", True, WHITE)
        self.screen.blit(lvl_label, (SIDEBAR_X, GRID_Y + 60))
        lvl_val = font.render(str(self.level), True, CYAN)
        self.screen.blit(lvl_val, (SIDEBAR_X, GRID_Y + 85))

        lines_label = font.render("LINES", True, WHITE)
        self.screen.blit(lines_label, (SIDEBAR_X, GRID_Y + 120))
        lines_val = font.render(str(self.lines), True, CYAN)
        self.screen.blit(lines_val, (SIDEBAR_X, GRID_Y + 145))

        next_label = font.render("NEXT", True, WHITE)
        self.screen.blit(next_label, (SIDEBAR_X, GRID_Y + 190))
        if self.next_piece:
            self.draw_mini_piece(self.next_piece, SIDEBAR_X, GRID_Y + 220)

        hold_label = font.render("HOLD", True, WHITE)
        self.screen.blit(hold_label, (SIDEBAR_X, GRID_Y + 340))
        if self.hold_piece:
            self.draw_mini_piece(self.hold_piece, SIDEBAR_X, GRID_Y + 370)

    def draw_mini_piece(self, piece, x, y):
        matrix = piece.get_matrix()
        size = len(matrix)
        mini_size = 20
        offset_x = x + (4 - size) * mini_size // 2
        for r in range(size):
            for c in range(size):
                if matrix[r][c]:
                    rect = pygame.Rect(offset_x + c * mini_size, y + r * mini_size,
                                     mini_size - 1, mini_size - 1)
                    pygame.draw.rect(self.screen, piece.color, rect)

    def render_level_transition(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 72)
        text = font.render(f"LEVEL {self.level}", True, YELLOW)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - text.get_height() // 2))

    def render_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 56)
        text = font.render("GAME OVER", True, RED)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                SCREEN_HEIGHT // 2 - 60))

        font = pygame.font.Font(None, 28)
        score_text = font.render(f"Score: {self.score}  Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()
