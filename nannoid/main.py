import sys
import pygame

from constants import W, H, FPS, LEVEL_DIR, PLAY_LEVELS
from engine.gameloop import GameLoop, loop_delay, loop_update

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

    from game.level import Level
    level = Level()
    level.screen = screen
    level.score = 0
    level.cur = 1
    level.sissy = 0

    level.bkgr_fname = None
    level.bkgr = None
    level.level_fname = f"{LEVEL_DIR}/{PLAY_LEVELS[level.cur]}.lvl"

    level.load()
    level.init_graphics()
    level.init()

    state = 'menu'
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        loop_delay(level)
        level.paint(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
