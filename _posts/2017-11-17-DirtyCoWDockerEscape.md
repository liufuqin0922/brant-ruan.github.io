---
title: CVE-2016-5195 实验 | DirtyCoW与Docker逃逸
category: Sec
---

## CVE-2016-5195 实验 | DirtyCoW与Docker逃逸

### 0x00 前述

最近出比赛题用到Docker，于是就想到了脏牛火的那段时间有一个利用它做Docker逃逸的PoC。再一看，发现和`vdso`有关，恰好最近研究溢出也遇到了这个东西（在我的[另一篇博文](http://aptx4869.me/ctf/2017/09/08/Overflow.html)中）。

### 0x01 环境搭建

手头有一个`ubuntu-14.04.4-desktop-amd64.iso`就直接拿来开新的VM了。之前也一直想过这个问题：研究漏洞需要老的内核，官网上好像不好直接下老的。如果恰好没有旧的VM或者镜像，可以考虑装一个新的VM然后做一下内核降级（我没有做），可以参考[这里]()。

Docker的安装可以参考[官方文档](https://docs.docker.com/engine/installation/linux/ubuntu/#/prerequisites)。不过也可以直接把官方文档里的步骤写成下面这个脚本（不保证未来能用）：

```bash
sudo apt-get update

sudo apt-get install -y \
        linux-image-extra-$(uname -r) \
        linux-image-extra-virtual

sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"

sudo apt-get update
sudo apt-get install -y docker-ce
```

之后似乎非root用户不能用`docker ps`，解决一下：

```bash
sudo groupadd docker
sudo gpasswd -a ${USER} docker
sudo service docker restart
```

退出当前用户重新登陆一下就好。

最后看一下目前的环境：

```
uname -a
    Linux br-virtual-machine 4.2.0-27-generic #32~14.04.1-Ubuntu SMP Fri Jan22 
    15:32:26 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux

docker -v

    Docker version 17.09.0-ce, build afdb6d4
```

### 0x02 实验

### 0x03 原理

### 0x04 参考

- [脏牛漏洞-Docker逃逸POC(dirtycow-vdso)代码分析](http://blog.csdn.net/enjoy5512/article/details/53196047)
- [【技术分享】利用Dirty Cow实现docker逃逸（附演示视频）](http://bobao.360.cn/learning/detail/3168.html)
- [github: scumjr/dirtycow-vdso](https://github.com/scumjr/dirtycow-vdso)
- [github: gebl/dirtycow-docker-vdso](https://github.com/gebl/dirtycow-docker-vdso)