import random
import pygame
from constants import *
from player import Player
from alien import Alien
from bullet import Bullet
from powerup import PowerUp
from ai import AIController
from config import Config

CONTROL_SCHEMES = [
    {
        "up": pygame.K_UP, "down": pygame.K_DOWN,
        "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
        "shoot": pygame.K_RCTRL,
    },
    {
        "up": pygame.K_w, "down": pygame.K_s,
        "left": pygame.K_a, "right": pygame.K_d,
        "shoot": pygame.K_SPACE,
    },
    {
        "up": pygame.K_i, "down": pygame.K_k,
        "left": pygame.K_j, "right": pygame.K_l,
        "shoot": pygame.K_p,
    },
    {
        "up": pygame.K_KP5, "down": pygame.K_KP2,
        "left": pygame.K_KP1, "right": pygame.K_KP3,
        "shoot": pygame.K_KP0,
    },
]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Alien Conquer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.config = Config()
        self.state = "title"
        self.players = []
        self.aliens = []
        self.powerups = []
        self.ai_controllers = []
        self.font_large = pygame.font.Font(None, 72)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.credits_scroll = 0
        self.selected_menu = 0
        self.bullettime_global = False

        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.joysticks.append(j)

    def run(self):
        while self.running:
            if self.state == "title":
                self._title_screen()
            elif self.state == "playing":
                self._game_loop()
            elif self.state == "game_over":
                self._game_over_screen()
            elif self.state == "credits":
                self._credits_screen()
            elif self.state == "config":
                self._config_screen()
            elif self.state == "how_to_play":
                self._how_to_play_screen()
        pygame.quit()

    def _start_game(self, num_players, num_aliens):
        self.players = []
        self.aliens = []
        self.powerups = []
        self.ai_controllers = []
        self.bullettime_global = False
        total_ships = num_players

        for i in range(total_ships):
            angle = (360 / total_ships) * i
            rad = math.radians(angle)
            dist = 100
            x = SCREEN_WIDTH // 2 + math.cos(rad) * dist
            y = SCREEN_HEIGHT // 2 + math.sin(rad) * dist
            controls = CONTROL_SCHEMES[i] if i < len(CONTROL_SCHEMES) else CONTROL_SCHEMES[0]
            p = Player(i, x, y, controls)
            self.players.append(p)
            if i >= num_players:
                ai = AIController(p)
                self.ai_controllers.append(ai)

        for _ in range(num_aliens):
            self._spawn_alien()

    def _spawn_alien(self):
        x = random.randint(ALIEN_SIZE, SCREEN_WIDTH - ALIEN_SIZE)
        y = random.randint(ALIEN_SIZE, SCREEN_HEIGHT // 2)
        color = random.choice(PLAYER_COLORS)
        self.aliens.append(Alien(x, y, color))

    def _game_loop(self):
        playing = True
        while playing and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

            keys = pygame.key.get_pressed()
            for ai in self.ai_controllers:
                ai_keys = ai.get_keys(self.aliens, self.players)
                for k, v in ai_keys.items():
                    keys[k] = keys[k] or v

            for p in self.players:
                p.update(keys, self.aliens)

            for a in self.aliens[:]:
                a.update(self.players)
                if not a.active:
                    self.aliens.remove(a)

            for pu in self.powerups[:]:
                pu.update()
                if not pu.active:
                    self.powerups.remove(pu)

            self._check_collisions()

            if random.random() < POWERUP_SPAWN_CHANCE:
                self.powerups.append(PowerUp.spawn_random())

            while len(self.aliens) < self.config.get("num_aliens"):
                self._spawn_alien()

            alive_count = sum(1 for p in self.players if p.alive)
            if alive_count <= 0:
                playing = False
                self.state = "game_over"

            self._draw_game()
            self.clock.tick(FPS)

    def _check_collisions(self):
        for p in self.players:
            if not p.alive:
                continue
            pr = p.get_rect()
            for a in self.aliens[:]:
                if not a.active:
                    continue
                if pr.colliderect(a.get_rect()):
                    if p.invincible_timer > 0:
                        continue
                    if self._can_resurrect(p):
                        continue
                    p.die()
                    a.active = False

            for b in p.bullets[:]:
                if not b.active:
                    continue
                br = pygame.Rect(b.x - b.size, b.y - b.size,
                                 b.size * 2, b.size * 2)
                for a in self.aliens[:]:
                    if not a.active:
                        continue
                    if br.colliderect(a.get_rect()):
                        b.active = False
                        a.color = p.color
                        if a.color == p.color:
                            p.score += SCORE_SAME_COLOR
                        else:
                            p.score += SCORE_DIFF_COLOR
                        a.active = False

            for pu in self.powerups[:]:
                if pr.colliderect(pu.get_rect()):
                    if pu.kind == "laser":
                        p.laser_active = True
                        p.laser_timer = POWERUP_DURATION
                    elif pu.kind == "bullettime":
                        p.bullettime_active = True
                        p.bullettime_timer = POWERUP_DURATION
                    pu.active = False

        for i, p1 in enumerate(self.players):
            if not p1.alive:
                continue
            for p2 in self.players[i + 1:]:
                if not p2.alive:
                    continue
                if p1.get_rect().colliderect(p2.get_rect()):
                    pass

    def _can_resurrect(self, player):
        if any(p.score > player.score for p in self.players if p != player):
            return False
        player.resurrect()
        return True

    def _draw_game(self):
        self.screen.fill(BLACK)
        for a in self.aliens:
            a.draw(self.screen)
        for pu in self.powerups:
            pu.draw(self.screen)
        for p in self.players:
            p.draw(self.screen)
        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        y = 10
        for i, p in enumerate(self.players):
            color = PLAYER_COLORS[i]
            name = COLOR_NAMES[i]
            text = f"{name}: {p.score}  Lives: {p.lives}"
            if not p.active:
                text += " [DEAD]"
            surf = self.font_small.render(text, True, color)
            self.screen.blit(surf, (10, y))
            y += 22

    def _title_screen(self):
        self.selected_menu = self.selected_menu % 4
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_menu = (self.selected_menu - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        self.selected_menu = (self.selected_menu + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if self.selected_menu == 0:
                            n = self.config.get("num_players")
                            a = self.config.get("num_aliens")
                            self._start_game(n, a)
                            self.state = "playing"
                            return
                        elif self.selected_menu == 1:
                            self.state = "how_to_play"
                            return
                        elif self.selected_menu == 2:
                            self.state = "config"
                            return
                        elif self.selected_menu == 3:
                            self.state = "credits"
                            return

            self.screen.fill(BLACK)
            title = self.font_large.render("ALIEN CONQUER", True, (0, 255, 0))
            tr = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(title, tr)

            items = ["Start Game", "How to Play", "Configuration", "Credits"]
            for i, item in enumerate(items):
                color = (255, 255, 0) if i == self.selected_menu else WHITE
                surf = self.font_med.render(item, True, color)
                sr = surf.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 50))
                self.screen.blit(surf, sr)

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
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.state = "title"

            self.screen.fill(BLACK)
            go = self.font_large.render("GAME OVER", True, (255, 50, 50))
            gr = go.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(go, gr)

            winner = max(self.players, key=lambda p: p.score)
            wt = self.font_med.render(
                f"{winner.color_name} wins with {winner.score} points!",
                True, winner.color)
            wr = wt.get_rect(center=(SCREEN_WIDTH // 2, 200))
            self.screen.blit(wt, wr)

            y = 280
            for p in sorted(self.players, key=lambda p: -p.score):
                st = self.font_med.render(
                    f"{p.color_name}: {p.score}", True, p.color)
                sr = st.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(st, sr)
                y += 40

            cont = self.font_small.render(
                "Press ENTER or ESC to continue", True, GRAY)
            cr = cont.get_rect(center=(SCREEN_WIDTH // 2, 500))
            self.screen.blit(cont, cr)

            pygame.display.flip()
            self.clock.tick(FPS)

    def _credits_screen(self):
        credits = [
            "ALIEN CONQUER",
            "",
            "Original concept by Taiua Pires",
            "",
            "Recreated from project description",
            "at pygame.org/project/584",
            "",
            "Original game features:",
            "- 1 to 4 player arcade action",
            "- AI opponent",
            "- Color-based alien scoring",
            "- Laser cannon & bullet time",
            "- Resurrection mechanic",
            "- Joystick support",
            "",
            "Controls:",
            "P1: Arrow keys + Right Ctrl",
            "P2: WASD + Space",
            "P3: JIKL + P",
            "P4: Numpad 1523 + Numpad 0",
            "",
            "Press ESC to return",
        ]
        waiting = True
        scroll = SCREEN_HEIGHT
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.state = "title"
                    elif event.key == pygame.K_UP:
                        scroll += 20
                    elif event.key == pygame.K_DOWN:
                        scroll -= 20

            scroll -= 1
            self.screen.fill(BLACK)
            y = scroll
            for line in credits:
                color = (255, 255, 0) if line == "ALIEN CONQUER" else WHITE
                surf = self.font_med.render(line, True, color)
                sr = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(surf, sr)
                y += 30

            if scroll < -len(credits) * 30:
                scroll = SCREEN_HEIGHT

            pygame.display.flip()
            self.clock.tick(FPS)

    def _how_to_play_screen(self):
        lines = [
            ("ALIEN CONQUER", (0, 255, 0)),
            ("", WHITE),
            ("GOAL: Be the last ship standing!", WHITE),
            ("", WHITE),
            ("SCORING", (255, 255, 0)),
            ("  Hit an alien of YOUR color -> +10 points", WHITE),
            ("  Hit an alien of a DIFFERENT color -> +20 points", WHITE),
            ("  Aliens switch to your color when hit", WHITE),
            ("", WHITE),
            ("RESURRECTION", (255, 255, 0)),
            ("  If you have the MOST points and get hit by", WHITE),
            ("  an alien, you resurrect instead of dying!", WHITE),
            ("", WHITE),
            ("POWER-UPS", (255, 255, 0)),
            ("  Blue diamond = Laser Cannon (rapid fire)", WHITE),
            ("  Red square = Bullet Time (slow motion)", WHITE),
            ("", WHITE),
            ("HOW TO SHOOT", (255, 255, 0)),
            ("  P1: Right Ctrl     P2: Space", WHITE),
            ("  P3: P              P4: Numpad 0", WHITE),
            ("", WHITE),
            ("CONTROLS", (255, 255, 0)),
            ("  P1: Arrow keys", WHITE),
            ("  P2: W/A/S/D", WHITE),
            ("  P3: I/J/K/L", WHITE),
            ("  P4: Numpad 1/5/2/3", WHITE),
            ("", WHITE),
            ("Press ESC to return", GRAY),
        ]
        waiting = True
        scroll_y = 0
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.state = "title"
                    elif event.key == pygame.K_UP:
                        scroll_y = min(scroll_y + 20, 0)
                    elif event.key == pygame.K_DOWN:
                        scroll_y -= 20

            self.screen.fill(BLACK)
            y = 30 + scroll_y
            for text, color in lines:
                surf = self.font_small.render(text, True, color)
                sr = surf.get_rect(topleft=(40, y))
                self.screen.blit(surf, sr)
                y += 24

            hint = self.font_small.render(
                "UP/DOWN to scroll | ESC to return", True, GRAY)
            hr = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
            self.screen.blit(hint, hr)

            pygame.display.flip()
            self.clock.tick(FPS)

    def _config_screen(self):
        options = [
            ("Number of Players", "num_players", 1, 4),
            ("Number of Aliens", "num_aliens", 5, 50),
        ]
        selected = 0
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.config.save()
                        waiting = False
                        self.state = "title"
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_LEFT:
                        label, key, mn, mx = options[selected]
                        val = self.config.get(key)
                        self.config.set(key, max(mn, val - 1))
                    elif event.key == pygame.K_RIGHT:
                        label, key, mn, mx = options[selected]
                        val = self.config.get(key)
                        self.config.set(key, min(mx, val + 1))

            self.screen.fill(BLACK)
            title = self.font_large.render("CONFIGURATION", True, (0, 255, 0))
            tr = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            self.screen.blit(title, tr)

            y = 200
            for i, (label, key, mn, mx) in enumerate(options):
                color = (255, 255, 0) if i == selected else WHITE
                val = self.config.get(key)
                txt = f"{label}: {val}"
                surf = self.font_med.render(txt, True, color)
                sr = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(surf, sr)
                y += 60

            hint = self.font_small.render(
                "Arrow keys to change | ESC to save and return",
                True, GRAY)
            hr = hint.get_rect(center=(SCREEN_WIDTH // 2, 500))
            self.screen.blit(hint, hr)

            pygame.display.flip()
            self.clock.tick(FPS)

import math
