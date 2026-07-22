#ifndef WORKER_H
#define WORKER_H

#include <pthread.h>

typedef struct {
    int num_threads;
    pthread_t *threads;
    void (*work_func)(void*, int, int);
    void *work_data;
    int work_count;
    volatile int work_index;
    pthread_mutex_t mutex;
    pthread_barrier_t barrier;
} ThreadPool;

ThreadPool* thread_pool_create(int num_threads);
void thread_pool_dispatch(ThreadPool *pool, void (*func)(void*, int, int), void *data, int count);
void thread_pool_wait(ThreadPool *pool);
void thread_pool_destroy(ThreadPool *pool);

#endif
