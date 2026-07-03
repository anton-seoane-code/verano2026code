import pygame
import sys
import numpy as np
from OpenGL.GL import *

from blocks import BLOCK_TYPES
from renderer import Renderer
from world import World, WORLD_HEIGHT
from player import Player

WIDTH, HEIGHT = 800, 600
FOV = 75
NEAR = 0.1
FAR = 150.0

def make_sound(freq, duration, volume=0.3):
    sample_rate = 22050
    samples = int(sample_rate * duration)
    mono = (volume * 32767 * np.sin(2 * np.pi * freq * np.arange(samples) / sample_rate) *
            np.exp(-3 * np.arange(samples) / samples)).astype(np.int16)
    stereo = np.column_stack([mono, mono])
    return pygame.sndarray.make_sound(stereo)

def draw_hud(screen, player, hit_pos):
    w, h = screen.get_size()
    cx, cy = w // 2, h // 2
    color = (255, 255, 255)
    pygame.draw.line(screen, color, (cx - 8, cy), (cx - 3, cy), 2)
    pygame.draw.line(screen, color, (cx + 3, cy), (cx + 8, cy), 2)
    pygame.draw.line(screen, color, (cx, cy - 8), (cx, cy - 3), 2)
    pygame.draw.line(screen, color, (cx, cy + 3), (cx, cy + 8), 2)
    font = pygame.font.Font(None, 18)
    coord_text = font.render(
        f"Pos: ({player.pos[0]:.1f}, {player.pos[1]:.1f}, {player.pos[2]:.1f})",
        True, (255, 255, 255), (0, 0, 0, 128)
    )
    screen.blit(coord_text, (10, 10))
    bar_y = h - 50
    bar_h = 36
    total_w = 7 * 40
    bx = (w - total_w) // 2
    block_ids = [1, 3, 5, 7, 8, 4, 6]
    for i, bid in enumerate(block_ids):
        bt = BLOCK_TYPES.get(bid)
        if not bt:
            continue
        x = bx + i * 40
        sel = (i + 1) == player.selected_block or \
              (player.selected_block == bid)
        outline = (255, 255, 255) if (i + 1) == player.selected_block else (80, 80, 80)
        bg = (50, 50, 50) if (i + 1) == player.selected_block else (30, 30, 30)
        pygame.draw.rect(screen, bg, (x, bar_y, 38, bar_h))
        pygame.draw.rect(screen, outline, (x, bar_y, 38, bar_h), 2)
        name = bt['name'][:5]
        label = font.render(name, True, (200, 200, 200))
        screen.blit(label, (x + 4, bar_y + 4))
        key_l = font.render(str(i + 1), True, (150, 150, 150))
        screen.blit(key_l, (x + 4, bar_y + 20))

    if hit_pos:
        hx, hy, hz = hit_pos
        hit_text = font.render(
            f"Target: ({hx}, {hy}, {hz})",
            True, (255, 255, 255), (0, 0, 0, 128)
        )
        screen.blit(hit_text, (10, 30))

def main():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Minecraft (Python/OpenGL)")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    clock = pygame.time.Clock()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    sounds = {
        'place': make_sound(300, 0.1, 0.2),
        'break': make_sound(150, 0.15, 0.25),
    }

    world = World(seed=42)
    renderer = Renderer(WIDTH, HEIGHT)
    renderer.set_projection(FOV, NEAR, FAR)
    player = Player(world)
    hit_pos = None
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            player.handle_event(event, sounds)

        player.update(dt)
        hit = player.raycast()
        hit_pos = hit['block'] if hit else None

        view_pos = player.pos.copy()
        view_pos[1] += 0.8
        renderer.set_view(view_pos, (player.yaw, player.pitch))
        chunks = world.get_chunks_in_range(player.pos[0], player.pos[2])
        renderer.render(chunks, view_pos, hit_pos)

        overlay.fill((0, 0, 0, 0))
        draw_hud(overlay, player, hit_pos)
        screen = pygame.display.get_surface()
        screen.blit(overlay, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
