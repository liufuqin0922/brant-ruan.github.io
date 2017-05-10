---
category: Sec
title: Linux Rootkit 实验 | 0002 Rootkit 基本功能实现
---

## Linux Rootkit 实验 | 0002 Rootkit 基本功能实现

### 实验说明

本次实验将初步实现 rootkit 的基本功能：

- 阻止其他内核模块加载
- 提供 root 后门
- 隐藏文件
- 隐藏进程
- 隐藏端口
- 隐藏内核模块

并对可行的改进方向进行展望。

本次实验基于 0001 实验中学习的挂钩技术。

### 实验环境

```
uname -a:
Linux kali 4.6.0-kali1-amd64 #1 SMP Debian 4.6.4-1kali1 (2016-07-21) x86_64 GNU/Linux

GCC version:6.1.1
```

上述环境搭建于虚拟机，另外在没有特殊说明的情况下，均以 root 权限执行。

**注：后面实验参考的是4.11的源码，可以[在线阅览](http://elixir.free-electrons.com/linux/latest/ident/sys_call_table)。**

### 实验过程

#### 控制内核模块加载

首先如果可以，把进来的漏洞堵上，防止其他人进入系统。接下来，就是阻止可能有威胁的内核代码执行（如 Anti-rootkit 之类），这个有些难，我们先做到控制内核模块的加载，之后才是提供其他功能。先保障生存再展开工作 :)

测试结果如下：

首先我们在正常情况下加载以及清除`lamb`模块：

![]({{ site.url }}/resources/pictures/linux-rkt-9.png)

接着我们加载`guard`模块，再测试`lamb`模块。可以看到，我们先加载`guard`模块，再加载`lamb`模块，它的入口和出口函数已经被`Fake`替换。我们卸载`lamb`和`guard`，再次加载`lamb`模块，发现加载和卸载又恢复正常。

![]({{ site.url }}/resources/pictures/linux-rkt-10.png)

#### 提供 root 后门

测试结果如下：

![]({{ site.url }}/resources/pictures/linux-rkt-8.png)

#### 隐藏文件

在我们的设定里，所有以`QTDS_`为前缀的文件都会被隐藏（QTDS = “齐天大圣”）。

测试结果如下：

首先，我们加载`fileHid`模块：

![]({{ site.url }}/resources/pictures/linux-rkt-11.png)

接着创建`hello`文件，可以看到，`hello`文件正常显示。我们把`hello`更名为`QTDS_hello`，这时再`ls`，发现文件消失，且`dmesg`中有我们设定的打印语句：

![]({{ site.url }}/resources/pictures/linux-rkt-12.png)

![]({{ site.url }}/resources/pictures/linux-rkt-13.png)

此时只是用户看不到文件而已，但如果知道文件名，还是可以对它操作：

![]({{ site.url }}/resources/pictures/linux-rkt-14.png)

这时如果卸载模块，则文件又会显现出来：

![]({{ site.url }}/resources/pictures/linux-rkt-15.png)

![]({{ site.url }}/resources/pictures/linux-rkt-16.png)

日志则会记录`iterate`的改变：

![]({{ site.url }}/resources/pictures/linux-rkt-17.png)

**将“提供 root 后门”环节和本环节的方法结合，就可以做出隐藏的 root 后门。**

#### 隐藏进程

测试结果如下：

图片中一个 shell 的`PID`是`3033`。在没有加载模块之前，`ps`可以看到该进程。在加载模块之后，`ps`中无该进程：

![]({{ site.url }}/resources/pictures/linux-rkt-18.png)

卸载模块后，进程重新在`ps`中出现：

![]({{ site.url }}/resources/pictures/linux-rkt-19.png)

#### 隐藏端口



#### 隐藏内核模块

个人以为隐藏内核模块应该是 rootkit 加载后要做的第二件事情。但是由于它的方法依赖于“隐藏文件”和“隐藏端口”的方法，所以放在这里实验。

#### 未来展望

### 实验问题

【问题一】

一开始写代码有问题，即使是错误的认证也能提权到 root。然后在`dmesg`中报错，并且`rmmod`出错。错误信息如下：

![]({{ site.url }}/resources/pictures/linux-rkt-7-err.png)

![]({{ site.url }}/resources/pictures/linux-rkt-7-err2.png)

和 novice 师傅的代码对比后，并控制变量进行部分改动又通过虚拟机不断恢复快照测试，终于确定问题出在我的`write_handler`上。终于发现问题，在最后部分：

师傅的代码：

![](./{{ site.url }}/resources/pictures/linux-rkt-7-err3.png)

我的代码：

![](./{{ site.url }}/resources/pictures/linux-rkt-7-err4.png)

粗心了。

【问题二】

隐藏进程的实验中，我们是把进程号写死在代码里，这样十分不方便。很明显，在实际渗透过程中，我们需要隐藏的进程的进程号只有在运行时才知道。一种可以借鉴的改进思路是：新设定一个信号，模块运行时，我们给哪个进程发该信号，那个进程就被隐藏起来。这是 [m0nad/Diamorphine](https://github.com/m0nad/Diamorphine) 这个 rootkit 的设计。未来我会写一篇文章专门分析这个 rootkit，它的其他思路也是很有意思的。

### 实验总结与思考

- 内核中的事情，真的是要细心。顺着 FreeBuf 的文章往下看时，`kbuff = kmalloc(count, GFP_KERNEL);`这个地方少分配了一个尾零。事实上应该是`kbuff = kmalloc(count + 1, GFP_KERNEL);`

- 突然想到，做 rootkit 应该从对抗者的角度考虑问题。假如我是用户，我会通过什么方式查看文件？会通过什么方式查看端口？会通过什么方式查看进程？会通过什么方式查看内核模块？进一步地，这些查看的方法是什么原理？用了什么系统调用，用了什么内核数据结构？进一步地，我们能`fake`这些原理中的哪些部分？对这部分下手，rootkit 就渐渐出来了

- 个人以为 rootkit 应该提供一个能够远程连接的 root shell（对于内网的机器，用 reverse shell 是不是更好），并具备痕迹清理、自我删除甚至更强的反取证功能（另外，是否需要隐藏当前登录用户？）

- 在隐藏端口实验，从内核源码中看到的`seq_file`让我学会了一种用 C 表达面向对象的编程技巧（这代码，太美了）

{% highlight c %}
struct seq_file {
	char *buf;
	size_t size;
	size_t from;
	size_t count;
	size_t pad_until;
	loff_t index;
	loff_t read_pos;
	u64 version;
	struct mutex lock;
	const struct seq_operations *op;
	int poll_event;
	const struct file *file;
	void *private;
};
struct seq_operations {
	void * (*start) (struct seq_file *m, loff_t *pos);
	void (*stop) (struct seq_file *m, void *v);
	void * (*next) (struct seq_file *m, void *v, loff_t *pos);
	int (*show) (struct seq_file *m, void *v);
};
{% endhighlight %}

- 通过这次实验，我发现自己的 C 语言还有许多要学习的地方

### 参考资料

- [Linux Rootkit系列三：实例详解 Rootkit 必备的基本功能](http://www.freebuf.com/articles/system/107829.html)
- [Github: research-rootkit](https://github.com/NoviceLive/research-rootkit)