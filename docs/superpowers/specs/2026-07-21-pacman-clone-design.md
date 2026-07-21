# Pac-Man Clone — Design Document

## Overview
Faithful classic Pac-Man recreation in Python/Pygame. Single-player arcade game with maze navigation, dot collection, ghost AI, scoreboard, and level progression.

## Tech Stack
- **Language**: Python 3
- **Framework**: Pygame 2.x
- **Rendering**: `pygame.draw` primitives (no sprite sheets)

## Architecture

```
pacman-clone/
├── main.py          # Entry point
├── constants.py     # Colors, sizes, maze layout, game constants
├── maze.py          # Maze loading, tile grid, collision queries
├── player.py        # Pac-Man movement, input, rendering
├── ghost.py         # Ghost base + 4 types with distinct AI
├── game.py          # Game state machine, HUD, level logic
├── scoreboard.py    # High score persistence (pickle)
└── requirements.txt  # pygame dependency
```

## Game Mechanics

### Maze
- 28×31 tile grid, tile size 20px = 560×620 game area + 40px HUD = 560×660 screen
- Tile types: WALL, DOT, PELLET, EMPTY, TUNNEL, GHOST_WALL, GHOST_INTERIOR, GHOST_DOOR
- Tunnel wraps left edge ↔ right edge on row 13
- Ghost house in center area (rows 10-12, cols 11-16) with door at (13,12),(14,12)

### Player (Pac-Man)
- Arrow keys / WASD control
- Tile-aligned movement with direction buffering
- Yellow circle with animated mouth
- Starts at (14, 28)

### Ghost AI — 4 Distinct Behaviors

| Ghost | Color | Target Strategy |
|-------|-------|-----------------|
| **Blinky** | Red | Direct chase → Pac-Man's current tile |
| **Pinky** | Pink | Ambush → 4 tiles ahead of Pac-Man |
| **Inky** | Cyan | Flanking → 2× vector from Blinky to 2 tiles ahead |
| **Clyde** | Orange | Shy → chase if >8 tiles away, else scatter corner |

- **Scatter mode**: ghosts patrol their corners (periodic, ~7s)
- **Chase mode**: ghosts use individual targeting (periodic, ~20s)
- **Frightened mode**: after eating power pellet (~6s), ghosts turn blue, slow down, reverse direction
- **Eaten mode**: eyes return to ghost house at high speed
- Pathfinding: Manhattan distance minimization at intersections

### Scoring
- Dot: 10 pts
- Power pellet: 50 pts (activates frightened mode)
- Ghost: 200→400→800→1600 pts (doubles per ghost during one pellet)
- Extra life at 10,000 pts
- High score persisted to `pacman.high` (top 5)

### Level Progression
- Ghost speed: +5% per level
- Power pellet duration: -0.5s per level (min 1s)
- Scatter duration: -0.5s per level (min 1s)

### States
- MENU → PLAYING → DYING → PLAYING (respawn) or GAME_OVER → MENU
- PLAYING → LEVEL_TRANSITION → PLAYING (next level)

## Dependencies
- pygame (≥2.0.0)

## Run
```bash
pip install -r requirements.txt
python main.py
```
