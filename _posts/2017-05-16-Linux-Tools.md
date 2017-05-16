---
title: Head First Linux Tools
category: Linux
---

## Head First Linux Tools

> 记录 Linux 工具的简单使用方法

### 0x00 chroot

##### 介绍

```
man chroot
```

##### 实验

以下实验以`root`权限在`/root`目录下进行。建立如下目录结构：

```
sandbox
|- hello.c
|- lib/
```

`hello.c`即最简单的打印`Hello, world`程序。

```
gcc -o hello hello.c
ldd hello
```

得到动态链接信息：

```
linux-gate.so.1 =>  (0xb7778000)
libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb75be000)
/lib/ld-linux.so.2 (0xb7779000)
```

为了保证`chroot`后程序能正确找到动态链接器和动态链接库：

```
cp /lib/i386-linux-gnu/libc.so.6 ./sandbox/lib
cp /lib/ld-linux.so.2 ./sandbox/lib
```

测试如下，因为原来的根目录下无`hello`程序，所以第一次运行失败：

![]({{ site.url }}/resources/pictures/linux-tools-0.PNG)

##### 原理

但就这个工具来讲，应该是使用了 API `chroot()`，可参考`man 2 chroot`。

我写了个简单的`mychroot`，同样有效：

{% highlight c %}
// mychroot.c
#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if(argc < 3){
        printf("%s NEWROOTPATH FILENAME\n", argv[0]);
        return 0;
    }
    if(chroot(argv[1])){
        perror("chroot");
        return -1;
    }
    execve(argv[2], &(argv[2]), NULL);

    return 0;
}
{% endhighlight %}

更深层次的原理：猜测是更改了进程图像的`task_struct->fs->root`。