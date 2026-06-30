# Alien Conquer

A 1-4 player arcade space shooter based on the game by Taiua Pires
([pygame.org/project/584](https://www.pygame.org/project/584)).

The goal is to be the last ship standing. Destroy aliens, score points,
collect power-ups, and outlast your opponents!

## Changelog

### 2026-06-30 — Commit 1: Project skeleton
- Initial project setup with directory structure
- `main.py` — entry point
- `game.py` — main game class with state machine (title, playing, game over, credits, config)
- `player.py` — player ship with movement, shooting, lives, power-up state
- `alien.py` — alien enemies with AI movement
- `bullet.py` — projectile system
- `powerup.py` — laser cannon and bullet time power-ups
- `ai.py` — AI controller for computer players
- `config.py` — config save/load to JSON file
- `constants.py` — all game constants
- `requirements.txt` — pygame dependency
- Control schemes for 4 players (keyboard + joystick support)
- Title screen, game over screen, credits screen, configuration screen
- Full collision detection (player-alien, bullet-alien, player-powerup, player-player)
- Scoring: +10 for matching color, +20 for different color
- Resurrection mechanic: leading player revives on hit
- Complete game loop with spawning, power-up drops, and HUD
