#ifndef RENDERER_H
#define RENDERER_H

#include <stdint.h>

typedef struct {
    unsigned int tex_id;
    unsigned int vao, vbo;
    unsigned int shader;
    int width, height;
} Renderer;

int renderer_init(Renderer *ren, int width, int height);
void renderer_destroy(Renderer *ren);
void renderer_render(Renderer *ren, uint8_t *pixels);
void renderer_save_ppm(Renderer *ren, uint8_t *pixels, const char *filename);

#endif
