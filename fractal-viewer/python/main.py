import sys
import pygame
from viewport import Viewport
from fractal import render_fractal
from renderer import Renderer
from palette import make_palette

WIDTH, HEIGHT = 800, 600
MAX_ITER = 256

class FractalApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fractal Viewer")
        self.clock = pygame.time.Clock()
        self.viewport = Viewport(WIDTH, HEIGHT)
        self.renderer = Renderer(WIDTH, HEIGHT)
        self.palette = make_palette(1024)
        self.julia_mode = False
        self.julia_cx = 0.0
        self.julia_cy = 0.0
        self.dragging = False
        self.last_mouse = (0, 0)
        self.fullscreen = False
        self.needs_rerender = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.julia_mode = False
                    self.needs_rerender = True
                elif event.key == pygame.K_j:
                    self.julia_mode = True
                    self.julia_cx, self.julia_cy = -0.7, 0.27015
                    self.needs_rerender = True
                elif event.key == pygame.K_f:
                    self.fullscreen = not self.fullscreen
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_s:
                    self.save_screenshot()
                elif event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse = event.pos
                elif event.button == 4:
                    mx, my = event.pos
                    self.viewport.zoom_at(mx, my, 1.1)
                    self.needs_rerender = True
                elif event.button == 5:
                    mx, my = event.pos
                    self.viewport.zoom_at(mx, my, 1.0 / 1.1)
                    self.needs_rerender = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            if event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mx, my = event.pos
                    dx = mx - self.last_mouse[0]
                    dy = my - self.last_mouse[1]
                    self.viewport.pan(dx, dy)
                    self.last_mouse = event.pos
                    self.render(True)
                if self.julia_mode:
                    mx, my = event.pos
                    self.julia_cx, self.julia_cy = self.viewport.screen_to_complex(mx, my)
                    self.needs_rerender = True
        return True

    def render(self, low_res=False):
        render_fractal(
            self.renderer.pixels, WIDTH, HEIGHT,
            self.viewport.cx, self.viewport.cy, self.viewport.zoom,
            MAX_ITER, self.palette,
            self.julia_mode, self.julia_cx, self.julia_cy,
        )
        self.renderer.draw(self.screen, low_res)

    def save_screenshot(self):
        import datetime
        name = f"fractal_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
        pygame.image.save(self.screen, name)
        print(f"Screenshot saved: {name}")

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if self.needs_rerender:
                self.render()
                self.needs_rerender = False
            self.clock.tick(60)
        pygame.quit()

def main():
    app = FractalApp()
    app.run()

if __name__ == "__main__":
    main()
