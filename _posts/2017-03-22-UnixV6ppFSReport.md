---
title: Unix v6-plus-plus Filesystem Analysis
category: CS
---

## Unix v6-plus-plus Filesystem Analysis

### 0x00 Preface

Filesystem plays a critical role in one operating system. In this paper, I will go into details about the filesystem in *Unix v6-plus-plus*, which comes from *Unix v6* and was modified in C-plus-plus to run on *Bochs* by our OS teachers for teaching. You can download the source code of *Unix v6-plus-plus* [here]({{ site.url }}/resources/code/Unixv6pp-src.zip).

We will call *Unix v6-plus-plus* as *Unix v6pp*.

#### Content

I will descript the filesystem in **4 parts**:

- Structure of files stored on the disc
- Structure of files opened in the memory
- Structure of file directory
- File operating interfaces

#### Source Code Files

Files below are related:

|File Name|File Name|File Name|
|:-:|:-:|:-:|
|include/FileSystem.h|include/INode.h|include/OpenFileManager.h|
|fs/FileSystem.cpp|fs/INode.cpp|fs/OpenFileManager.cpp|
|include/File.h|include/FileManager.h|include/User.h|
|fs/File.cpp|fs/FileManager.cpp||

**Now, let's be a Pirate :)**

### 0x01 Structure of files stored on the disc

In this part, our goal is to explain how the files are organized on the disc.  
Files below are related:

|File Name|
|:-:|
|include/FileSystem.h|
|fs/FileSystem.cpp|
|include/INode.h|
|fs/INode.cpp|

#### Macro-Architecture

Let's see some constants in the definition of `FileSystem` class:

{% highlight c %}
// include/FileSystem.h
class FileSystem
{
public:
	/* static consts */
	static const int SUPER_BLOCK_SECTOR_NUMBER = 200;
	static const int INODE_NUMBER_PER_SECTOR = 8;
	static const int INODE_ZONE_START_SECTOR = 202;
	static const int INODE_ZONE_SIZE = 1024 - 202;
	static const int DATA_ZONE_START_SECTOR = 1024;
	static const int DATA_ZONE_END_SECTOR = 18000 - 1;
	static const int DATA_ZONE_SIZE = 18000 -  DATA_ZONE_START_SECTOR;
    ...
}
{% endhighlight %}

From codes above we can draw up the macro-architecture with some extra knowledge about OS:

(unit: section)

|0|1 ~ 199|200 ~ 201|202|......|1023|1024|......|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|boot|Kernel Image|Super Block|DiskInode|......|DiskInode|Data Block|......|

Each section holds 512 bytes; each `DiskInode` is 64 bytes. So each section is able to hold 8 `DiskInode`s. `SuperBlock` is on 200 and 201 sections. `DiskInode`s occupy sections from 202 to 1023. Data blocks begin from NO.1024 section.

*Unix v6pp* does not manage sections from 0 to 199.

#### SuperBlock

There is only one global `SuperBlock` object in the whole system. However, each block device has its own `SuperBlock`.

```
// fs/FileSystem.cpp
SuperBlock g_spb; // global object
```

`SuperBlock` records information about a whole device. Let's see the definition of `SuperBlock`:

{% highlight c %}
// include/FileSystem.h
class SuperBlock
{
public:
	SuperBlock(); // nothing to do
	~SuperBlock(); // nothing to do
public:
	int		s_isize;
	int		s_fsize;
	int		s_nfree;
	int		s_free[100];
	int		s_ninode;
	int		s_inode[100];
	int		s_flock;
	int		s_ilock;
	int		s_fmod;
	int		s_ronly;
	int		s_time;
	int		padding[47];
};
{% endhighlight %}

In *Unix v6pp*, Constructor function and Destructor function are both empty.

Now let's talk about variables in this class.

First, these variables are easy to learn:

- `padding` enables `SuperBlock` to occupy 2 * 512 bytes (2 sections)
- `s_iszie` stores the number of sections used for `DiskInode`s
- `s_fsize` stores the number of sections
- `s_fmod` is a flag. If it is enabled, the `SuperBlock` on the disk should be update to that in the memory (modified)
- `s_ronly` is a flag, which means the filesystem is read-only
- `s_time` stores the time of the last updating operation

