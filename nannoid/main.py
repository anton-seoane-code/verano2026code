import pygame

from constants import *

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

    from game.level import Level

    level = Level()
    level.screen = screen
    level.score = 0
    level.cur = 1
    level.sissy = 0
    level.lives = LIVES
    level.bkgr_fname = None
    level.bkgr = None
    level.level_fname = f"{LEVEL_DIR}/{PLAY_LEVELS[level.cur]}.lvl"

    level.load()
    level.init_graphics()
    level.init()
    level.start()

    running = True
    while running:
        level.loop()
        if level.quit:
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
