# Fractal Viewer

High-performance Mandelbrot & Julia set viewer with real-time zoom and pan. Implemented in both **Python** (pygame + numpy + numba) and **C** (SDL2 + OpenGL + pthreads + AVX2).

## Project Structure

```
fractal-viewer/
├── python/              # Python version (rapid prototype)
│   ├── main.py          # App entry point, event loop
│   ├── fractal.py       # Escape-time with smooth coloring (numba JIT)
│   ├── viewport.py      # Complex plane math, zoom/pan
│   ├── renderer.py      # Pygame pixel buffer display
│   ├── palette.py       # Color gradient generation
│   ├── requirements.txt
│   └── run.sh
├── c/                   # C version (native performance)
│   ├── src/
│   │   ├── main.c       # SDL2 + OpenGL init, event loop
│   │   ├── fractal.c/h  # Escape-time, SIMD (AVX2) inner loop
│   │   ├── viewport.c/h # Viewport math (double precision)
│   │   ├── renderer.c/h # OpenGL texture rendering
│   │   ├── palette.c/h  # Color palette LUT
│   │   └── worker.c/h   # pthread thread pool
│   └── CMakeLists.txt
└── README.md
```

## Dependencies

### Python
- Python 3.8+
- pygame, numpy, numba

Install: `pip install -r python/requirements.txt`

### C
- SDL2 (development headers)
- OpenGL
- CMake 3.10+
- pthreads (included in glibc)

On Debian/Ubuntu:
```bash
sudo apt install cmake libsdl2-dev libgl-dev
```

## Running

### Python
```bash
cd python
python3 main.py
# or
./run.sh
```

### C
```bash
cd c
mkdir build && cd build
cmake ..
make -j$(nproc)
./fractal-viewer
```

## Controls

| Key | Action |
|-----|--------|
| Mouse wheel | Zoom in/out (centered on cursor) |
| Left drag | Pan |
| `M` | Switch to Mandelbrot set |
| `J` | Switch to Julia set |
| Mouse move (Julia) | Update Julia `c` parameter in real-time |
| `F` | Toggle fullscreen |
| `S` | Save screenshot (PPM format) |
| `Esc` | Quit |

## The Math

### Mandelbrot Set
The Mandelbrot set is the set of complex numbers `c` for which the function
`f_c(z) = z^2 + c` does not diverge when iterated from `z = 0`.

Each pixel maps to a point `c` in the complex plane. We iterate:
`z_{n+1} = z_n^2 + c`, starting from `z_0 = 0`.

If `|z|` exceeds 2, the point escapes and is colored by the iteration count.

### Julia Set
For a fixed `c`, the Julia set is the set of starting `z` values for which
`f_c(z)` does not diverge. Same iteration formula, but each pixel maps to the
starting `z` while `c` is a global parameter (controlled by mouse movement).

### Smooth Coloring
Instead of discrete bands, we compute a fractional iteration count:
```
smooth = n + 1 - log(log(|z_n|)) / log(2)
```
This maps to a continuous color gradient via sine-based palette.

## Performance

| Feature | Python | C |
|---------|--------|---|
| Rendering | numpy arrays → pygame Surface | CPU pixel buffer → OpenGL texture |
| Parallelism | numba JIT (auto-vectorization) | pthreads + manual AVX2 SIMD |
| Zoom precision | double | double (scalar), float (SIMD) |
| Render speed (800×600, 256 iter) | ~5-15 FPS (JIT warm) | ~60 FPS (threaded + SIMD) |
| Fullscreen | pygame toggle | SDL native toggle |
| Portability | Any OS with Python + pygame | Any OS with SDL2 + OpenGL |

The Python version prioritizes rapid prototyping and readability. The C version
achieves real-time 60 FPS navigation through multi-threading, SIMD vectorization,
and direct GPU texture upload.

## Screenshots

Screenshots are saved as PPM files (`fractal_YYYYMMDD_HHMMSS.ppm`) in the
working directory. Convert to PNG with:
```bash
convert fractal_*.ppm fractal.png  # requires ImageMagick
```