Second, the remaining variables are related to the management of free section blocks and free `DiskInode`s.

- `s_ninode` stores the number of free `DiskInode`s directly managed by `SuperBlock`
- `s_inode[100]` is the index table of free `DiskInode`s directly managed by `SuperBlock`. The element in this array is the index of one `DiskInode` on one device
- `s_nfree` stores the number of free data blocks directly managed by `SuperBlock`. The element in this array is the index of one section block on one device
- `s_free[100]`
- `s_ilock` is a lock to ensure mutex of different operations on `s_inode[100]`
- `s_flock` is a lock to ensure mutex of different operations on `s_free[100]`

The management of free `DiskInode`s and free section blocks is interesting. For convenience, `SuperBlock` does not directly manage all the free `DiskInode`s and free data blocks.

#### Management of Free DiskInodes

`FileSystem::IAlloc(short dev)` and `FileSystem::IFree(short dev, int number)` are used to manage free `DiskInode`s:

##### Allocate

Firstly, `sb = this->GetFS(dev);` to fetch the `SuperBlock` of current device and make sure `s_ilock` is unlocked (or wait for it is unlocked):

{% highlight c %}
sb = this->GetFS(dev);
while(sb->s_ilock){
	u.u_procp->Sleep((unsigned long)&sb->s_ilock, ProcessManager::PINOD);
}
{% endhighlight %}

If `s_inode[100]` is empty, then lock `s_ilock` and search for free `DiskInode`s and record them into `s_inode[]` until `s_ninode` is 100 or no free `DiskInode` remains. If `IALLOC` of one `DiskInode` is disabled, system will then check whether that has been loaded into memory. Only these two conditions are met can one `DiskInode` prove to be free and be added into `s_inode[]`:

{% highlight c %}
if(sb->s_ninode <= 0){
    sb->s_ilock++;
    ino = -1;
    for(int i = 0; i < sb->s_isize; i++){
        pBuf = this->m_BufferManager->Bread(dev, FileSystem::INODE_ZONE_START_SECTOR + i);
        int* p = (int *)pBuf->b_addr;
        for(int j = 0; j < FileSystem::INODE_NUMBER_PER_SECTOR; j++){
            ino++;
            int mode = *( p + j * sizeof(DiskInode)/sizeof(int) );
            if(mode != 0){
                continue;
            }
            if( g_InodeTable.IsLoaded(dev, ino) == -1 ){
                sb->s_inode[sb->s_ninode++] = ino;
                if(sb->s_ninode >= 100)
                {
                    break;
                }
            }
        }
        this->m_BufferManager->Brelse(pBuf);
        if(sb->s_ninode >= 100){
            break;
        }
    }
    sb->s_ilock = 0;
    Kernel::Instance().GetProcessManager().WakeUpAll((unsigned long)&sb->s_ilock);
    if(sb->s_ninode <= 0){
        Diagnose::Write("No Space On %d !\n", dev);
        u.u_error = User::ENOSPC;
        return NULL;
    }
}
{% endhighlight %}

If system reaches here, there must remain free `DiskInode` in `s_inode[]`. Load all the `DiskInode`s in `s_inode[]` into memory until `INodeTable` is full:

{% highlight c %}
while(true){
    ino = sb->s_inode[--sb->s_ninode];
    pNode = g_InodeTable.IGet(dev, ino);
    if(NULL == pNode){
        return NULL;
    }
    if(0 == pNode->i_mode){
        pNode->Clean();
        sb->s_fmod = 1;
        return pNode;
    }
    else{
        g_InodeTable.IPut(pNode);
        continue;
    }
}
{% endhighlight %}

Attention! When system modifies `SuperBlock` in the memory, it should enable `s_fmod`.

##### Free

This function is easy to understand. When `s_ilock` is unlocked and `s_ninode` is less than 100, then record `DiskInode` indexed by `number` in `s_inode`, or just return.

{% highlight c%}
void FileSystem::IFree(short dev, int number)
{
	SuperBlock* sb;
	sb = this->GetFS(dev);
	if(sb->s_ilock){
		return;
	}
	if(sb->s_ninode >= 100){
		return;
	}
	sb->s_inode[sb->s_ninode++] = number; // push
	sb->s_fmod = 1;
}
{% endhighlight %}

