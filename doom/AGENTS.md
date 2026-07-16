# Doom

This is a **Godot 4** game project created with **GenieEngine**, an AI-powered game engine.

GenieEngine gives the assistant its full build rules (scope, ECS architecture, asset
layout, file headers, testing tools) automatically while the app runs — those rules are
versioned with the app rather than stored here.

Use this file for project-specific notes the assistant should always know: game design
decisions, art direction, conventions, TODOs.

## Project

- **Genre**: 3D first-person shooter
- **ECS layout**: components/, entities/, systems/
- **Player**: WASD move, mouse look, left-click shoot
- **Enemies**: move toward player, deal contact damage (10/s), 50 HP each, detection range 30
- **Shooting**: raycast from camera, 25 damage, 0.3s fire rate, 100 range
- **Player HP**: 100, green health bar bottom-left, red when low
- **Enemy spawning**: new enemy every 15s in a random room (not center room)
- **Game Over**: label appears on death, click to restart
- **Enemies**: 5 placed in rooms around the level
- **Level**: 3×3 grid of 10×10 rooms with 2-unit doorways at center of each inner wall; 12 wall segments generated in _build_level()
- **Walls**: StaticBody3D with BoxShape3D + BoxMesh, dark gray material
- **Floor**: dark concrete-colored material
