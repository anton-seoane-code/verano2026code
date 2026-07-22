#include "worker.h"
#include <stdlib.h>

typedef struct {
    ThreadPool *pool;
    int thread_id;
} ThreadArg;

static void* thread_worker(void *arg) {
    ThreadArg *targ = (ThreadArg*)arg;
    ThreadPool *pool = targ->pool;
    int thread_id = targ->thread_id;
    free(targ);

    while (1) {
        int idx = __sync_fetch_and_add(&pool->work_index, 1);
        if (idx >= pool->work_count) break;
        pool->work_func(pool->work_data, idx, thread_id);
    }

    pthread_barrier_wait(&pool->barrier);
    return NULL;
}

ThreadPool* thread_pool_create(int num_threads) {
    ThreadPool *pool = malloc(sizeof(ThreadPool));
    pool->num_threads = num_threads;
    pool->threads = malloc(num_threads * sizeof(pthread_t));
    pool->work_func = NULL;
    pool->work_data = NULL;
    pool->work_count = 0;
    pool->work_index = 0;
    pthread_mutex_init(&pool->mutex, NULL);
    pthread_barrier_init(&pool->barrier, NULL, num_threads + 1);
    return pool;
}

void thread_pool_dispatch(ThreadPool *pool,
                          void (*func)(void*, int, int),
                          void *data, int count) {
    pool->work_func = func;
    pool->work_data = data;
    pool->work_count = count;
    pool->work_index = 0;

    for (int i = 0; i < pool->num_threads; i++) {
        ThreadArg *arg = malloc(sizeof(ThreadArg));
        arg->pool = pool;
        arg->thread_id = i;
        pthread_create(&pool->threads[i], NULL, thread_worker, arg);
    }
}

void thread_pool_wait(ThreadPool *pool) {
    pthread_barrier_wait(&pool->barrier);
}

void thread_pool_destroy(ThreadPool *pool) {
    pthread_barrier_destroy(&pool->barrier);
    pthread_mutex_destroy(&pool->mutex);
    free(pool->threads);
    free(pool);
}
