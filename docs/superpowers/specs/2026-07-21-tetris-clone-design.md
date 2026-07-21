# Tetris Clone — Design Document

**Date:** 2026-07-21
**Technology:** Python 3 + Pygame
**Directory:** `tetris-clone/`

## Overview

A Tetris game clone built with pygame, featuring a persistent scoreboard and level-based difficulty progression (phases). All graphics rendered with `pygame.draw` primitives.

## Architecture

Six modules:

| File | Responsibility |
|------|---------------|
| `main.py` | Entry point |
| `game.py` | State machine, game loop, input, update, render |
| `board.py` | 10×20 grid, collision detection, line clearing |
| `tetromino.py` | Piece shapes, rotation (SRS-style), movement |
| `scoreboard.py` | High score persistence (pickle, top 5), name entry |
| `constants.py` | Colors, sizes, speeds, SRS kick tables, shapes |

## Phases (Levels)

- Level increases every 10 lines cleared
- Speed formula: `LEVEL_SPEEDS[level-1]` — 800ms at level 1 down to 50ms at level 10+
- Level-up transition: 1.5s overlay showing "LEVEL N!" before play resumes

## Scoring

- Soft drop: +1 per row
- Hard drop: +2 per row
- Line clear: 100/300/500/800 × level for 1/2/3/4 lines

## Scoreboard

- Persistent via pickle to `tetris.high`
- Top 5 entries with name, score, level
- Name entry: 3-letter input on game over if score qualifies
- Displayed on title screen and after game over

## Controls

- ← → : Move left/right
- ↑ : Rotate clockwise
- Z : Rotate counter-clockwise
- ↓ : Soft drop
- Space : Hard drop
- C : Hold piece
- P : (reserved for pause)

## Game States

MENU → PLAYING ↔ LEVEL_TRANSITION → GAME_OVER → NAME_ENTRY → SCOREBOARD → MENU

## Rendering

- Grid: dark background with subtle grid lines
- Pieces: colored blocks with lighter highlight on top/left edges
- Ghost piece: dimmed outline at drop preview
- Sidebar: score, level, lines, next piece, hold piece
- All graphics via `pygame.draw` primitives (no external assets)
