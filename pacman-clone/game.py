import pygame
import sys
from constants import *
from maze import Maze
from player import Player
from ghost import Ghost, create_ghosts
from scoreboard import Scoreboard

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man Clone")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)

        self.scoreboard = Scoreboard()
        self.state = 'menu'
        self.score = 0
        self.level = 1
        self.lives = 3
        self.flash_timer = 0
        self.ghost_combo = 0
        self.scatter_mode = False
        self.scatter_timer = 0
        self.chase_timer = 0
        self.player_name = ""
        self.name_entry = False
        self.input_name = ""

        self._init_level()

    def _init_level(self):
        self.maze = Maze()
        self.player = Player(self.maze)
        self.ghosts = create_ghosts(self.maze)

        speed_mult = 1.0 + (self.level - 1) * 0.05
        pellet_dur = max(MIN_PELLET_DURATION, PELLET_DURATION - (self.level - 1) * LEVEL_PELLET_DECREASE)
        scatter_dur = max(MIN_SCATTER_DURATION, INITIAL_SCATTER_DURATION - (self.level - 1) * LEVEL_SCATTER_DECREASE)

        self.player.speed = int(PLAYER_SPEED * speed_mult)
        self.pellet_duration = pellet_dur
        self.scatter_duration = scatter_dur
        self.chase_duration = INITIAL_CHASE_DURATION

        self.scatter_mode = True
        self.scatter_timer = scatter_dur
        self.chase_timer = 0
        self.ghost_combo = 0

        self.ghosts[0].set_leave_timer(0)
        self.ghosts[1].set_leave_timer(90)
        self.ghosts[2].set_leave_timer(180)
        self.ghosts[3].set_leave_timer(270)

        for g in self.ghosts:
            g.speed = int(GHOST_SPEED * speed_mult)

    def _toggle_ghost_mode(self):
        chase = not self.scatter_mode
        for g in self.ghosts:
            g.toggle_mode(chase)

    def _draw_text_centered(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
        return surf

    def _draw_menu(self):
        self.screen.fill(BLACK)
        self._draw_text_centered("PAC-MAN", self.font_big, YELLOW, HUD_HEIGHT + 100)
        self._draw_text_centered("Press SPACE to Start", self.font_small, WHITE, HUD_HEIGHT + 200)
        self._draw_text_centered("Arrow Keys / WASD to Move", self.font_small, WHITE, HUD_HEIGHT + 230)
        self.scoreboard.draw(self.screen)

    def _draw_game_over(self):
        self.screen.fill(BLACK)
        self._draw_text_centered("GAME OVER", self.font_big, RED, HUD_HEIGHT + 80)
        self._draw_text_centered(f"Score: {self.score}", self.font_small, WHITE, HUD_HEIGHT + 160)
        self._draw_text_centered(f"Level: {self.level}", self.font_small, WHITE, HUD_HEIGHT + 190)

        if self.name_entry:
            input_surf = self.font_small.render(f"Name: {self.input_name}_", True, YELLOW)
            self.screen.blit(input_surf, (SCREEN_WIDTH // 2 - input_surf.get_width() // 2, HUD_HEIGHT + 240))
            self._draw_text_centered("Press ENTER to save", self.font_small, WHITE, HUD_HEIGHT + 270)
        else:
            self._draw_text_centered("Press SPACE to continue", self.font_small, WHITE, HUD_HEIGHT + 240)
        self.scoreboard.draw(self.screen)

    def _draw_level_transition(self):
        self.screen.fill(BLACK)
        self._draw_text_centered(f"LEVEL {self.level}", self.font_big, YELLOW, HUD_HEIGHT + 150)

    def _reset_positions(self):
        self.player.reset_position()
        for g in self.ghosts:
            g.reset_position()
        self.ghosts[0].set_leave_timer(0)
        self.ghosts[1].set_leave_timer(90)
        self.ghosts[2].set_leave_timer(180)
        self.ghosts[3].set_leave_timer(270)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.state = 'playing'
                        self.score = 0
                        self.level = 1
                        self.lives = 3
                        self._init_level()
                    continue

                if self.state == 'game_over' and self.name_entry:
                    if event.key == pygame.K_RETURN:
                        name = self.input_name.strip() or "AAA"
                        self.scoreboard.add_score(name, self.score, self.level)
                        self.name_entry = False
                        self.input_name = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    elif event.unicode.isalpha() and len(self.input_name) < 3:
                        self.input_name += event.unicode.upper()
                    continue

                if self.state == 'game_over':
                    if event.key == pygame.K_SPACE:
                        self.state = 'menu'
                        self.score = 0
                        self.level = 1
                        self.lives = 3
                    continue

                if self.state == 'playing':
                    if event.key in DIR_VECTORS:
                        self.player.set_direction(DIR_VECTORS[event.key])

        return True

    def update(self):
        if self.state == 'dying':
            self.flash_timer += 1
            if self.flash_timer > 60:
                self.flash_timer = 0
                if self.lives <= 0:
                    if self.scoreboard.is_high_score(self.score):
                        self.name_entry = True
                        self.input_name = ""
                        self.state = 'game_over'
                    else:
                        self.state = 'game_over'
                else:
                    self.state = 'playing'
                    self._reset_positions()
            return

        if self.state == 'level_transition':
            self.flash_timer += 1
            if self.flash_timer > 60:
                self.flash_timer = 0
                self.state = 'playing'
                self._init_level()
            return

        if self.state != 'playing':
            return

        self.player.update()

        for g in self.ghosts:
            blinky = self.ghosts[0] if g.ghost_type != 'blinky' else None
            g.update(self.player, self.ghosts[0])

        if self.scatter_mode:
            self.scatter_timer -= 1
            if self.scatter_timer <= 0:
                self.scatter_mode = False
                self.chase_timer = self.chase_duration
                self._toggle_ghost_mode()
        else:
            self.chase_timer -= 1
            if self.chase_timer <= 0:
                self.scatter_mode = True
                self.scatter_timer = self.scatter_duration
                self._toggle_ghost_mode()

        px, py = int(self.player.x), int(self.player.y)
        p_col = (px - TILE_SIZE // 2) // TILE_SIZE % COLS
        p_row = (py - HUD_HEIGHT) // TILE_SIZE

        if self.maze.has_dot(p_col, p_row):
            pts = self.maze.remove_dot(p_col, p_row)
            if pts > 0:
                self.score += pts
                if pts == PELLET_SCORE:
                    self._activate_power_pellet()
                if self.lives < 9 and self.score >= EXTRA_LIFE_SCORE:
                    self.lives += 1

        for g in self.ghosts:
            if g.mode == 'eaten':
                continue
            dx = abs(self.player.x - g.x)
            dy = abs(self.player.y - g.y)
            if dx < TILE_SIZE - 2 and dy < TILE_SIZE - 2:
                if g.mode == 'frightened':
                    self.ghost_combo += 1
                    pts = GHOST_SCORE_BASE * (2 ** (self.ghost_combo - 1))
                    self.score += pts
                    g.set_eaten()
                elif g.mode not in ('house', 'leaving'):
                    self.lives -= 1
                    self.state = 'dying'
                    self.flash_timer = 0
                    return

        if self.maze.dots == 0:
            self.level += 1
            self.state = 'level_transition'
            self.flash_timer = 0

    def _activate_power_pellet(self):
        self.ghost_combo = 0
        for g in self.ghosts:
            if g.mode not in ('eaten', 'house'):
                g.set_frightened(self.pellet_duration)

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == 'menu':
            self._draw_menu()
        elif self.state == 'playing':
            self.maze.draw(self.screen)
            self.player.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.scoreboard.draw_hud(self.screen, self.score, self.level, self.lives)
        elif self.state == 'dying':
            self.maze.draw(self.screen)
            if self.flash_timer % 10 < 5:
                self.player.draw(self.screen)
            for g in self.ghosts:
                g.draw(self.screen)
            self.scoreboard.draw_hud(self.screen, self.score, self.level, self.lives)
        elif self.state == 'level_transition':
            self._draw_level_transition()
            self.scoreboard.draw_hud(self.screen, self.score, self.level, self.lives)
        elif self.state == 'game_over':
            self._draw_game_over()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
