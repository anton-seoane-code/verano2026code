#include <SDL2/SDL.h>
#include <SDL2/SDL_opengl.h>
#include "viewport.h"
#include "palette.h"
#include "fractal.h"
#include "renderer.h"
#include "worker.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define WIDTH 800
#define HEIGHT 600
#define MAX_ITER 256

typedef struct {
    SDL_Window *window;
    SDL_GLContext gl_ctx;
    Renderer renderer;
    Viewport viewport;
    Palette palette;
    FractalRenderData fractal_rd;
    ThreadPool *pool;
    uint8_t *pixels;
    int w, h;
    int fullscreen;
    int julia_mode;
    double julia_cx, julia_cy;
    int dragging;
    int last_mx, last_my;
    int needs_render;
    int running;
} App;

static int app_resize(App *app, int w, int h) {
    double old_cx = app->viewport.cx;
    double old_cy = app->viewport.cy;
    double old_zoom = app->viewport.zoom;

    free(app->pixels);
    app->pixels = malloc((size_t)w * h * 3);
    if (!app->pixels) return 0;

    renderer_destroy(&app->renderer);
    if (!renderer_init(&app->renderer, w, h)) return 0;

    viewport_init(&app->viewport, w, h);
    app->viewport.cx = old_cx;
    app->viewport.cy = old_cy;
    app->viewport.zoom = old_zoom;

    app->w = w;
    app->h = h;
    app->fractal_rd.pixels = app->pixels;
    app->fractal_rd.width = w;
    app->fractal_rd.height = h;
    app->fractal_rd.viewport = &app->viewport;
    return 1;
}

static void app_init(App *app) {
    SDL_Init(SDL_INIT_VIDEO);

    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,
                        SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);

    app->window = SDL_CreateWindow("Fractal Viewer",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        WIDTH, HEIGHT,
        SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE);
    app->gl_ctx = SDL_GL_CreateContext(app->window);
    SDL_GL_SetSwapInterval(1);

    app->w = WIDTH;
    app->h = HEIGHT;
    app->pixels = NULL;
    app->fullscreen = 0;
    app->julia_mode = 0;
    app->julia_cx = -0.7;
    app->julia_cy = 0.27015;
    app->dragging = 0;
    app->needs_render = 1;
    app->running = 1;

    int num_threads = SDL_GetCPUCount();
    if (num_threads < 1) num_threads = 1;
    app->pool = thread_pool_create(num_threads);

    viewport_init(&app->viewport, WIDTH, HEIGHT);
    app->palette = palette_create(1024);

    app->fractal_rd.pixels = NULL;
    app->fractal_rd.viewport = &app->viewport;
    app->fractal_rd.max_iter = MAX_ITER;
    app->fractal_rd.palette = &app->palette;
    app->fractal_rd.julia_mode = 0;
    app->fractal_rd.julia_cx = 0.0;
    app->fractal_rd.julia_cy = 0.0;
    app->fractal_rd.pool = app->pool;

    app_resize(app, WIDTH, HEIGHT);
}

static void app_render(App *app) {
    fractal_render(&app->fractal_rd);
    renderer_render(&app->renderer, app->pixels);
    SDL_GL_SwapWindow(app->window);
}

static void app_toggle_fullscreen(App *app) {
    app->fullscreen = !app->fullscreen;
    if (app->fullscreen) {
        SDL_SetWindowFullscreen(app->window, SDL_WINDOW_FULLSCREEN_DESKTOP);
    } else {
        SDL_SetWindowFullscreen(app->window, 0);
        SDL_SetWindowSize(app->window, WIDTH, HEIGHT);
    }

    int w, h;
    SDL_GetWindowSize(app->window, &w, &h);
    app_resize(app, w, h);
    app->needs_render = 1;
}

static void app_save_screenshot(App *app) {
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    char name[64];
    strftime(name, sizeof(name), "fractal_%Y%m%d_%H%M%S.ppm", tm);
    renderer_save_ppm(&app->renderer, app->pixels, name);
}

static void app_set_julia(App *app, int mx, int my) {
    double px, py;
    viewport_screen_to_complex(&app->viewport, mx, my, &px, &py);
    app->julia_cx = px;
    app->julia_cy = py;
    app->fractal_rd.julia_cx = px;
    app->fractal_rd.julia_cy = py;
}

static void app_handle_event(App *app, SDL_Event *ev) {
    switch (ev->type) {
    case SDL_QUIT:
        app->running = 0;
        break;
    case SDL_KEYDOWN:
        switch (ev->key.keysym.sym) {
        case SDLK_m:
            app->julia_mode = 0;
            app->fractal_rd.julia_mode = 0;
            app->needs_render = 1;
            break;
        case SDLK_j:
            app->julia_mode = 1;
            app->fractal_rd.julia_mode = 1;
            app->julia_cx = -0.7;
            app->julia_cy = 0.27015;
            app->fractal_rd.julia_cx = app->julia_cx;
            app->fractal_rd.julia_cy = app->julia_cy;
            app->needs_render = 1;
            break;
        case SDLK_f:
            app_toggle_fullscreen(app);
            break;
        case SDLK_s:
            app_save_screenshot(app);
            break;
        case SDLK_ESCAPE:
            app->running = 0;
            break;
        default:
            break;
        }
        break;
    case SDL_MOUSEBUTTONDOWN:
        if (ev->button.button == SDL_BUTTON_LEFT) {
            app->dragging = 1;
            app->last_mx = ev->button.x;
            app->last_my = ev->button.y;
        }
        break;
    case SDL_MOUSEBUTTONUP:
        if (ev->button.button == SDL_BUTTON_LEFT) {
            app->dragging = 0;
            app->needs_render = 1;
        }
        break;
    case SDL_MOUSEMOTION:
        if (app->dragging) {
            int dx = ev->motion.x - app->last_mx;
            int dy = ev->motion.y - app->last_my;
            viewport_pan(&app->viewport, -dx, -dy);
            app->last_mx = ev->motion.x;
            app->last_my = ev->motion.y;
            fractal_render(&app->fractal_rd);
            renderer_render(&app->renderer, app->pixels);
            SDL_GL_SwapWindow(app->window);
        }
        if (app->julia_mode) {
            app_set_julia(app, ev->motion.x, ev->motion.y);
            app->needs_render = 1;
        }
        break;
    case SDL_MOUSEWHEEL: {
        int mx, my;
        SDL_GetMouseState(&mx, &my);
        double factor = (ev->wheel.y > 0) ? 1.1 : 1.0 / 1.1;
        viewport_zoom_at(&app->viewport, mx, my, factor);
        app->needs_render = 1;
        break;
    }
    case SDL_WINDOWEVENT:
        if (ev->window.event == SDL_WINDOWEVENT_RESIZED) {
            app_resize(app, ev->window.data1, ev->window.data2);
            app->needs_render = 1;
        }
        break;
    default:
        break;
    }
}

static void app_run(App *app) {
    while (app->running) {
        SDL_Event ev;
        while (SDL_PollEvent(&ev)) {
            app_handle_event(app, &ev);
        }

        if (app->needs_render) {
            app_render(app);
            app->needs_render = 0;
        }

        SDL_Delay(16);
    }
}

static void app_destroy(App *app) {
    free(app->pixels);
    palette_destroy(&app->palette);
    renderer_destroy(&app->renderer);
    thread_pool_destroy(app->pool);
    SDL_GL_DeleteContext(app->gl_ctx);
    SDL_DestroyWindow(app->window);
    SDL_Quit();
}

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    App app = {0};
    app_init(&app);
    app_run(&app);
    app_destroy(&app);
    return 0;
}
