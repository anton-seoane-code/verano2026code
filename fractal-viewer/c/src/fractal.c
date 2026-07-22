#include "fractal.h"
#include <math.h>
#include <stdlib.h>
#include <pthread.h>
#include <immintrin.h>

#define MAX_ITER_DEFAULT 256

static inline double my_log2(double x) {
    return log(x) / log(2.0);
}

static void render_pixel(uint8_t *pixels, int x, int y, int w, int h,
                          Viewport *vp, int max_iter, Palette *pal,
                          int julia, double jcx, double jcy) {
    double px = (x - w / 2.0) / vp->zoom + vp->cx;
    double py = (y - h / 2.0) / vp->zoom + vp->cy;

    double zx, zy, cx, cy;
    if (julia) {
        zx = px; zy = py;
        cx = jcx; cy = jcy;
    } else {
        zx = 0.0; zy = 0.0;
        cx = px; cy = py;
    }

    int iter = 0;
    while (zx * zx + zy * zy < 4.0 && iter < max_iter) {
        double tmp = zx * zx - zy * zy + cx;
        zy = 2.0 * zx * zy + cy;
        zx = tmp;
        iter++;
    }

    int idx = (y * w + x) * 3;
    if (iter == max_iter) {
        pixels[idx] = pixels[idx + 1] = pixels[idx + 2] = 0;
    } else {
        double mag = sqrt(zx * zx + zy * zy);
        double smooth = iter + 1.0 - my_log2(log(mag));
        int ci = ((int)smooth) % pal->size;
        if (ci < 0) ci += pal->size;
        pixels[idx]     = pal->colors[ci][0];
        pixels[idx + 1] = pal->colors[ci][1];
        pixels[idx + 2] = pal->colors[ci][2];
    }
}

#ifdef __AVX2__
static void render_pixels_simd(uint8_t *pixels, int x0, int y, int count,
                                int w, int h, Viewport *vp, int max_iter,
                                Palette *pal, int julia, double jcx, double jcy) {
    for (int xi = 0; xi < count; xi += 8) {
        int n = (count - xi < 8) ? count - xi : 8;
        float cxs[8], cys[8], zxs[8], zys[8];
        int iters[8] = {0};
        int active[8] = {1, 1, 1, 1, 1, 1, 1, 1};

        for (int i = 0; i < n; i++) {
            double px = (x0 + xi + i - w / 2.0) / vp->zoom + vp->cx;
            double py = (y - h / 2.0) / vp->zoom + vp->cy;
            if (julia) {
                zxs[i] = (float)px; zys[i] = (float)py;
                cxs[i] = (float)jcx; cys[i] = (float)jcy;
            } else {
                zxs[i] = 0.0f; zys[i] = 0.0f;
                cxs[i] = (float)px; cys[i] = (float)py;
            }
        }

        __m256 cx_v = _mm256_loadu_ps(cxs);
        __m256 cy_v = _mm256_loadu_ps(cys);

        __m256i active_v = _mm256_set_epi32(1, 1, 1, 1, 1, 1, 1, 1);
        __m256i iter_v = _mm256_setzero_si256();

        for (int iter = 0; iter < max_iter; iter++) {
            int mask = _mm256_movemask_epi8((__m256i)
                _mm256_cmp_ps(_mm256_setzero_ps(),
                    _mm256_castsi256_ps(active_v), _CMP_EQ_OQ));
            if (mask == 0) break;

            __m256 zx_v = _mm256_loadu_ps(zxs);
            __m256 zy_v = _mm256_loadu_ps(zys);

            __m256 zx2 = _mm256_mul_ps(zx_v, zx_v);
            __m256 zy2 = _mm256_mul_ps(zy_v, zy_v);
            __m256 zxzy = _mm256_mul_ps(zx_v, zy_v);

            __m256 escaped = _mm256_cmp_ps(
                _mm256_add_ps(zx2, zy2), _mm256_set1_ps(4.0f), _CMP_GE_OQ);

            __m256i escaped_i = _mm256_castps_si256(escaped);
            __m256i one = _mm256_set1_epi32(1);
            iter_v = _mm256_add_epi32(iter_v,
                _mm256_and_si256(active_v, one));

            __m256 zx_new = _mm256_add_ps(_mm256_sub_ps(zx2, zy2), cx_v);
            __m256 zy_new = _mm256_add_ps(
                _mm256_mul_ps(_mm256_set1_ps(2.0f), zxzy), cy_v);

            _mm256_storeu_ps(zxs, _mm256_blendv_ps(zx_v, zx_new, escaped));
            _mm256_storeu_ps(zys, _mm256_blendv_ps(zy_v, zy_new, escaped));

            active_v = _mm256_andnot_si256(escaped_i, active_v);
        }

        _mm256_storeu_si256((__m256i*)iters, iter_v);
        for (int i = 0; i < n; i++) {
            int idx = (y * w + x0 + xi + i) * 3;
            if (iters[i] >= max_iter) {
                pixels[idx] = pixels[idx + 1] = pixels[idx + 2] = 0;
            } else {
                double mag = sqrt(zxs[i] * zxs[i] + zys[i] * zys[i]);
                double smooth = iters[i] + 1.0 - my_log2(log(mag));
                int ci = ((int)smooth) % pal->size;
                if (ci < 0) ci += pal->size;
                pixels[idx]     = pal->colors[ci][0];
                pixels[idx + 1] = pal->colors[ci][1];
                pixels[idx + 2] = pal->colors[ci][2];
            }
        }
    }
}
#endif

typedef struct {
    uint8_t *pixels;
    int width, height;
    Viewport *vp;
    int max_iter;
    Palette *pal;
    int julia;
    double jcx, jcy;
    int y_start, y_end;
    volatile int next_y;
    pthread_mutex_t *mutex;
} RenderChunk;

static void* render_worker(void *arg) {
    RenderChunk *rc = (RenderChunk*)arg;

    while (1) {
        pthread_mutex_lock(rc->mutex);
        int y = rc->next_y;
        if (y >= rc->y_end) {
            pthread_mutex_unlock(rc->mutex);
            break;
        }
        rc->next_y = y + 1;
        pthread_mutex_unlock(rc->mutex);

#ifdef __AVX2__
        render_pixels_simd(rc->pixels, 0, y, rc->width,
                           rc->width, rc->height, rc->vp,
                           rc->max_iter, rc->pal,
                           rc->julia, rc->jcx, rc->jcy);
#else
        for (int x = 0; x < rc->width; x++) {
            render_pixel(rc->pixels, x, y, rc->width, rc->height,
                        rc->vp, rc->max_iter, rc->pal,
                        rc->julia, rc->jcx, rc->jcy);
        }
#endif
    }
    return NULL;
}

void fractal_render(FractalRenderData *rd) {
    int w = rd->width;
    int h = rd->height;

    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    RenderChunk rc = {
        .pixels = rd->pixels,
        .width = w,
        .height = h,
        .vp = rd->viewport,
        .max_iter = rd->max_iter,
        .pal = rd->palette,
        .julia = rd->julia_mode,
        .jcx = rd->julia_cx,
        .jcy = rd->julia_cy,
        .y_start = 0,
        .y_end = h,
        .next_y = 0,
        .mutex = &mutex,
    };

    int num_threads = rd->pool ? rd->pool->num_threads : 1;
    pthread_t threads[num_threads];

    for (int i = 0; i < num_threads; i++) {
        pthread_create(&threads[i], NULL, render_worker, &rc);
    }
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
}
