---
title: Linux Kernel Notes
category: Linux
---

## Linux Kernel Notes

### 2017-06-14 Unix操作系统分析课程笔记

这是倒数第二节Unix操作系统分析课程，但是这学期的内容在这堂课上结束了。

Slab染色 -- 提高 CPU cache 命中率。

可执行文件的`radix树`的叶子结点全是干净的（不会被写）。

`LRU链表`把所有装文件的主存页框串起来。另外，`LRU链表`又分解成`active链表`和`inactive`链表，内存不足需要释放时，一定是`inactive链表`上的页框被释放出来。

`/dev/sda`这个特殊文件的`radix`树叶子结点存放的是`metadata`，即`inode`之类。

`page`可以对应一个`buffer`链表。

所有空闲内存由`Buddy System`管理。

由`page[f]`中的成员`mapping`和`index`可以找到引用其的进程（它们的`vm_area_struct`串在`vma_head`链表上）。在内存不足需要把一些页框中的内容`swap out`出去时需要做这种反向映射的操作。

### container_of

看 Linux 内核数据结构`list`的实现时一直有个问题：`list_head`是直接嵌入在实际结构体中的，那么怎么根据`list_head`找到包裹它的结构体实例的首地址呢？

PLKA 上是这么写的：

{% highlight c %}
#define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)
#define container_of(ptr, type, member) ({	\
		const typeof( ((type *)0)->member ) *__mptr = (ptr);	\
        (type *)( (char *)__mptr -offsetof(type, member) );})
{% endhighlight %}

`typeof`是 C 的一个扩展，用于返回变量的类型。

`offsetof`这个宏可以返回结构体成员相对于结构体的偏移量。这个宏非常巧妙！它假设`0地址`处有一个结构体，但是并不对指针进行解引用，所以没问题。对`0地址`处的`MEMBER`进行取地址，取出的当然就是成员的偏移量了，因为结构体的首地址刚好是 0！

有了`offsetof`，`container_of`就很好理解了。思路是找到结构体成员的地址，然后利用`offsetof`找到结构体成员的偏移地址。两者相减，即获得结构体的首地址。`__mptr`保存的是传入的结构体成员的地址。

最后，用`list_entry`宏把上面的封装起来：

```
#define list_entry(ptr, type, member)	\
	container_of(ptr, type, member)
```

通过`list_entry`就可以获得链表上的结构体实例了！

### do{...}while(0)

在看 Linux 内核源码时总会在宏定义中遇到`do{...}while(0)`。以前一直不怎么用`do while`这种方式写循环，感觉一不留神会出错，更别提写这种只会执行一次的`do while`了。但 Linux 内核中大量地运用了这种技巧，如下面的`kunmap_atomic`：

{% highlight c %}
#define kunmap_atomic(addr, idx)	do { pagefault_enable(); } while (0)
{% endhighlight %}

原来它有很多好处：

- 帮助定义复杂的宏以避免错误（主要用途）
- 避免使用`goto`控制程序流
- 定义单一的函数块来完成复杂的操作

参考了[这篇文章](http://www.cnblogs.com/lizhenghn/p/3674430.html)和[这篇文章](http://blog.csdn.net/chenhu_doc/article/details/856468)。

### 2017-06-07 Unix操作系统分析课程笔记

今日 Unix 系统分析课程就要结束了。老师说只有我们几个人选了课还坚持下来了，完成的还不错，大家全都给优。我心里是有些惭愧的。由于各种原因，自己并没有竭尽全力，而我确实很喜欢研究 Linux 内核。老师还给优，问心有愧。且以自鞭自勉，孜孜以学。

做一下今天的笔记：

**在 exec 后，进程的全 0 页（bss/heap/stack）是怎么来的？**

在内存中有一个`Zero page`，假设其页框号是`M0`，则进程的全 0 页的`PTE`初值为`M0`加`RO`属性。当进程要写入页面的时候，为其分配`N0`页框，将上述的`PTE`项替换为`N0`加`RW`属性，然后做一个`for循环`把内容置零。

**请求代码段的过程？**

具体的汇编指令时`call 0x08048000`，这时会去查`PTE`，由于是第一次请求，则`PTE`项为空，引发缺页异常，把地址放入`cr2`寄存器，之后由`cr2 - x + offset`计算出虚拟地址，代入`VMA`查找得到在文件的`offset`，用这个`offset`到`file`结构中的`address_space`基数树中查看是否已经存在相应主存页框，如果有，则直接把它填入`PTE`即可，如果没有，则分配主存页框`M1`，在对应`PTE`填入`M1`加`RW`属性。再查`i_blocks`数组找到扇区号，用`bio`进行 I/O 请求。多个连续的`bio`块可能打包成一个`request`，提交给`DMA`进行数据传输。

**问题：父子进程如何传递数据页面？**