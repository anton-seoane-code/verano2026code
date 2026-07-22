#ifndef VIEWPORT_H
#define VIEWPORT_H

typedef struct {
    int width, height;
    double cx, cy;
    double zoom;
} Viewport;

void viewport_init(Viewport *vp, int width, int height);
void viewport_screen_to_complex(Viewport *vp, int sx, int sy, double *px, double *py);
void viewport_zoom_at(Viewport *vp, int sx, int sy, double factor);
void viewport_pan(Viewport *vp, double dx, double dy);

#endif
