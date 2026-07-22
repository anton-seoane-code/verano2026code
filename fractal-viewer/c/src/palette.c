#include "palette.h"
#include <stdlib.h>
#include <math.h>

Palette palette_create(int size) {
    Palette p;
    p.size = size;
    p.colors = malloc(size * 3);
    for (int i = 0; i < size; i++) {
        double t = 2.0 * M_PI * i / size;
        p.colors[i][0] = (uint8_t)(128 + 127 * sin(t + 0.0));
        p.colors[i][1] = (uint8_t)(128 + 127 * sin(t + 2.0));
        p.colors[i][2] = (uint8_t)(128 + 127 * sin(t + 4.0));
    }
    return p;
}

void palette_destroy(Palette *p) {
    free(p->colors);
    p->colors = NULL;
    p->size = 0;
}