#### Management of Free Data Blocks

*Unix v6pp* uses grouping chained index table to manage free data blocks. Picture below simply shows the structure:

![unixv6pp-group-chained-index-table]({{ site.url }}/resources/pictures/unixv6pp-group-chained-index-table.png)

`FileSystem::Alloc(short dev)` and `FileSystem::Free(short dev, int blkno)` are used to manage free data blocks:

##### Allocate

When `s_flock` is unlocked, use `blkno` to fetch one free data block. If `blkno` is 0, there is no more free data block, then return. If `blkno` is invalid (checked by `BadBlock()`), then return. 

{% highlight c %}
sb = this->GetFS(dev);
while(sb->s_flock){
    u.u_procp->Sleep((unsigned long)&sb->s_flock, ProcessManager::PINOD);
}
blkno = sb->s_free[--sb->s_nfree];
if(0 == blkno ){
    sb->s_nfree = 0;
    Diagnose::Write("No Space On %d !\n", dev);
    u.u_error = User::ENOSPC;
    return NULL;
}
if( this->BadBlock(sb, dev, blkno) ){
    return NULL;
}
{% endhighlight %}

After `blkno` fetches one, if `s_nfree` is 0, then copy first 404 bytes (`s_nfree` + `s_free[100]`) from data block with the index of `SuperBlock->s_free[0]` to `SuperBlock->s_nfree` and `SuperBlock->s_free[100]`, that is, take down the indirect index table of the next group (e.g. group 4 in the picture above):

{% highlight c %}
if(sb->s_nfree <= 0){
    sb->s_flock++;
    pBuf = this->m_BufferManager->Bread(dev, blkno);
    int* p = (int *)pBuf->b_addr;
    sb->s_nfree = *p++;
    Utility::DWordCopy(p, sb->s_free, 100);
    this->m_BufferManager->Brelse(pBuf);
    sb->s_flock = 0;
    Kernel::Instance().GetProcessManager().WakeUpAll((unsigned long)&sb->s_flock);
}
pBuf = this->m_BufferManager->GetBlk(dev, blkno);
this->m_BufferManager->ClrBuf(pBuf);
sb->s_fmod = 1;

return pBuf;
{% endhighlight %}

##### Free

Firstly wait until `s_flock` is unlocked and blkno is valid:

{% highlight c %}
sb = this->GetFS(dev);
sb->s_fmod = 1;
while(sb->s_flock){
    u.u_procp->Sleep((unsigned long)&sb->s_flock, ProcessManager::PINOD);
}
if(this->BadBlock(sb, dev, blkno)){
    return;
}
{% endhighlight %}

If `blkno` is going to be the first free data block, use `s_free[0]` to mark end and use `s_free[1]` to point to this `blkno` data block; else, copy `SuperBlock->s_nfree` and `SuperBlock->s_free[100]` (404 bytes) to `blkno` data block, then use `SuperBlock->s_free[0]` to point to `blkno` data block and set `SuperBlock->s_nfree` to 1:

{% highlight c %}
if(sb->s_nfree <= 0){
    sb->s_nfree = 1;
    sb->s_free[0] = 0;
}
if(sb->s_nfree >= 100){
    sb->s_flock++;
    pBuf = this->m_BufferManager->GetBlk(dev, blkno);
    int* p = (int *)pBuf->b_addr;
    *p++ = sb->s_nfree;
    Utility::DWordCopy(sb->s_free, p, 100);
    sb->s_nfree = 0;
    this->m_BufferManager->Bwrite(pBuf);
    sb->s_flock = 0;
    Kernel::Instance().GetProcessManager().WakeUpAll((unsigned long)&sb->s_flock);
}
sb->s_free[sb->s_nfree++] = blkno;
sb->s_fmod = 1;
{% endhighlight %}

#### File Structure

In Unix, everything is a file. So In this sub-part we just talk about the conception of **File** on the layer of `DiskInode-DataBlock` model, without the specific file meanings and structures.  
In this model, one file is organised as meta-data and file-data:

![File_DiskInode_DataBlock]({{ site.url }}/resources/pictures/File_DiskInode_DataBlock.png)

