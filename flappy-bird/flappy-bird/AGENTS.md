# Flappy Bird

This is a **Godot 4** game project created with **GenieEngine**, an AI-powered game engine.

GenieEngine gives the assistant its full build rules (scope, ECS architecture, asset
layout, file headers, testing tools) automatically while the app runs — those rules are
versioned with the app rather than stored here.

Use this file for project-specific notes the assistant should always know: game design
decisions, art direction, conventions, TODOs.

## Game design
- Bird at x=200, flaps with Space/left click.
- Pipes scroll from right at 200 px/s, spawn every 1.6s, gap 150px, gap Y range 150–420.
- Ground scrolls at 100 px/s, top at y=536.
- Gravity 980, flap strength -330, max fall 600.
- Game over on pipe collision (Area2D body overlap) or ground hit (y ≥ 536).
- Restart by tapping Space/click after game over (reloads scene).
- Score increments when pipe pair's x passes bird's x.
