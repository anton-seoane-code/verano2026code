import random
import pygame
from constants import *
from snake import Snake
from food import RedFood, BlueBonus

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake 2006")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "start"
        self.score = 0
        self.high_score = self._load_high_score()
        self.move_timer = 0
        self.paused = False
        self.snake = Snake()
        self.red_food = RedFood()
        self.blue_bonus = BlueBonus()
        self.font_large = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def run(self):
        while self.running:
            if self.state == "start":
                self._start_screen()
            elif self.state == "playing":
                self._game_loop()
            elif self.state == "game_over":
                self._game_over_screen()
        pygame.quit()

    def _start_game(self):
        self.score = 0
        self.move_timer = 0
        self.paused = False
        self.snake = Snake()
        self.red_food = RedFood()
        self.blue_bonus = BlueBonus()
        self.red_food.respawn(self.snake.get_body_set())

    def _game_loop(self):
        playing = True
        blue_spawn_timer = random.randint(60, 180)
        while playing and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:
                        self.snake.set_direction("up")
                    elif event.key == pygame.K_DOWN:
                        self.snake.set_direction("down")
                    elif event.key == pygame.K_LEFT:
                        self.snake.set_direction("left")
                    elif event.key == pygame.K_RIGHT:
                        self.snake.set_direction("right")

            if not self.paused:
                self.move_timer += 1
                if self.move_timer >= MOVE_INTERVAL:
                    self.move_timer = 0
                    self.snake.update()
                    if self._check_collisions():
                        playing = False
                        self.state = "game_over"

                blue_spawn_timer -= 1
                if blue_spawn_timer <= 0 and not self.blue_bonus.active:
                    self.blue_bonus.spawn(self.snake.get_body_set())
                    blue_spawn_timer = random.randint(120, 300)

                self.blue_bonus.update()

            self._draw()
            self.clock.tick(FPS)

    def _check_collisions(self):
        head = self.snake.get_head()

        if self.snake.check_wall_collision():
            self._save_high_score()
            return True

        if self.snake.check_self_collision():
            self._save_high_score()
            return True

        if head == self.red_food.get_pos():
            self.score += RED_FOOD_SCORE
            self.snake.grow()
            self.red_food.respawn(self.snake.get_body_set())

        if self.blue_bonus.active and head == self.blue_bonus.get_pos():
            self.score += BLUE_BONUS_SCORE
            self.snake.grow()
            self.blue_bonus.active = False

        return False

    def _draw(self):
        self.screen.fill(BLACK)

        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

        self.red_food.draw(self.screen)
        self.blue_bonus.draw(self.screen)
        self.snake.draw(self.screen)

        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        hs_text = self.font_small.render(f"High: {self.high_score}", True, YELLOW)
        hs_rect = hs_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        self.screen.blit(hs_text, hs_rect)

        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            pause_text = self.font_large.render("PAUSED", True, WHITE)
            pr = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pr)
            hint = self.font_small.render("Press P to resume", True, GRAY)
            hr = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(hint, hr)

        pygame.display.flip()

    def _start_screen(self):
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self._start_game()
                        self.state = "playing"
                        return

            self.screen.fill(BLACK)
            title = self.font_large.render("SNAKE 2006", True, GREEN)
            tr = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(title, tr)

            info_lines = [
                "Arrow keys to move",
                "P to pause",
                "Red food = 1 point",
                "Blue bonus = 5 points (disappears fast!)",
                "Don't hit the wall or yourself",
            ]
            y = 260
            for line in info_lines:
                surf = self.font_small.render(line, True, WHITE)
                sr = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(surf, sr)
                y += 35

            prompt = self.font_med.render("Press ENTER to start", True, YELLOW)
            pr = prompt.get_rect(center=(SCREEN_WIDTH // 2, 480))
            self.screen.blit(prompt, pr)

            hs = self.font_small.render(f"High Score: {self.high_score}", True, YELLOW)
            hr = hs.get_rect(center=(SCREEN_WIDTH // 2, 530))
            self.screen.blit(hs, hr)

            pygame.display.flip()
            self.clock.tick(FPS)

    def _game_over_screen(self):
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        waiting = False
                        self.state = "start"
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.state = "start"

            self.screen.fill(BLACK)
            go = self.font_large.render("GAME OVER", True, RED)
            gr = go.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(go, gr)

            score = self.font_med.render(f"Score: {self.score}", True, WHITE)
            sr = score.get_rect(center=(SCREEN_WIDTH // 2, 250))
            self.screen.blit(score, sr)

            if self.score >= self.high_score:
                new = self.font_med.render("NEW HIGH SCORE!", True, YELLOW)
                nr = new.get_rect(center=(SCREEN_WIDTH // 2, 300))
                self.screen.blit(new, nr)
            else:
                hs = self.font_small.render(f"High Score: {self.high_score}", True, YELLOW)
                hr = hs.get_rect(center=(SCREEN_WIDTH // 2, 300))
                self.screen.blit(hs, hr)

            prompt = self.font_small.render("Press ENTER or ESC to continue", True, GRAY)
            pr = prompt.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(prompt, pr)

            pygame.display.flip()
            self.clock.tick(FPS)

    def _load_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            try:
                with open(HIGH_SCORE_FILE, "w") as f:
                    f.write(str(self.high_score))
            except IOError:
                pass
