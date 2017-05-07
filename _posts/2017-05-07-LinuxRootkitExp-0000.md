---
category: Sec
title: Linux Rootkit 实验 | 0000 LKM 的基础编写&隐藏
---

## Linux Rootkit 实验 | 0000 LKM 的基础编写&隐藏

### 实验说明

LKM 作为内核模块，动态加载，无需重新编译内核。

通过实验，学习 LKM 模块的编写和加载，以及如何初步隐藏模块。在本次实验中，隐藏意味着三个方面：

- 对 lsmod 隐藏
- 对 /proc/modules 隐藏
- 对 /sys/module 隐藏

### 实验环境

```
uname -a:
Linux kali 4.6.0-kali1-amd64 #1 SMP Debian 4.6.4-1kali1 (2016-07-21) x86_64 GNU/Linux

GCC version:6.1.1
```

上述环境搭建于虚拟机，另外在没有特殊说明的情况下，均以 root 权限执行。

### 实验过程

我们首先看一下一般的 LKM 编译加载的过程。

**LKM 测试代码**

{% highlight c %}
// lkm.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int lkm_init(void)
{
    printk("bt: module loaded\n");
    return 0;
}

static void lkm_exit(void)
{
    printk("bt: module removed\n");
}

module_init(lkm_init);
module_exit(lkm_exit);
{% endhighlight %}

**代码解释**

`lkm_init()`和`lkm_exit()`分别是内核模块的初始化函数和清除函数，角色类似于构造函数和析构函数，模块被加载时初始化函数被内核执行，模块被卸载时清除函数被执行。如果没有定义清除函数，则内核不允许卸载该模块。

内核中无法调用 C 库函数，所以不能用`printf`输出，要用内核导出的`printk`，它把内容记录到系统日志里。

`module_init`和`module_exit`是内核的两个宏，利用这两个宏来指定我们的初始化和清除函数。

**Makefile**

```
obj-m   := lkm.o
 
KDIR    := /lib/modules/$(shell uname -r)/build
PWD    := $(shell pwd)
 
default:
$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules
```

然后`make`就好。生成的`lkm.ko`文件就是模块文件。输入`insmod lkm.ko`加载模块。

接着通过`cat /var/log/messages`或`dmesg | tail -n 1`查看加载情况：

```
[ 2931.410443] bt: module loaded
```

对于这种正常模块来说，我们是可以查看到它的。输入`lsmod | grep lkm`：

```
lkm                    16384  0
```

而`lsmod`是通过`/proc/modules`获得信息的，我们也可以直接查看它。输入`cat /proc/modules | grep lkm`：

```
lkm 16384 0 - Live 0xffffffffc04a0000 (POE)
```

另外，还可以`ls /sys/module/`，我们会发现其下有一个`lkm/`目录，这也证明了我们的模块的存在。

好了，测试结束，卸载模块：`rmmod lkm.ko`。我们可以通过上面介绍的`dmesg`方式查看卸载的记录。

**隐藏模块**

下面我们开始隐藏实验。上面已经说过，`lsmod`是通过读取`/proc/modules`来发挥作用的，所以我们仅需要处理`/proc/modules`即可。另外，我们需要再处理掉`/sys/module/`。

### 实验问题

【问题一】

我们在本次实验中还是留下了痕迹，因为我们进行`insmod`和`rmmod`时会有输出，所以使用`dmesg`或者直接`cat /var/log/messages`还是可以看到。不过很简单，只需要取消输出即可，把`printk`去掉。

另外，执行命令的过程会被记录在`history`中，也许也应该清理一下？

【问题二】

测试模块的确看不到了，但也没办法通过命令行进行卸载。将来要找到卸载的方法，最好是易于控制的方法，或者能够自卸载（不知道可不可行）。进可攻，退可守，最好能够在需要撤离时不留痕迹地从目标机器上消失。

【问题三】

解释一下这个 Makefile 的内容？

【问题四】

`make`后生成的文件如下：

```
lkm.o
lkm.mod.c
lkm.mod.o
lkm.ko
modules.order
Module.symvers
```

`lkm.ko` 是我们需要的模块文件，那么其他的文件是干嘛的？

【问题五】

经过本次实验的操作，是否真的没有办法检测到这个模块了？

### 实验总结与思考

本次实验是跟着 FreeBuf 上 arciryas 师傅的文章一步步操作的。这也是我借鉴“实验”的方法（做实验+写实验报告书）来整理学习相关零碎知识点并形成知识体系的第一次尝试。关于 Windows 上的 Rootkit 有一本《Rootkit:系统灰色地带的潜伏者》，最近张瑜先生出了一本《Rootkit隐遁攻击技术及其防范》。而 Linux Rootkit 的资料就比较零散了，多见于博客、论文和杂志（如 Phrack）中。它们往往是不成体系的，不断总结积累非常重要。初步想法是收集网络上的资料进行实验，再根据这些资料进行递归学习（如通过写拓展延伸积累基础知识），接着慢慢从整体的视角来把自己的实验成果进行整合，以此形成自己的知识技术网络。

### 拓展延伸

关于 LKM 编写：

- 《linux设备驱动程序》（第三版）第二章“构造和运行模块”

关于 proc 和 sysfs 文件系统：

- 《深入Linux内核架构》第十章“无持久存储的文件系统”

### 参考资料

- [Linux Rootkit系列一：LKM的基础编写及隐藏](http://www.freebuf.com/articles/system/54263.html)