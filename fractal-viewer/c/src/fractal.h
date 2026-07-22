#ifndef FRACTAL_H
#define FRACTAL_H

#include <stdint.h>
#include "viewport.h"
#include "palette.h"
#include "worker.h"

typedef struct {
    uint8_t *pixels;
    int width, height;
    Viewport *viewport;
    int max_iter;
    Palette *palette;
    int julia_mode;
    double julia_cx, julia_cy;
    ThreadPool *pool;
    int use_low_res;
} FractalRenderData;

void fractal_render(FractalRenderData *rd);

#endif
