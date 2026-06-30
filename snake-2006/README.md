# Snake 2006

A classic Snake game recreation based on the project by Cifa
([pygame.org/project/433](https://www.pygame.org/project/433)).

Eat red food for points, grab blue bonuses before they disappear,
avoid walls and yourself!

## Changelog

All notable changes to this project are documented below.

### [1.0.0] — 2026-06-30

#### Added
- Initial project skeleton with directory structure
- `main.py` — game entry point
- `game.py` — main game class with state machine (start, playing, game over)
- `snake.py` — snake class stub
- `food.py` — red food and blue bonus stubs
- `constants.py` — game constants
- `requirements.txt` — pygame dependency

### [1.1.0] — 2026-06-30

#### Added
- Full `snake.py` implementation:
  - Grid-based segment list with (x, y) coordinate tracking
  - Direction queue for buffering multiple direction changes per frame
  - Grid-aligned movement with grow flag for length increase
  - Self-collision detection (head vs body)
  - Wall collision detection (out of bounds)
  - Head drawn with DARK_GREEN outline + GREEN fill + white eye
  - Body segments drawn as green rects with dark green border

### [1.2.0] — 2026-06-30

#### Added
- Full `food.py` implementation:
  - `RedFood` — permanent until eaten, spawns on random empty cell, drawn as red square with yellow center
  - `BlueBonus` — spawns briefly (120 frames), blinks when about to disappear, drawn as blue square with white center
  - Both avoid spawning on snake body

### [1.3.0] — 2026-06-30

#### Added
- Full `game.py` implementation:
  - Grid-based movement with timing interval (MOVE_INTERVAL=8 frames)
  - Collision detection: wall death, self-bite death, red food (+1 + grow), blue bonus (+5 + grow)
  - Pause toggle with 'P' key and overlay
  - Blue bonus auto-spawns every 2-5 seconds
  - Grid line background
  - Score HUD (top-left) and high score display (top-right)
  - High score persistence via `snake_2006.high` file
