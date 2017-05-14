---
title: Unix v6-plus-plus Exec Analysis
category: CS
---

## Unix v6-plus-plus Exec Analysis

### Preface

本文将分析`Exec`在`Unix v6pp`上的实现。  
我们知道，`Exec`往往跟在`fork`后执行，目的是为子进程建立新的进程图像，从而执行新的程序。  
`Exec`在各个平台的实现都与该平台的可执行文件格式密切相关。`Unix v6pp`使用和`Windows`相同的`PE`格式。本次分析暂不涉及`动态链接`。  

后面的分析将分为两个部分：

- PE 文件格式
- Exec 执行流程

### Portable Executable File (PE)

简单的 PE 格式如下图所示：

![unixv6pp-exec-0.png]({{ site.url }}/resources/pictures/unixv6pp-exec-0.PNG)

上图中没有出现`bss`，因为只有进入内存中时才为它分配空间。

我们不必深陷文件格式的细节，也不必把所有这些都记下来。要在脑子中始终保持一个观念，计算机是讲逻辑的，计算机科技是合理的，是可理解的。这样一来，我们在面对一个宏观层面的结构时就能够充分把握它的上上下下因为我们的问题都能够找到答案，就`PE`格式来说：

**Q**

这个东西要被执行，总要知道它第一行机器码的地址吧，有没有哪里记录这个呢？

**A**

有。`可选头`中有一项是`AddressOfEntryPoint`，它指出了程序最先执行的代码地址，它是一个相对于基准地址的偏移量。

**Q**

怎么知道它要被加载到内存中的哪里？

**A**

可以的。在`可选头`中有一项是`ImageBase`，指出了装载地址。

诸如此类，只要我们拥有一份定义格式的源码（`include/PEParser.h`），结合问题我们就能够顺利地捋出文件格式的内容存在的目的。

可执行程序要被执行，就理所当然要有办法解决这样那样如我们上面提到的问题，我们的目的是弄懂`Exec`的执行过程，所以不必陷入格式的细节。我们将继续往下分析，遇到问题解决问题即可。

### Exec

`Exec`仅仅刷新进程的用户态图像，即代码段，数据段，堆栈段。进程核心态图像不变，依旧保持`fork`之后的值。

下面正式进入`Exec`的分析。

首先看系统调用代码：

{% highlight c %}
// interrupt/SystemCall.cpp
/*	11 = exec	count = 2	*/
int SystemCall::Sys_Exec()
{
	ProcessManager& procMgr = Kernel::Instance().GetProcessManager();
	procMgr.Exec();

	return 0;	/* GCC likes it ! */
}
{% endhighlight %}

我们想一想，如果你是操作系统内核，要加载一个可执行程序到内存然后执行它，你会做些什么？

我会做：

- 找到要打开的文件
- 检查如果超过大小限制就不打开
- 检查有没有权限打开
- 解析 PE 格式，根据头部信息读入数据段
- 查看 text 块是不是已经在内存，不是则读入代码段
- 分配堆和栈
- 建立相对地址映射表
- 把之前的参数放入用户态的栈上
- EIP 设置为它的入口地址，执行程序

接下来我们分 11 个阶段讲解，看看真正是怎么样的。参考源码为`proc/ProcessManager.cpp`。

#### Stage 1 寻找文件，权限检测

寻找文件：

{% highlight c %}
pInode = fileMgr.NameI(FileManager::NextChar, FileManager::OPEN);
{% endhighlight %}

如果系统中进行图像改换的进程大于等于最大值，则睡眠：

{% highlight c %}
while( this->ExeCnt >= NEXEC )
{
    u.u_procp->Sleep((unsigned long)&ExeCnt, ProcessManager::EXPRI);
}
this->ExeCnt++;
{% endhighlight %}

检查权限。注意，如果权限检查未通过，则会把`ExeCnt`减一，因为当前程序不会被执行，所以其他等待进程可以被唤醒了。

{% highlight c %}
if ( fileMgr.Access(pInode, Inode::IEXEC) || (pInode->i_mode & Inode::IFMT) != 0 )
{
    fileMgr.m_InodeTable->IPut(pInode);
    if ( this->ExeCnt >= NEXEC )
    {
        WakeUpAll((unsigned long)&ExeCnt);
    }
    this->ExeCnt--;
    return;
}
{% endhighlight %}

#### Stage 2 解析文件头

开始按照`PE`格式解析。这里封装性做的很好，一个`parser`封装了所有细节，只需要调用它的`HeaderLoad`然后从它的成员变量中取数据就好了。

这个`HeaderLoad`十分有意思，把节头读入了核心态页表区，老师的注释说是因为核心态用不了`malloc`，且`new`动态申请有一些问题。

{% highlight c %}
PEParser parser;
if ( parser.HeaderLoad(pInode) == false )
{
    fileMgr.m_InodeTable->IPut(pInode);
    return;
}
// 正文段地址及长度
u.u_MemoryDescriptor.m_TextStartAddress = parser.TextAddress;
u.u_MemoryDescriptor.m_TextSize = parser.TextSize;
// 数据段地址及长度
u.u_MemoryDescriptor.m_DataStartAddress = parser.DataAddress;
u.u_MemoryDescriptor.m_DataSize = parser.DataSize;
// 堆栈段初始化长度
u.u_MemoryDescriptor.m_StackSize = parser.StackSize;
{% endhighlight %}

