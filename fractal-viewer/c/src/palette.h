#ifndef PALETTE_H
#define PALETTE_H

#include <stdint.h>

typedef struct {
    int size;
    uint8_t (*colors)[3];
} Palette;

Palette palette_create(int size);
void palette_destroy(Palette *p);

#endif
