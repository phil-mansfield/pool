#ifndef POOL_POOL_H_
#define POOL_POOL_H_

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

struct pool_t {
    void *blocks;
    bool *valid;
    int32_t block_count, block_size, valid_count;
    int32_t free_head;
};

#define pool_acquire(pool, type) (pool_acquire_sized((pool), sizeof((type))))

struct pool_t *pool_new(int32_t block_count, int32_t block_size);
void pool_free(struct pool_t *pool);
/* Not meant to be called externally. Use the macro pool_borrow() instead. */
void *pool_acquire_sized(struct pool_t *pool, size_t size);
void pool_return(struct pool_t *pool, void *ptr);
bool pool_is_full(struct pool_t *pool);
bool pool_is_valid(struct pool_t *pool, void *ptr);

#endif /* POOL_POOL_H_ */
