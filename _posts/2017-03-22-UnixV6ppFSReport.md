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
|fs/File.cpp|fs/FileManager.cpp|||

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

First, I will explain variables easy to learn:

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

{% highlight c %}
Inode* FileSystem::IAlloc(short dev)
{
	SuperBlock* sb;
	Buf* pBuf;
	Inode* pNode;
	User& u = Kernel::Instance().GetUser();
	int ino;
	sb = this->GetFS(dev);
	while(sb->s_ilock){
		u.u_procp->Sleep((unsigned long)&sb->s_ilock, ProcessManager::PINOD);
	}
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
	return NULL;	/* GCC likes it! */
}
{% endhighlight %}

##### Free

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

`FileSystem::Alloc(short dev)` and `FileSystem::Free(short dev, int blkno)` are used to manage free data blocks:

##### Allocate

{% highlight c %}
Buf* FileSystem::Alloc(short dev)
{
	int blkno;
	SuperBlock* sb;
	Buf* pBuf;
	User& u = Kernel::Instance().GetUser();
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
}
{% endhighlight %}

##### Free

{% highlight c %}
void FileSystem::Free(short dev, int blkno)
{
	SuperBlock* sb;
	Buf* pBuf;
	User& u = Kernel::Instance().GetUser();
	sb = this->GetFS(dev);
	sb->s_fmod = 1;
	while(sb->s_flock){
		u.u_procp->Sleep((unsigned long)&sb->s_flock, ProcessManager::PINOD);
	}
	if(this->BadBlock(sb, dev, blkno)){
		return;
	}
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
}
{% endhighlight %}

#### File Structure

In Unix, everything is a file. So In this sub-part we just talk about the conception of **File** on the layer of `DiskInode-DataBlock` model, without the specific file meanings and structures.

### 0x02 Structure of files opened in the memory

### 0x03 Structure of file directory

### 0x04 File operating interfaces

### 0x05 Summary

### 0x06 Reference

