#include "pool.h"

#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>

#include "debug.h"
#include "overflow.h"

#define MAX(x, y) ((x) > (y)? (x): (y))

/*******************************/
/* Unexported Helper Functions */
/*******************************/

void set_next(struct pool_t *pool, int32_t idx, int32_t val)
{
    uint8_t *ptr = ((uint8_t*) pool->blocks) + idx * pool->block_size;
    *((int32_t*)ptr) = val;
}

int32_t get_next(struct pool_t *pool, int32_t idx)
{
    uint8_t *ptr = ((uint8_t*) pool->blocks) + idx * pool->block_size;
    return *((int32_t*)ptr);
}

int32_t idx_from_ptr(struct pool_t *pool, void *ptr, bool *clean_conversion)
{
    ptrdiff_t diff = ptr - pool->blocks;
    int32_t idx = (diff / pool->block_size);
    *clean_conversion = idx * pool->block_size == diff;
    return idx;
}

/**********************/
/* Exported Functions */
/**********************/

/* TODO: add malloc success checks.
 * TODO: add overflow check for block_count and block_size. */
struct pool_t *pool_new(int32_t block_count, int32_t block_size)
{
    check(!mult_overflow_int32(block_count, block_size), "Overflow!")

    struct pool_t *pool = malloc(sizeof(*pool));
    check_mem(pool);

    pool->block_count = block_count;
    pool->block_size = MAX((size_t)block_size, sizeof(pool->free_head));

    pool->valid = calloc(sizeof(*pool->valid), pool->block_count);
    pool->blocks = calloc(pool->block_size, pool->block_count);

    pool->free_head = 0;
    pool->valid_count = 0;

    for (int i = 0; i < pool->block_count; i++) {
        set_next(pool, i, i + 1);
    }
    set_next(pool, pool->block_count - 1, -1);

    return pool;
}

/* TODO: add NULL check. */
void pool_free(struct pool_t *pool)
{
    free(pool->valid);
    free(pool->blocks);
}

/* TODO: better error handling on size error. */
/* TODO: zero return data field? */
/* TODO: do we actually care about checking the size? Maybe add a separate
 * check function.*/
void *pool_acquire_sized(struct pool_t *pool, size_t size)
{
    if (size > (size_t) pool->block_size) {
        fprintf(stderr, "Invalid size for pool operation.");
        exit(1);
    } else if (pool_is_full(pool)) {
        return NULL;
    }

    int idx = pool->free_head;
    pool->free_head = get_next(pool, pool->free_head);
    pool->valid[idx] = true;

    return ((uint8_t*)pool->blocks) + pool->block_size * idx;
}

/* TODO: Add debug condition which calls pool_is_valid(). */
void pool_return(struct pool_t *pool, void *ptr)
{
    bool clean_conversion;
    int idx = idx_from_ptr(pool, ptr, &clean_conversion);
    set_next(pool, idx, pool->free_head);
    pool->valid[idx] = false;
    pool->free_head = idx;
}

bool pool_is_full(struct pool_t *pool)
{
    return pool->free_head == -1;
}

bool pool_is_valid(struct pool_t *pool, void *ptr)
{
    bool clean_conversion;
    int idx = idx_from_ptr(pool, ptr, &clean_conversion);
    return (clean_conversion && pool->valid[idx] &&
            (idx >= 0 && idx < pool->block_count));
}
