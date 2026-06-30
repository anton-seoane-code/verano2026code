import math
import pygame
from constants import *

class AIController:
    def __init__(self, player):
        self.player = player
        self.think_timer = 0
        self.target = None
        self.dodge_timer = 0

    def get_keys(self, aliens, players):
        keys = {self.player.controls[k]: False for k in
                ["up", "down", "left", "right", "shoot"]}

        if not self.player.alive:
            return keys

        self.think_timer -= 1
        if self.think_timer <= 0:
            self._think(aliens, players)
            self.think_timer = AI_THINK_INTERVAL

        if self.target:
            dx = self.target.x - self.player.x
            dy = self.target.y - self.player.y
            dist = math.hypot(dx, dy)

            if abs(dx) > 5:
                keys[self.player.controls["right"]] = dx > 0
                keys[self.player.controls["left"]] = dx < 0
            if abs(dy) > 5:
                keys[self.player.controls["down"]] = dy > 0
                keys[self.player.controls["up"]] = dy < 0

            if dist < 300 and self.target.active:
                keys[self.player.controls["shoot"]] = True

        return keys

    def _think(self, aliens, players):
        closest = None
        min_dist = float("inf")
        for a in aliens:
            if a.active:
                d = math.hypot(a.x - self.player.x, a.y - self.player.y)
                if d < min_dist:
                    min_dist = d
                    closest = a
        self.target = closest

        for a in aliens:
            if not a.active:
                continue
            d = math.hypot(a.x - self.player.x, a.y - self.player.y)
            if d < 80:
                self.dodge_timer = 20

        if self.dodge_timer > 0:
            self.dodge_timer -= 1
