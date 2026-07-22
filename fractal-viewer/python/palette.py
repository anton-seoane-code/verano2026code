import numpy as np

def make_palette(n=1024):
    palette = np.zeros((n, 3), dtype=np.uint8)
    for i in range(n):
        t = 2.0 * np.pi * i / n
        palette[i, 0] = int(128 + 127 * np.sin(t + 0.0))
        palette[i, 1] = int(128 + 127 * np.sin(t + 2.0))
        palette[i, 2] = int(128 + 127 * np.sin(t + 4.0))
    return palette
