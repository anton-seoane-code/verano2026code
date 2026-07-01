import pygame
from pygame.locals import *
from constants import FPS

class GameLoop:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = False
        self.state = None
        self.states = {}

    def run(self):
        self.running = True
        while self.running:
            if self.state:
                self.state = self.state()
            else:
                self.running = False

    def quit(self):
        self.running = False