如果需要的内存大小大于用户态虚拟地址空间大小，就退出：

{% highlight c %}
if ( parser.TextSize + parser.DataSize + parser.StackSize  + PageManager::PAGE_SIZE > MemoryDescriptor::USER_SPACE_SIZE - parser.TextAddress)
{
    fileMgr.m_InodeTable->IPut(pInode);
    u.u_error = User::ENOMEM;
    return;
}
{% endhighlight %}

这里有个问题，为什么大于号右边要减去`TextAddress`呢？

#### Stage 3 保护用户栈中 exec 参数

具体来说，参数就是`argc`和`argv`。为什么要保护参数？因为我们后面要释放原进程的用户态图像，而这些参数保存在原进程的用户栈中，新程序需要这些参数，所以要保存到别的地方。

首先在核心态页表区申请一块足够大的空间（`fakestack`），并使这块空间为`8K`（2^13 bytes）的整数倍：

{% highlight c %}
int allocLength = (parser.StackSize + PageManager::PAGE_SIZE * 2 - 1) >> 13 << 13;
unsigned long fakeStack = kernelPgMgr.AllocMemory(allocLength);
{% endhighlight %}

接着定位到栈底，注意。这里上面`AllocMemory`分配的是物理内存，所以这里要转换到线性空间地址（加上`0xC0000000`）：

先放命令行参数字符串：

{% highlight c %}
int argc = u.u_arg[1];
char** argv = (char **)u.u_arg[2];
unsigned int esp = MemoryDescriptor::USER_SPACE_SIZE;
unsigned long desAddress = fakeStack + allocLength + 0xC0000000;
int length;
for (int i = 0; i < argc; i++ )
{
    length = 0;
    while( NULL != argv[i][length] )
    {
        length++;
    }
    desAddress = desAddress - (length + 1);
    Utility::MemCopy((unsigned long)argv[i], desAddress, length + 1);
    esp = esp - (length + 1);
    argv[i] = (char *)esp;
}
{% endhighlight %}

再放`argv[argc-1]`~`argv[0]`这些指针：

{% highlight c %}
desAddress = desAddress & 0xFFFFFFF0;
esp = esp & 0xFFFFFFF0;
int endValue = 0;
desAddress -= sizeof(endValue);
esp -= sizeof(endValue);
Utility::MemCopy((unsigned long)&endValue, desAddress, sizeof(endValue));

desAddress -= argc * sizeof(int);
esp -= argc * sizeof(int);
Utility::MemCopy((unsigned long)argv, desAddress, argc * sizeof(int));
{% endhighlight %}

再放`argv`这个二阶指针和`argc`：

{% highlight c %}
endValue = esp;
desAddress -= sizeof(int);
esp -= sizeof(int);
Utility::MemCopy((unsigned long)&endValue, desAddress, sizeof(int));

desAddress -= sizeof(int);
esp -= sizeof(int);
Utility::MemCopy((unsigned long)&argc, desAddress, sizeof(int));
{% endhighlight %}

至此，参数保存到了核心态页表区，结构如下：

![]({{ site.url }}/resources/pictures/unixv6pp-exec-1.PNG)

可以进行下一步释放空间的操作了。

#### Stage 4 缩小空间到 PPDA 和 proc

取消与原来的 text 块的勾连：

{% highlight c %}
if ( u.u_procp->p_textp != NULL )
{
    u.u_procp->p_textp->XFree();
    u.u_procp->p_textp = NULL;
}
{% endhighlight %}

缩小可交换部分，保留 PPDA 区。

{% highlight c %}
// USIZE 正是 PPDA 区的大小
u.u_procp->Expand(ProcessManager::USIZE);
{% endhighlight %}

#### Stage 5 分配代码段空间并写 text 块

我们知道，Text 结构是可以共享的，因为代码一般是只读的。找 Text 的逻辑是这样的：如果遇到空闲的，记下它的位置，继续找；如果遇到已经使用的，且它对应的刚好是我们需要的代码，就把它引用数加1且把寻找用的指针`pText`置`NULL`，`break`跳出。

{% highlight c %}
pText = NULL;
for ( int i = 0; i < ProcessManager::NTEXT; i++ )
{
    if ( NULL == this->text[i].x_iptr )
    {
        if ( NULL == pText )
        {
            pText = &(this->text[i]);
        }
    }
    else if ( pInode == this->text[i].x_iptr )
    {
        this->text[i].x_count++;
        this->text[i].x_ccount++;
        u.u_procp->p_textp = &(this->text[i]);
        pText = NULL;
        break;
    }
}
{% endhighlight %}

所以出循环时，如果`pText`不是`NULL`,将为新程序分配一个`Text`结构以及对应的代码段空间；否则，则不分配：

