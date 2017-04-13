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

#### Integral Comprehension

Firstly, we'd better have an integral comprehension:

![unixv6pp-open-files-structure]({{ site.url }}/resources/pictures/unixv6pp-open-files-structure.png)

You may note that all these structures have nothing to do with **filename**. That is because the filename is stored in directory files and we will talk about that in *[Part 3](https://brant-ruan.github.io/cs/2017/04/11/UnixV6ppFSReport3.html)*.

The index of entries in `OpenFiles` is the famous `fd` (file descriptor).

It will be comprehensible if we talk about this topic **step by step** because we can show a dynamic process.

#### From DiskInode to INode

![unixv6pp-DiskInode2Inode]({{ site.url }}/resources/pictures/unixv6pp-DiskInode2Inode.png)

The picture above means that we will map one `DiskInode` on the disk to one `INode` in the memory.

First, let's study the `INode` class, whose variables are very similar to those in `DiskInode` class:

|INode|DiskInode|INode|DiskInode|INode|DiskInode|
|:-:|:-:|:-:|:-:|:-:|:-:|
|i_mode|d_mode|rablock|/|/|d_atime|
|i_nlink|d_nlink|i_flag|/|/|d_mtime|
|i_uid|d_uid|i_count|/|||
|i_gid|d_gid|i_dev|/|||
|i_size|d_size|i_number|/|||
|i_addr[10]|d_addr[10]|i_lastr|/|||

The duplicate variables won't be explained. We focus on the new in `INode`:

- `i_dev` stores ID of the device from which one `DiskInode` comes
- `i_number` stores ID of one `DiskInode` on a disk
- `i_flag` stores some flags:

|Mask Code|Name|Description|
|:-:|:-:|:-:|
|0000 0001|ILOCK|inode locked|
|0000 0010|IUPD|inode modified|
|0000 0100|IACC|inode accessed|
|0000 1000|IMOUNT|inode used to mount sub fs|
|0001 0000|IWANT|inode waited for by process|
|0010 0000|ITEXT|inode related to text segment|

- `i_count` stores number of instances referencing this inode. If it is 0, this inode is free
- `i_lastr` stores logic ID of the last block read to judge whether to do read-ahead operation
- `rablock` stores physical ID of the next block for read-ahead

`INode` does not care about `d_atime` and `d_mtime`.

Attention! Relationship between one `INode` and one `DiskInode` is one-to-one.

`INode` class provides some important methods:

{% highlight c %}
int Bmap(int lbn);
void ReadI();
void WriteI();
{% endhighlight %}

**Bmap**

`Bmap` is to translate logic block number (lbn) into physical block number (phyBlkno), on which other methods rely. Exactly, `lbn` is the index of one entry in `i_addr[0] ~ i_addr[5]` for small files, `i_addr[0] ~ i_addr[5] + extra 1 level indirect index block` for large files or `i_addr[0] ~ i_addr[5] + extra 1 level indirect index block + 2 level indirect index block` for huge files. `phyBlkno` is the value of such an entry.

The structure of `Bmap` is very clear (in pseudocode):

```
if lbn >= HUGE_FILE_BLOCK, return (lbn invalid)
if lbn < 6 (small file)
	phyBlkno = i_addr[lbn] (fetch directly)
    if phyBlkno is 0 then allocate
        if allocate successfully
        	phyBlkno = pFirstBuf->b_blkno (fetch number)
            i_addr[lbn] = phyBlkno (map)
            rablock = this->i_addr[lbn + 1] (read-ahead)
        else (fail to allocate)
	        rablock = this->i_addr[lbn + 1]
    return phyBlkno
else (large/huge file)
	use lbn to calculate index1 in i_addr[]
    phyBlkno = this->i_addr[index1] (fetch it)
    if phyBlkno is 0 then allocate 1 level indirect index block
    	if failed then return
        i_addr[index1] = pFirstBuf->b_blkno (map)
    read the 1 level indirect index block and point by iTable
    if this is a huge file
    	use lbn to calculate index2 in 1 level indirect index block
        phyBlkno = iTable[index2]
        if phyBlkno is 0 then allocate 2 level block
        read the 2 level block and point by iTable
    phyBlkno = iTable[index] (if 0 then allocate)
    deal with read-ahead
    return phyBlkno
```

**ReadI**

This method is to read file data.

```
if u_IOParam.m_Count is 0 then return (nothing rest)
if inode is char device then invoke Read() of CharDevice and return
while (no error and u_IOParam.m_Count is not 0)
	fetch dev and use Bmap to get bn
    pBuf = bufMgr.Bread(dev, bn)
    IOMove(start, u.u_IOParam.m_Base, nbytes) (copy to user)
    update u.u_IOParam
```

**WriteI**

This method is to read data to file.

```

```

Now you have learnt most of `INode` class. Let's continue to see how one `DiskInode` is mapped to one `INode`.

#### Between OpenFileTable and InodeTable

![unixv6pp-Inode2File]({{ site.url }}/resources/pictures/unixv6pp-Inode2File.png)

Here we begin with the system call `SystemCall::Sys_Open()`. This API is famous and clear, and we will dive into something else interesting :)

In `SystemCall::Sys_Open()`:

```
fileMgr.Open();
```

`fileMgr` is an object of `FileManager` class, which has three important pointers:

{% highlight c %}
FileSystem* m_FileSystem;
InodeTable* m_InodeTable;
OpenFileTable* m_OpenFileTable;
{% endhighlight %}

So you can see it is the very chief. We will talk more about `FileManager` in *Part 3* and *Part 4*. Now let's see `FileManager::Open()`:

{% highlight c %}
this->Open1(pInode, u.u_arg[1], 0);
{% endhighlight %}

As we see, It has Another `FileManager::Open1()` used not only by `FileManager::Open()` but also by `FileManager::Creat()`. Dive into it and we can see:

{% highlight c %}
File* pFile = this->m_OpenFileTable->FAlloc();
if ( NULL == pFile )
{
	this->m_InodeTable->IPut(pInode);
	return;
}
pFile->f_flag = mode & (File::FREAD | File::FWRITE);
pFile->f_inode = pInode;
{% endhighlight %}

#### Between ProcessOpenFileTable and OpenFileTable

![unixv6pp-File2FileStar]({{ site.url }}/resources/pictures/unixv6pp-File2FileStar.png)