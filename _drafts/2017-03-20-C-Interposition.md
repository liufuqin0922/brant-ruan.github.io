---
title: Interposition in C
category: CS
---

## Interposition in C

本文主要介绍`Linux`环境下 C 语言中的`Interposition`特性，中文叫做“打桩”。另外，`单元测试`中也有`打桩`这个词，英文是`Mock`，后面会用一个小节简介`Mock`。

### 概念

【参考资料】第一篇文章主要讲`Windows`下的`打桩`，但是已经很好的解释了`打桩`的概念。`interposition`是`hook`技术的一种，

### 实验

{% highlight c %}
/* _GNU_SOURCE is needed for RTLD_NEXT, GCC will not define it by default */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <stdint.h>
#include <inttypes.h>

static uint32_t malloc_count = 0;
static uint64_t total = 0;

void summary(){
    fprintf(stderr, "malloc called: %u times\n", malloc_count);
    fprintf(stderr, "total allocated memory: %" PRIu64 " bytes\n", total);
}

void *malloc(size_t size){
    static void* (*real_malloc)(size_t) = NULL;
//    void *ptr = 0;

    if(real_malloc == NULL){
        real_malloc = dlsym(RTLD_NEXT, "malloc");
        atexit(summary);
    }

    malloc_count++;
    total += size;

    return real_malloc(size);
}
{% endhighlight %}

**_GNU_SOURCE **

**RTLD_NEXT**

**PRIu64**

**LD_PRELOAD**

```
gcc -shared -ldl -fPIC malloc_counter.c -o /tmp/libmcnt.so
export LD_PRELOAD="/tmp/libstr.so"
```

### Mock in Unit Testing

### 参考资料

**用到的**

1. [多任务下的数据结构与算法：函数的HOOK](http://www.mscto.com/shujujiegou/25533203.html)
2. [C进阶指南（2）：数组和指针、打桩](http://blog.jobbole.com/73094/)
3. [Guide to Advanced Programming in C](http://pfacka.binaryparadise.com/articles/guide-to-advanced-programming-in-C.html)

**暂未用**

- [Linux Applications Debugging Techniques/The interposition library](https://en.wikibooks.org/wiki/Linux_Applications_Debugging_Techniques/The_interposition_library)
- [Let’s Hook a Library Function](http://opensourceforu.com/2011/08/lets-hook-a-library-function/)
- [24-linking-v2-6up](http://www-users.cselabs.umn.edu/classes/Spring-2015/csci2021/smcc-lectures/24-linking-v2-6up.pdf)
- [Tutorial: Function Interposition in Linux](http://jayconrod.com/posts/23/tutorial-function-interposition-in-linux)
- [数据结构与算法：多个函数的HOOK实现](http://www.mscto.com/shujujiegou/25533303.html)
- [What does “#define _GNU_SOURCE” imply?](http://stackoverflow.com/questions/5582211/what-does-define-gnu-source-imply)
- [Linux Hook 笔记](http://www.cnblogs.com/pannengzhi/p/5203467.html)
- [Linux System Calls Hooking Method Summary](http://www.cnblogs.com/LittleHann/p/3854977.html)
- [Linux Dynamic Shared Library && LD Linker](http://www.cnblogs.com/LittleHann/p/4244863.html)