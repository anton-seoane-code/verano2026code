# Nannoid

An Arkanoid / Breakout clone with space graphics. Originally created by Phil Hassey in 2005.

This is a modern Python/pygame recreation using the original assets.

## Commit Log

### Commit 1-4: Skeleton, engine, paddle+ball, blocks
- Created project structure (engine/, game/, screens/, assets/)
- Engine: tilemap.py, sprite.py, collision.py (separate X/Y tile hits), gameloop.py
- Level loader (.lvl format), tile definitions (IDs 0-9, 13-15, 16-23, 32-39, 40-47)
- Animation chains, block_explode (tile 7 bomb), block_shadow
- Paddle: mouse+arrows, smooth width transitions, type system (p/l/c/e/3)
- Ball: velocity physics, angle quantization (6° from axes), wall/block bounce
- Original assets installed (13 images, 14 sfx WAVs, 50 level files, font, tiles.png)

### Commit 5: Power-ups, lasers, junk enemies, SFX
- Pill drop on block explosion (random 1/n chance, configurable via PILL_DROP_CHANCE)
- 6 pill types: Enlarge (E), Slow (S), Laser (L), Catch (C), Multi-ball (3), Extra Life (P)
- Laser system: fires 2 lasers from paddle ends on space/click when laser pill active
- Junk enemies: 3 types (sphere/pyramid/cubes), bounce off walls, defeated by ball/laser
- SFX loading: 14 WAV files loaded at Level init, played on events (bang/snap/blip/bew/woop)
- All gameplay elements integrated into level.py loop (sparkle, animation, clayer, junk spawn)

## Controls

| Key | Action |
|---|---|
| Mouse | Move paddle |
| Left/Right arrows | Move paddle |
| Left click / Space | Release ball / Fire laser |
| P / Return | Pause |
| Escape | Quit to menu |
| F12 | Skip level (debug) |

## Power-ups

| Pill | Effect |
|---|---|
| Enlarge (E) | Widen paddle |
| Slow (S) | Reset ball speed |
| Laser (L) | Paddle fires lasers |
| Catch (C) | Ball sticks to paddle |
| Extra Life (P) | +1 life |
| Multi-ball (3) | +2 extra balls |

## Scoring

| Event | Points |
|---|---|
| Brick destroyed | 11 |
| Pill caught | 37 |
| Enemy destroyed | 23 |
| Ball hit | 3 |
| Extra life | Every 20,000 points |

## Credits

- Phil Hassey — original code, graphics, SFX, level design
- Luke Ulrich — Blender tutorial
- Daniel Nicholson — music (not included)
