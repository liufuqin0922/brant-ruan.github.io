---
title: Anti-Debug
category: Sec
---

## Anti-Debug

参考文章[ELF反调试初探](http://www.freebuf.com/sectool/83509.html)。

这篇文章让我想起了入门者应该知道的整体架构：逆向总的来说分为静态代码分析和动态调试（还有patch）。为了对抗逆向，就有了代码混淆技术和反调试技术，比如加壳和检测某些标志位，另外还有校赛CTF中接触到的[movfuscator](https://recon.cx/2015/slides/recon2015-14-christopher-domas-The-movfuscator.pdf)，更多混淆技术介绍可以参考[
漫谈混淆技术：从Citadel混淆壳说起](http://www.freebuf.com/articles/web/103188.html)。另外，比较有趣的还有虚拟机检测技术（沙盒检测技术）。

反调试：

- ptrace自身进程

```
#include <stdio.h>
#include <sys/ptrace.h>
int main(int argc, char **argv)
{
    if(ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
       printf("Debugger detected\n");
       return 1;
   }  
   printf("All good\n");
   return 0;
}
```

原理：同一时间，一个进程只能被一个调试器调试，所以它调试自身，如果已经被GDB加载，则会调试失败返回。反过来，如果它先运行，GDB后来企图attach上去，由于它已经调试自身，所以GDB会ptrace失败，报错如下：

```
Attaching to process 10329
Could not attach to process.  If your uid matches the uid of the target
process, check the setting of /proc/sys/kernel/yama/ptrace_scope, or try
again as the root user.  For more details, see /etc/sysctl.d/10-ptrace.conf
warning: process 10329 is already traced by process 9359
ptrace: Operation not permitted.
```

**P.S. 研究一下ptrace**

- 检查父进程名称

```
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
   char buf0[32], buf1[128];
   FILE *fin;

   snprintf(buf0, 24, "/proc/%d/cmdline", getppid());
   fin = fopen(buf0, "r");
   fgets(buf1, 128, fin);
   fclose(fin);

   if(!strncmp(buf1, "gdb", strlen("gdb"))) {
       printf("Debugger detected");
       return 1;
   }
   printf("All good");
   return 0;
}
```

**P.S. 这种方法对attach无效**

- 检查进程运行状态

原理：正常状态下，/proc/12246/status为：

```
Name:	print
State:	S (sleeping)
Tgid:	12246
Ngid:	0
Pid:	12246
PPid:	11140
TracerPid:	0
```

attach后，是下面这样：

```
Name:	print
State:	t (tracing stop)
Tgid:	12246
Ngid:	0
Pid:	12246
PPid:	11140
TracerPid:	12266
```

所以可以通过检测进程的TracerPid来判断是不是被调试：

```
#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[]) {
   int i;
   scanf("%d", &i);
   char buf1[512];
   FILE* fin;
   fin = fopen("/proc/self/status", "r");
   int tpid;
   const char *needle = "TracerPid:";
   size_t nl = strlen(needle);
   while(fgets(buf1, 512, fin)) {
       if(!strncmp(buf1, needle, nl)) {
           sscanf(buf1, "TracerPid: %d", &tpid);
           if(tpid != 0) {
                printf("Debugger detected\n");
                return 1;
           }
       }
    }
   fclose(fin);
   printf("All good\n");
   return 0;
}
```

**P.S. 可以动态地利用这个方法来检测（可以fork出一个子进程专门负责检测）**

- 设置进程最大运行时间

原理：调试的时间一般来说远远大于程序正常运行需要的时间

```
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

void alarmHandler(int sig)
{
   printf("Debugger detected\n");
   exit(1);
}
void__attribute__((constructor))setupSig(void)
{
   signal(SIGALRM, alarmHandler);
   alarm(2);
}
int main(int argc, char *argv[])
{
   printf("All good\n");
   return 0;
}
```

**P.S. 研究一下GNU C的__attribute__机制**

```
简注：
	__attribute__((constructor)) 在main() 之前执行
	__attribute__((destructor))  在main() 执行结束之后执行

如果有多个需要这种执行方式的过程，则可以设置优先级，要注意0-100优先级系统保留，另外constructor优先级是越小越高，destructor的则相反
	__attribute__((constructor(PRIORITY)))
	__attribute__((destructor(PRIORITY)))
```

另外，这种反调试的方式很容易被绕过：在GDB中`info handle SIGALRM`查看信号是否传递给程序，可以通过`handle SIGALRM nopass`屏蔽掉信号

- 检查进程打开的fd

这个方法我觉得不是很严谨，对于稍微大一点的程序来说打开5个文件描述符是很可能的（尤其是程序员在fork进程后忘记关闭继承的文件描述符的情况），所以不记录了。

**以上方法均非常容易通过静态分析并patch绕过，需要结合代码混淆才能达到更好效果**