Meta data helps to manage the data blocks. So let's see the definition of `DiskInode` class:

{% highlight c%}
// include/INode.h
class DiskInode
{
public:
	DiskInode();
	~DiskInode(); // nothing to do
public:
	unsigned int d_mode;
	int		d_nlink;
	short	d_uid;
	short	d_gid;
	int		d_size;
	int		d_addr[10];
	int		d_atime;
	int		d_mtime;
};
{% endhighlight %}

{% highlight c %}
// fs/Inode.cpp
DiskInode::DiskInode()
{
	this->d_mode = 0;
	this->d_nlink = 0;
	this->d_uid = -1;
	this->d_gid = -1;
	this->d_size = 0;
	for(int i = 0; i < 10; i++){
		this->d_addr[i] = 0;
	}
	this->d_atime = 0;
	this->d_mtime = 0;
}
{% endhighlight %}

`DiskInode::DiskInode()` is to initialize variables in the class. This is Necessary. When one `DiskInode` is in the stack,  not all entries will be updated. So when `sync` is operated you should set variables not updated to default values instead of values remaining on the stack before this `DiskInode` is loaded.

- `d_mode` records states of one file, lower 16 bits used:

|Mask Code|Name|Description|
|:-:|:-:|:-:|
|0000 0000 0000 0001|IEXEC (o)|other exec|
|0000 0000 0000 0010|IWRITE (o)|other write|
|0000 0000 0000 0100|IREAD (o)|other read|
|0000 0000 0000 1000|IEXEC (g)|group exec|
|0000 0000 0001 0000|IWRITE (g)|group write|
|0000 0000 0010 0000|IREAD (g)|group read|
|0000 0000 0100 0000|IEXEC (u)|user exec|
|0000 0000 1000 0000|IWRITE (u)|user write|
|0000 0001 0000 0000|IREAD (u)|user read|
|0000 0010 0000 0000|ISVTX|on Swap|
|0000 0100 0000 0000|ISGID|SGID file|
|0000 1000 0000 0000|ISUID|SUID file|
|0001 0000 0000 0000|ILARG|large or huge file|
|0110 0000 0000 0000|IFMT|file type|
|1000 0000 0000 0000|IALLOC|file used|

Definitions above can be found in `INode` class, We will talk about which in *0x02 part*.

More about `IFMT`:

```
00 - Common data file
01 - Character device file
10 - Directory file
11 - Block device file
```

- `d_nlink` counts the number of different path names for one file in the whole directory tree (That is, hard link)
- `d_uid` stores the owner's ID
- `d_gid` stores the owner group's ID
- `d_atime` stores the last access time
- `d_mtime` stores the last modified time
- `d_size` stores the size of one file (unit: byte)

From `INode` class we find some constants:

```
static const int BLOCK_SIZE = 512;
static const int ADDRESS_PER_INDEX_BLOCK = BLOCK_SIZE / sizeof(int);
static const int SMALL_FILE_BLOCK = 6;
static const int LARGE_FILE_BLOCK = 128 * 2 + 6;
static const int HUGE_FILE_BLOCK = 128 * 128 * 2 + 128 * 2 + 6;
```

Now we can calculate and sum these data:

|Small File|Large File|Huge File|
|:-:|:-:|:-:|
|[0, 6\*512]|(6\*512, 6\*512+128\*2]|(6\*512+128\*2, 6\*512+128\*2+128\*128\*2]|

(unit: byte)

Now we can talk about `d_addr[10]`. This array stores index of data blocks related.

If one is a small file, this array will be:

![unixv6pp-small-file]({{ site.url }}/resources/pictures/unixv6pp-small-file.png)

If one is a large file, this array will be:

![unixv6pp-large-file]({{ site.url }}/resources/pictures/unixv6pp-large-file.png)

Note that 1 level indirect index blocks appear.

If one is a huge file, this array will be:

![unixv6pp-huge-file]({{ site.url }}/resources/pictures/unixv6pp-huge-file.png)

Note that 2 level indirect index blocks appear.

`d_size` determines whether one is a small, large or huge file.

### 0x02 Structure of files opened in the memory

### 0x03 Structure of file directory

### 0x04 File operating interfaces

### 0x05 Summary

### 0x06 Reference

