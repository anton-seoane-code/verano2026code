import numpy as np
import math
from numba import jit

@jit(nopython=True)
def render_fractal(pixels, width, height, cx, cy, zoom,
                   max_iter, palette, julia_mode, julia_cx, julia_cy):
    pal_len = palette.shape[0]
    log2 = math.log(2.0)

    for y in range(height):
        for x in range(width):
            px = (x - width / 2) / zoom + cx
            py = (y - height / 2) / zoom + cy

            if julia_mode:
                zx, zy = px, py
                cx_val, cy_val = julia_cx, julia_cy
            else:
                zx, zy = 0.0, 0.0
                cx_val, cy_val = px, py

            iteration = 0
            while zx * zx + zy * zy < 4.0 and iteration < max_iter:
                zx, zy = zx * zx - zy * zy + cx_val, 2.0 * zx * zy + cy_val
                iteration += 1

            if iteration == max_iter:
                pixels[y, x, 0] = 0
                pixels[y, x, 1] = 0
                pixels[y, x, 2] = 0
            else:
                smooth = iteration + 1 - math.log(math.log(
                    math.sqrt(zx * zx + zy * zy))) / log2
                idx = int(smooth) % pal_len
                pixels[y, x, 0] = palette[idx, 0]
                pixels[y, x, 1] = palette[idx, 1]
                pixels[y, x, 2] = palette[idx, 2]
