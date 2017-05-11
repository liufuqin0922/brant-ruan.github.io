---
category: CS
title: Expert C Programming Notes
---

## Expert C Programming Notes

> 0 then 1, 1 then B, B then C, C then EVERYTHING :)

### 0x00 Preface

#### if(i = 3）

我们不时会犯下面这个错误：

```
if(i = 3){...}
```

事实上我们希望表达的是

```
if(i == 3){...}
```

一个小技巧是把两边的量反过来写：

```
if(3 = i){...}
```

上面这样可以让编译器报错，从而让你发现错误。这个技巧在判断与一个常量或字面量的相等关系时很有用。

#### time_t

我们将探究一下`time_t`。 借助`Eclipse`，我们可以方便地进行符号定位. 下面的探索基于`Linux 4.10.10`。

`include/linux/types.h`:

```
typedef __kernel_time_t		time_t;
```

`include/uapi/asm-generic/posix_types.h`:

```
typedef __kernel_long_t	__kernel_time_t;
typedef long		__kernel_long_t;
```

我们可以使用下面的程序找到`time_t`能表示的一个大值（UTC时间，64位机器）：

{% highlight c %}
time_t tmax = 0x7FFFFFFFFFFFFF;
printf("%s\n", asctime(gmtime(&tmax)));
{% endhighlight %}

```
Sun Jun 13 06:26:07 1141709097
```

到`1141709097`年，不知人类是否依然存在，是否还会使用计算机呢？

但是`long`占 8 字节，当我给`tmax`赋值为`0x7FFFFFFFFFFFFFFF`时会出现段错误，这是为什么？（上面我并没有打印出`tmax`的最大值）。

### 0x01 C Through the Mists of Time

```
// 三个大神
Ken Thompson | Dennis Ritchie | Brian Kernighan
```

早期 C 语言的许多特性是为了方便编译器设计者而建立的。如：

- 数组下标从 0 开始而非 1

因为偏移量的概念在编译器设计者心中已经根深蒂固。

- 基本数据类型直接与底层硬件对应

所以 C 一开始不支持浮点，直到支持浮点的硬件出现后。

- auto 是缺省的变量内存分配模式
- 数组名可以被看做指针
- float 自动被扩展为 double
- 不允许函数的嵌套定义
- register 关键字

Steve Bourne 编写的 shell 使用的脚本语言是 C 代码的变形，使用了宏定义：

```
#define STRING char *
#define IF if(
#define THEN ){
#define ELSE }else{
#define FI ;}
#define WHILE while(
#define DO ){
#define OD ;}
#define INT int
#define BEGIN{
#define END }
```

他的这种 C 语言变形促成了国际 C 语言混乱代码大赛......

C 语言标准的官方名称：`ISO/IEC 9899:1990`，不妨找来标准读一读。

### 0x02 It's Not a Bug, It's a Language Feature

C 中的作用域：要么全局可见，要么对其他文件都不可见。全局可见性与`interpositioning`特性之间可能有冲突。

关于优先级的建议：记住乘法和除法优先于加法和减法，其他的一律带上括号。

### 0x03 Unscrambling Declarations in C

下面这是个啥？

```
char * const *(*next)();
```

位域的使用：

{% highlight c %}
struct pid_tag{
	unsigned int inactive : 1;
	unsigned int : 1; // padding
	unsigned int refcount : 6;
	unsigned int  : 0; // padding
	short pid_id;
    struct pid_tag *link;
}
{% endhighlight %}

不要为了方便而对结构体使用`typedef`，多写一个`struct`有时很有用。

### 0x04 The Shocking Truth: C Arrays and Pointers Are NOT the Same!

### 0x05 Thinking of Linking

### 0x06 Poetry in Motion: Runtime Data Structures

### 0x07 Thanks for the Memory

### 0x08 Why Programmers Can't Tell Halloween from Christmas Day

### 0x09 More about Arrays

### 0x0A More About Pointers

### 0x0B You Know C, So C++ is Easy!
