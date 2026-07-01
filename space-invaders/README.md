# Alien Conquer

A 1-4 player arcade space shooter based on the game by Taiua Pires
([pygame.org/project/584](https://www.pygame.org/project/584)).

The goal is to be the last ship standing. Destroy aliens, score points,
collect power-ups, and outlast your opponents!

## Changelog

All notable changes to this project are documented below.

### [1.0.0] — 2026-07-01

#### Added
- Initial project release — full recreation of Alien Conquer by Taiua Pires
- `main.py` — game entry point
- `game.py` — main game loop with state machine (title, playing, game over, credits, config)
- `player.py` — player ship with 8-directional movement, shooting, lives, and power-up state
- `alien.py` — alien enemies with steering AI toward nearest player
- `bullet.py` — projectile system supporting normal and laser shots
- `powerup.py` — two power-ups: blue laser cannon and red bullet time
- `ai.py` — AI controller for computer-controlled opponents with targeting and dodging
- `config.py` — JSON-based config save/load (`alien_conquer.cfg`)
- `constants.py` — centralized game constants
- `requirements.txt` — pygame dependency declaration
- 4 keyboard control schemes (P1: arrows+RCTRL, P2: WASD+SPACE, P3: JIKL+P, P4: numpad)
- Automatic joystick detection and configuration
- Title screen with menu navigation (Start, How to Play, Config, Credits)
- Game over screen with winner announcement and scoreboard
- Credits screen with auto-scrolling text (UP/DOWN to control scroll speed)
- Configuration screen (number of players, number of aliens)
- HUD showing score and lives for each player
- Full collision detection: player-alien, bullet-alien, player-powerup, player-player
- Alien respawn system maintaining minimum alien count
- Alien color-switching on hit; scoring: +10 same color, +20 different color
- Resurrection mechanic — leading player revives instead of dying
- Invincibility frames on respawn (90 frames with flashing effect)
- All graphics rendered with `pygame.draw` primitives (no external assets)
