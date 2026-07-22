import numpy as np
import pygame

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = np.zeros((height, width, 3), dtype=np.uint8)
        self.surface = pygame.Surface((width, height))

    def update_surface(self):
        pygame.surfarray.blit_array(self.surface, self.pixels.swapaxes(0, 1))

    def draw(self, screen, low_res=False):
        if low_res:
            factor = 4
            lw = self.width // factor
            lh = self.height // factor
            small = np.zeros((lh, lw, 3), dtype=np.uint8)
            for y in range(lh):
                for x in range(lw):
                    small[y, x] = self.pixels[y * factor, x * factor]
            surf = pygame.Surface((lw, lh))
            pygame.surfarray.blit_array(surf, small.swapaxes(0, 1))
            pygame.transform.scale(surf, (self.width, self.height), self.surface)
        else:
            self.update_surface()
        screen.blit(self.surface, (0, 0))
        pygame.display.flip()
