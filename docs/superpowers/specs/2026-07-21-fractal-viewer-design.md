# Fractal Viewer — Design Document

**Date:** 2026-07-21
**Tech Stack:** Python (pygame + numpy + numba) and C (SDL2 + OpenGL + pthreads)
**Directory:** `fractal-viewer/`

## Overview

Dual-language high-performance Mandelbrot & Julia set viewer with real-time zoom/pan, smooth coloring, and perturbation theory for deep zooms (C only).

## Architecture

### Python version (`python/`)
| File | Responsibility |
|------|---------------|
| `main.py` | Pygame main loop, event handling, state management |
| `fractal.py` | Escape-time algorithm, smooth coloring, numba JIT |
| `renderer.py` | Pixel buffer → pygame Surface display |
| `viewport.py` | Complex plane math, zoom/pan, double precision |
| `palette.py` | Color gradient LUT for smooth coloring |

### C version (`c/`)
| File | Responsibility |
|------|---------------|
| `src/main.c` | SDL2+OpenGL init, event loop, fullscreen, screenshot |
| `src/fractal.c/h` | Escape-time + perturbation theory (long double reference) |
| `src/renderer.c/h` | CPU pixel buffer → OpenGL texture → fullscreen quad |
| `src/viewport.c/h` | Viewport state (long double center), zoom centered on cursor |
| `src/palette.c/h` | Precomputed color LUT, gradient generation |
| `src/worker.c/h` | pthread thread pool + AVX2 SIMD inner loops |

## Core Algorithm

Escape-time: `z_{n+1} = z_n^2 + c`, up to `max_iter`. Smooth coloring:
`color = N + 1 - log(log(|z|)) / log(2)`, mapped through gradient LUT.

## Interaction
- Mouse wheel: zoom centered on cursor
- Drag: pan
- M/J: toggle Mandelbrot / Julia sets
- Mouse move (Julia mode): update `c` parameter in real time
- F: fullscreen toggle
- S: screenshot (PNG)

## Performance Strategy
- Python: numba `@jit(nopython=True)` on inner iteration loop
- C: pthread thread pool (one per CPU core), AVX2 8-wide SIMD
- During drag: render at 25% resolution for responsive feedback
- C perturbation: single long double reference orbit, double deltas
