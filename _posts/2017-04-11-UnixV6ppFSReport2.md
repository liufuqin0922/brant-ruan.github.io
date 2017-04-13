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

The picture above means that we will map one `DiskInode` on the disk to one `Inode` in the memory.

First, let's study the `Inode` class, whose variables are very similar to those in `DiskInode` class:

|INode|DiskInode|INode|DiskInode|INode|DiskInode|
|:-:|:-:|:-:|:-:|:-:|:-:|
|i_mode|d_mode|rablock|/|/|d_atime|
|i_nlink|d_nlink|i_flag|/|/|d_mtime|
|i_uid|d_uid|i_count|/|||
|i_gid|d_gid|i_dev|/|||
|i_size|d_size|i_number|/|||
|i_addr[10]|d_addr[10]|i_lastr|/|||

The duplicate variables won't be explained. We focus on the new in `Inode`:

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

`Inode` does not care about `d_atime` and `d_mtime`.

Attention! Relationship between one `Inode` and one `DiskInode` is one-to-one.

`Inode` class provides some important methods:

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
    update u_IOParam
```

**WriteI**

This method is to write data to file.

```
if inode is char device then invoke Write() of CharDevice and return
if u_IOParam.m_Count is 0 then return (nothing rest)
while (no error and u_IOParam.m_Count is not 0)
	fetch dev and use Bmap to get bn
    if data to write is 512 bytes, then allocate buffer
    else firstly read out already existed data
    calculate where to write: start = pBuf->b_addr + offset
    IOMove(u.u_IOParam.m_Base, start, nbytes) (copy)
    update u_IOParam variables
    if one data block is full then rsync write (Bawrite)
    else delay and write (Bdwrite)
    update i_size (file's size)
```

Now you have learnt most of `Inode` class. Let's continue to see how one `DiskInode` is mapped to one `Inode`.

This process is mainly operated by `Inode* IGet(short dev, int inumber)` in `InodeTable`. In *Unix v6pp*, `InodeTable` has an inode array `m_Inode[NINODE]` (`NINODE` = 100). `IGet()` is to map `DiskInode` to one `Inode`. In addition, `IPut()` is to decrease `i_count` or free one `Inode`.

`Inode* InodeTable::IGet(short dev, int inumber)`:

```
while
    First use IsLoaded(dev, inumber) to check whether already mapped
    if already mapped,
        pInode = &(this->m_Inode[index]) (try to fetch it)
        if inode locked, then want it and sleep
        if sub-fs is mounted at this inode, then
            dev = pMount->m_dev (fetch real device number)
            inumber = FileSystem::ROOTINO (fetch real inode number)
            continue in while
        pInode->i_count++ (reference number increase)
        lock
        return pInode
    else
		GetFreeInode()
        if allocate successfully
        	set i_dev/i_number/i_flag/i_count/i_lastr
        Bread() to read in DiskInode
        if I/O error occurs, release buffer and IPut()
        pInode->ICopy(pBuf, inumber) (copy to Inode)
        release buffer
        return pInode
```

We can have short look at `Inode::ICopy()`:

{% highlight c %}
void Inode::ICopy(Buf *bp, int inumber)
{
	DiskInode dInode;
	DiskInode* pNode = &dInode;
    unsigned char* p = bp->b_addr + (inumber % FileSystem::INODE_NUMBER_PER_SECTOR) * sizeof(DiskInode);
    Utility::DWordCopy( (int *)p, (int *)pNode, sizeof(DiskInode)/sizeof(int) );
    this->i_mode = dInode.d_mode;
    this->i_nlink = dInode.d_nlink;
    this->i_uid = dInode.d_uid;
    this->i_gid = dInode.d_gid;
    this->i_size = dInode.d_size;
    for(int i = 0; i < 10; i++){
        this->i_addr[i] = dInode.d_addr[i];
    }
}
{% endhighlight %}

Very easy, right?

By the way, I want to show you the process of `IPut()`. When one file is `close()`, `IPut` will be invoked.

```
if pNode->i_count == 1 (only one reference)
	lock
    if i_nlink <=0 (no directory path points to it)
    	ITrunc() (truncate data block)
        i_mode = 0
        IFree(pNode->i_dev, pNode->i_number) (free DiskInode)
    IUpdate(Time::time) (update DiskInode)
    Prele() (unlock Inode)
    i_flag = 0
    i_number = -1
i_count--
Prele() (unlock Inode)
```

So far, we have mapped `DiskInode` to `Inode`.

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

**Note that `pFile->f_inode = pInode` connects `Inode` with `File`.**

#### Between ProcessOpenFileTable and OpenFileTable

![unixv6pp-File2FileStar]({{ site.url }}/resources/pictures/unixv6pp-File2FileStar.png)

Here we are interested in `OpenFileTable`. In *Unix v6pp*, `m_File[NFILE]` in it has 100 `File` objects.

`File* FAlloc()` is to allocate one free `File` in `m_File[]`.

```
fd = u.u_ofiles.AllocFreeSlot() (find one free File* in Process)
if fd < 0 return NULL (Process is unable to open more file)
for(int i = 0; i < OpenFileTable::NFILE; i++)
	if(this->m_File[i].f_count == 0) (free to use)
    	u.u_ofiles.SetF(fd, &this->m_File[i])
        this->m_File[i].f_count++
        this->m_File[i].f_offset = 0
        return (&this->m_File[i])
return NULL
```

**Note that `u.u_ofiles.SetF(fd, &this->m_File[i])` connects `File*` in `OpenFiles` with `File` in `OpenFileTable`.**

We can dive into `OpenFiles::SetF(int fd, File* pFile)`:

{% highlight c %}
	if(fd < 0 || fd >= OpenFiles::NOFILES){
		return;
	this->ProcessOpenFileTable[fd] = pFile;
{% endhighlight %}

All the relationship in the integral picture has been talked about. At last, we will explore `OpenFileTable::CloseF(File *pFile)`, which is to decrease `f_count` or free one `File`:

{% highlight c %}
if(pFile->f_flag & File::FPIPE){
    pNode = pFile->f_inode;
    pNode->i_mode &= ~(Inode::IREAD | Inode::IWRITE);
    procMgr.WakeUpAll((unsigned long)(pNode + 1));
    procMgr.WakeUpAll((unsigned long)(pNode + 2));
}
{% endhighlight %}

Code above is to deal with `pipe` which we Currently do not analyse.

{% highlight c %}
if(pFile->f_count <= 1)
   	pFile->f_inode->CloseI(pFile->f_flag & File::FWRITE);
	g_InodeTable.IPut(pFile->f_inode);
}
{% endhighlight %}

if `f_count` <= 1 then current process is the last process referencing this `File`. For special block device or char device invoke `CloseI`. For common file, just invoke `IPut` which we have talked about before.

Finally, 

{% highlight c %}
pFile->f_count--;
{% endhighlight %}

In `File` there is a `f_count` and in `Inode` there is a `i_count`. This idea is graceful.