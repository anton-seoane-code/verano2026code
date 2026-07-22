#include "viewport.h"

void viewport_init(Viewport *vp, int width, int height) {
    vp->width = width;
    vp->height = height;
    vp->cx = -0.5;
    vp->cy = 0.0;
    vp->zoom = 200.0;
}

void viewport_screen_to_complex(Viewport *vp, int sx, int sy, double *px, double *py) {
    *px = (sx - vp->width / 2.0) / vp->zoom + vp->cx;
    *py = (sy - vp->height / 2.0) / vp->zoom + vp->cy;
}

void viewport_zoom_at(Viewport *vp, int sx, int sy, double factor) {
    double px, py;
    viewport_screen_to_complex(vp, sx, sy, &px, &py);
    vp->zoom *= factor;
    vp->cx = px - (sx - vp->width / 2.0) / vp->zoom;
    vp->cy = py - (sy - vp->height / 2.0) / vp->zoom;
}

void viewport_pan(Viewport *vp, double dx, double dy) {
    vp->cx -= dx / vp->zoom;
    vp->cy -= dy / vp->zoom;
}
