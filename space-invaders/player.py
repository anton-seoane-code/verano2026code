import math
import pygame
from constants import *

class Player:
    def __init__(self, index, x, y, controls):
        self.index = index
        self.x = x
        self.y = y
        self.angle = 0
        self.color = PLAYER_COLORS[index]
        self.color_name = COLOR_NAMES[index]
        self.controls = controls
        self.score = 0
        self.lives = INITIAL_LIVES
        self.active = True
        self.respawn_timer = 0
        self.shoot_cooldown = 0
        self.bullets = []
        self.laser_active = False
        self.laser_timer = 0
        self.bullettime_active = False
        self.bullettime_timer = 0
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.invincible_timer = 0

    def update(self, keys, aliens):
        if not self.active:
            if self.respawn_timer > 0:
                self.respawn_timer -= 1
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if self.laser_timer > 0:
            self.laser_timer -= 1
        else:
            self.laser_active = False

        if self.bullettime_timer > 0:
            self.bullettime_timer -= 1
        else:
            self.bullettime_active = False

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        speed = self.speed
        dt = 0.5 if self.bullettime_active else 1.0

        dx = 0
        dy = 0
        if keys[self.controls["up"]]:
            dy = -speed * dt
        if keys[self.controls["down"]]:
            dy = speed * dt
        if keys[self.controls["left"]]:
            dx = -speed * dt
        if keys[self.controls["right"]]:
            dx = speed * dt

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx
        self.y += dy
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))

        if dx != 0 or dy != 0:
            self.angle = math.degrees(math.atan2(-dy, dx))

        if keys[self.controls["shoot"]] and self.shoot_cooldown == 0:
            self.shoot()

        for b in self.bullets[:]:
            b.update()
            if not b.active:
                self.bullets.remove(b)

    def shoot(self):
        if len(self.bullets) >= MAX_BULLETS:
            return
        rad = math.radians(self.angle)
        bx = self.x + math.cos(rad) * self.size
        by = self.y - math.sin(rad) * self.size
        self.bullets.append(Bullet(bx, by, self.angle, self.color, self.laser_active))
        self.shoot_cooldown = 10

    def draw(self, screen):
        if not self.active:
            return
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        pts = []
        for i in range(3):
            angle_deg = self.angle + 120 * i
            rad = math.radians(angle_deg)
            r = self.size if i == 0 else self.size * 0.6
            pts.append((self.x + math.cos(rad) * r,
                        self.y - math.sin(rad) * r))
        pygame.draw.polygon(screen, self.color, pts)
        pygame.draw.polygon(screen, WHITE, pts, 1)

        for b in self.bullets:
            b.draw(screen)

    def die(self):
        self.lives -= 1
        if self.lives > 0:
            self.respawn_timer = 60
            self.active = True
            self.invincible_timer = 90
            self.x = SCREEN_WIDTH // 2
            self.y = SCREEN_HEIGHT // 2
        else:
            self.active = False

    def resurrect(self):
        self.lives = max(self.lives, 1)
        self.active = True
        self.respawn_timer = 0
        self.invincible_timer = 90
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)

    @property
    def alive(self):
        return self.active and self.respawn_timer == 0

from bullet import Bullet
