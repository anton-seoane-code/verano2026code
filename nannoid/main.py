import sys
import pygame

from constants import W, H, FPS
from engine.gameloop import GameLoop

def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    pygame.display.set_caption("Nannoid")
    try:
        icon = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon)
    except:
        pass

    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    game = GameLoop(screen, clock)
    game.run()

if __name__ == "__main__":
    main()
