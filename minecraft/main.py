import pygame
import sys
from OpenGL.GL import *

from blocks import BLOCK_TYPES
from renderer import Renderer
from world import World, WORLD_HEIGHT
from player import Player

WIDTH, HEIGHT = 800, 600
FOV = 75
NEAR = 0.1
FAR = 150.0

def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Minecraft")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    clock = pygame.time.Clock()

    world = World(seed=42)
    renderer = Renderer(WIDTH, HEIGHT)
    renderer.set_projection(FOV, NEAR, FAR)
    player = Player(world)
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            player.handle_event(event)

        player.update(dt)
        view_pos = player.pos.copy()
        view_pos[1] += 0.8
        renderer.set_view(view_pos, (player.yaw, player.pitch))
        chunks = world.get_chunks_in_range(player.pos[0], player.pos[2])
        renderer.render(chunks, view_pos)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