{% highlight c %}
if ( NULL != pText )
{
    pInode->i_count++;
    pText->x_ccount = 1;
    pText->x_count = 1;
    pText->x_iptr = pInode;
    pText->x_size = u.u_MemoryDescriptor.m_TextSize;
    pText->x_caddr = userPgMgr.AllocMemory(pText->x_size);
    pText->x_daddr = Kernel::Instance().GetSwapperManager().AllocSwap(pText->x_size);
    u.u_procp->p_textp = pText;
}
else
{
    pText = u.u_procp->p_textp;
    sharedText = 1;
}
{% endhighlight %}

**会不会遇到既没有空闲 Text 结构，又在现有的 Text 结构中找不到相同代码段的情况呢？**

我觉得会有，目前系统中允许的最大进程数是`NPROC=100`，允许的最多`Text`结构数是`NTEXT=50`。这种情况在源代码里似乎没有体现出来如何处理？

注意，这是仅仅是分配了空间，还没有把代码放入其中。注意`sharedText`变量，它标志了是否已存在共享正文段。

#### Stage 6 建立地址映射

之前在第四阶段进程做了“大瘦身”，这里要扩充空间了：

{% highlight c %}
unsigned int newSize = ProcessManager::USIZE + u.u_MemoryDescriptor.m_DataSize + u.u_MemoryDescriptor.m_StackSize;
u.u_procp->Expand(newSize);
{% endhighlight %}

然后，建立相对地址映射表：

{% highlight c %}
u.u_MemoryDescriptor.EstablishUserPageTable(parser.TextAddress, parser.TextSize, parser.DataAddress, parser.DataSize, parser.StackSize);
{% endhighlight %}

#### Stage 7 创建新用户态图像

接着，非常重要！读入`text`/`data`/`rdata`/`bss`段，注意它传入了`sharedText`，是为了判断需不需要把`text`读出来：

{% highlight c %}
parser.Relocate(pInode, sharedText);
{% endhighlight %}

另外，如果`sharedText`是0，那么要给`text`在`swap`区留一份副本：

{% highlight c %}
if(sharedText == 0)
{
    u.u_procp->p_flag |= Process::SLOCK;
    bufMgr.Swap(pText->x_daddr, pText->x_caddr, pText->x_size, Buf::B_WRITE);
    u.u_procp->p_flag &= ~Process::SLOCK;
}
{% endhighlight %}

上面加锁是为了保证在写磁盘期间进程不会被交换出内存。

#### Stage 8 准备命令行参数

接着，就是把第三阶段保存的参数从核心态页表区移动到用户栈中，然后释放被占用的核心态空间：

{% highlight c %}
Utility::MemCopy(fakeStack + allocLength - parser.StackSize | 0xC0000000, MemoryDescriptor::USER_SPACE_SIZE - parser.StackSize, parser.StackSize);
kernelPgMgr.FreeMemory(allocLength, fakeStack);
{% endhighlight %}

#### Stage 9 拷贝 runtime() 和 SignalHandler()

把`runtime()`和`SignalHandler()`拷到进程线性地址的起始处`0x00000000h`？

{% highlight c %}
unsigned char* runtimeSrc = (unsigned char*)runtime;
unsigned char* runtimeDst = 0x00000000;
for (unsigned int i = 0; i < (unsigned long)ExecShell - (unsigned long)runtime; i++)
{
    *runtimeDst++ = *runtimeSrc++;
}
{% endhighlight %}

为什么要拷贝？

因为在第十阶段，`exec`将把新程序的入口地址放入`eax`寄存器返回，返回后`runtime`将执行，是它负责了调用`main`以及在`main`返回后调用1号系统调用终止进程：

{% highlight c %}
extern "C" void runtime()
{
	__asm__ __volatile__("	leave;	\
							movl %%esp, %%ebp;	\
							call *%%eax;		\
							movl $1, %%eax;	\
							movl $0, %%ebx;	\
							int $0x80"::);
}
{% endhighlight %}

但是`SignalHandler`在哪里？看的不是很懂。

#### Stage 10 扫尾，准备进入用户态

这里就是一些扫尾工作了，其中比较重要的是把`main`的入口地址放进`eax`：

{% highlight c %}
u.u_ar0[User::EAX] = parser.EntryPointAddress;
{% endhighlight %}

#### Stage 11 进入用户态，调用 main 函数

开始构造`Exec`退出的环境，比如把`pContext->eip`设置为`0x00000000`，使得退出后能够转到`runtime`执行：

{% highlight c %}
struct pt_context* pContext = (struct pt_context *)u.u_arg[4];
pContext->eip = 0x00000000;
pContext->xcs = Machine::USER_CODE_SEGMENT_SELECTOR;
pContext->eflags = 0x200;
pContext->esp = esp;
pContext->xss = Machine::USER_DATA_SEGMENT_SELECTOR;
{% endhighlight %}

让我们再回顾一下`runtime`中的一条指令：

```
call *%%eax
```

至此，天下纷争结束，`main`开始执行。

### 结语

纵览全篇，无非是数据拷贝来拷贝去，并对它进行解释。只不过不同的运算被我们赋予了不同的意义。抽象出来就是冯·诺依曼的模型：输入/控制器运算器存储器/输出。

很有意思，对吧？