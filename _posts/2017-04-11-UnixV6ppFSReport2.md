---
title: Unix v6-plus-plus Filesystem Analysis | Part 2
category: CS
---

## Unix v6-plus-plus Filesystem Analysis | Part 2

### 0x02 Structure of files opened in the memory

In this part, our goal is to descript structures of files opened in the memory.  
Files below are related:

|File Name|File Name|File Name|
|:-:|:-:|:-:|
|include/INode.h|include/OpenFileManager.h|include/File.h|
|fs/INode.cpp|fs/OpenFileManager.cpp|fs/File.cpp|

Exactly, we also need another file `include/User.h`, but actually we only need two statements in `User` class:

{% highlight c %}
OpenFiles u_ofiles;
IOParameter u_IOParam;
{% endhighlight %}

We only need to know that `OpenFiles` and `IOParameter` are in this class, because `User` class is the extended control block of one process.

From *[Part 1](https://brant-ruan.github.io/cs/2017/03/22/UnixV6ppFSReport.html)*, we have learnt how files are stored on the disk. That is very very good.



