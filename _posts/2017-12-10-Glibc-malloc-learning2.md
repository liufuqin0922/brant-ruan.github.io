---
title: Glibc堆管理学习笔记（二）
category: Linux
---

## Glibc堆管理学习笔记（二）

本部分完成对`_int_malloc`函数的分析。

该函数接受的参数为分配区指针`av`和所需空间大小`bytes`。

首先是一些变量的定义：

```c
static void *
_int_malloc (mstate av, size_t bytes)
{
  INTERNAL_SIZE_T nb;               /* normalized request size */
  unsigned int idx;                 /* associated bin index */
  mbinptr bin;                      /* associated bin */

  mchunkptr victim;                 /* inspected/selected chunk */
  INTERNAL_SIZE_T size;             /* its size */
  int victim_index;                 /* its bin index */

  mchunkptr remainder;              /* remainder from a split */
  unsigned long remainder_size;     /* its size */

  unsigned int block;               /* bit map traverser */
  unsigned int bit;                 /* bit map traverser */
  unsigned int map;                 /* current word of binmap */

  mchunkptr fwd;                    /* misc temp for linking */
  mchunkptr bck;                    /* misc temp for linking */

#if USE_TCACHE
  size_t tcache_unsorted_count;     /* count of unsorted chunks processed */
#endif

  const char *errstr = NULL;
```

紧接着先把需要分配的内存大小转换为`chunk`的大小：

```c
  checked_request2size (bytes, nb);
```

如果没有可用的分配区，就陷入到`sysmalloc`，通过`mmap`中获得一块`chunk`：

```c
  if (__glibc_unlikely (av == NULL))
    {
      void *p = sysmalloc (nb, av);
      if (p != NULL)
    alloc_perturb (p, bytes);
      return p;
    }
```

如果所需`chunk`大小小于等于`fastbin`中`最大chunk`的大小，就尝试从`fastbin`中分配。我们可以先想象一下分配流程：

- 根据chunk大小定位到fastbin的index
- 从上面定位到的fastbin头指针下取走一个chunk，并让头指针指向下一个chunk
- 将获得的chunk使用`chunk2mem`转换成用户需要的内存块并返回（注意，fastbin内的chunk的状态本身就是inuse，所以不用重新设置状态）

事实上，源代码中使用了`lock-free`技术来实现单向链表删除第一个结点。它既避免了多线程之间的影响，又没有使用效率低下的锁。

我们来具体看一下代码：

```c
#define REMOVE_FB(fb, victim, pp)           \
  do                            \
    {                           \
      victim = pp;                  \
      if (victim == NULL)               \
    break;                      \
    }                           \
  while ((pp = catomic_compare_and_exchange_val_acq (fb, victim->fd, victim)) \
     != victim);                    \

  if ((unsigned long) (nb) <= (unsigned long) (get_max_fast ()))
    {
      idx = fastbin_index (nb); // 定位下标
      mfastbinptr *fb = &fastbin (av, idx);
      mchunkptr pp = *fb;
      REMOVE_FB (fb, victim, pp); // 从该表头处取走第一个结点
      if (victim != 0)
        {
          if (__builtin_expect (fastbin_index (chunksize (victim)) != idx, 0))
            {
              errstr = "malloc(): memory corruption (fast)";
            errout:
              malloc_printerr (check_action, errstr, chunk2mem (victim), av);
              return NULL;
            }
          check_remalloced_chunk (av, victim, nb);
#if USE_TCACHE
      /* While we're here, if we see other chunks of the same size,
         stash them in the tcache.  */
      size_t tc_idx = csize2tidx (nb);
      if (tcache && tc_idx < mp_.tcache_bins)
        {
          mchunkptr tc_victim;

          /* While bin not empty and tcache not full, copy chunks over.  */
          while (tcache->counts[tc_idx] < mp_.tcache_count
             && (pp = *fb) != NULL)
        {
          REMOVE_FB (fb, tc_victim, pp);
          if (tc_victim != 0)
            {
              tcache_put (tc_victim, tc_idx);
                }
        }
        }
#endif
          void *p = chunk2mem (victim);
          alloc_perturb (p, bytes);
          return p;
        }
    }
```