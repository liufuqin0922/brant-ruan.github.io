---
title: Unix v6-plus-plus Filesystem Analysis | Part 4
category: CS
---

## Unix v6-plus-plus Filesystem Analysis | Part 4

### 0x04 File operating interfaces

In this part, our goal is to descript **File Operating Interface**  
Files below are related:

|File Name|File Name|
|:-:|:-:|
|include/FileManager.h|fs/FileManager.cpp|

I plan to analyse these methods:

```
void FileManager::Open()
void FileManager::Creat()
void FileManager::Open1(Inode* pInode, int mode, int trf)
void FileManager::Close()
void FileManager::Seek()
void FileManager::Read()
void FileManager::Write()
void FileManager::Rdwr(enum File::FileFlags mode)
Inode* FileManager::NameI(char (*func)(), enum DirectorySearchMode mode)
```

There are also some other important methods in `FileManager`. But here we currently care about I/O related. And we follow the general operating order, that is, first open, then seek one position, then read or write and finally close one file.

#### Open/Create/Open1/NameI

The relationship among these 4 methods is interesting! See the picture below:

![unixv6pp-OpenCreat]({{ site.url }}/resources/pictures/unixv6pp-OpenCreat.png)

`NextChar()` is a method to return the next `char` in pathname. If `NameI` return NULL, then `Open` will directly return without calling `Open1`, while `Creat` will call `MakNode` to return a new `Inode` to `pInode` if no error occurs. And `Creat` will do `pInode->i_mode |= newACCMode`.

**NameI**

Now dive into `NameI`. This method is so important that it translates pathname to `Inode`. But this method is complex, so be patient :)

![unixv6pp-NameI-structure]({{ site.url }}/resources/pictures/unixv6pp-NameI-structure.png)

The *out* part only has two statements:

{% highlight c %}
this->m_InodeTable->IPut(pInode);
return NULL;
{% endhighlight %}

When error occurs, `goto out` will be done.

In *preapre* part, it is very clear:

{% highlight c %}
pInode = u.u_cdir;
if ( '/' == (curchar = (*func)()) )
    pInode = this->rootDirInode;
this->m_InodeTable->IGet(pInode->i_dev, pInode->i_number);
while ( '/' == curchar )
    curchar = (*func)();
if ( '\0' == curchar && mode != FileManager::OPEN ){
    u.u_error = User::ENOENT;
    goto out;
}
{% endhighlight %}

With pathname like `/home/temp`, `pInode` will be assigned `rootDirInode`; with `home/temp`, `pInode` will be current directory. With `///home/temp`, `//` is skipped. And if you want to modify the current directory, error occurs and `goto out`.

We will take a pathname example: `/home/temp`.

Before program goes into `while`, `pInode` points to `Inode` of `/` and `curchar` is `h`.

In `while`, first do some `pre-configure`:

{% highlight c %}
if (u.u_error != User::NOERROR)
    break;	/* error, goto out; */
if ('\0' == curchar)
    return pInode; // succeed, return
if ( (pInode->i_mode & Inode::IFMT) != Inode::IFDIR ){
    u.u_error = User::ENOTDIR;
    break;	/* not dir, goto out; */
}
if ( this->Access(pInode, Inode::IEXEC) ){
    u.u_error = User::EACCES;
    break; /* no search right, goto out; */
}
{% endhighlight %}

Then copy `home` to `u.u_dbuf` and `curchar` now stores `t`.

Before search:

```
u.u_IOParam.m_Offset = 0;
u.u_IOParam.m_Count = pInode->i_size / (DirectoryEntry::DIRSIZ + 4);
freeEntryOffset = 0;
pBuf = NULL;
```

Now search `home` in `/`'s directory entry in a `sub-while`:

**Open1**

Now let's dive into `Open1`.

#### Seek

#### Read/Write/Rdwr

`Read`:

```
this->Rdwr(File::FREAD);
```

`Write`:

```
this->Rdwr(File::FWRITE);
```

So let's see `Rdwr`:

{% highlight c %}
pFile = u.u_ofiles.GetF(u.u_arg[0]);	/* fd */
if ( NULL == pFile )
    return;
if ( (pFile->f_flag & mode) == 0 ){
    u.u_error = User::EACCES;
    return;
}
u.u_IOParam.m_Base = (unsigned char *)u.u_arg[1];
u.u_IOParam.m_Count = u.u_arg[2];
u.u_segflg = 0;
if(pFile->f_flag & File::FPIPE){
    if ( File::FREAD == mode )
        this->ReadP(pFile);
    else
        this->WriteP(pFile);
}
else{
    pFile->f_inode->NFlock();
    u.u_IOParam.m_Offset = pFile->f_offset;
    if ( File::FREAD == mode )
        pFile->f_inode->ReadI();
    else
        pFile->f_inode->WriteI();
    pFile->f_offset += (u.u_arg[2] - u.u_IOParam.m_Count);
    pFile->f_inode->NFrele();
}
u.u_ar0[User::EAX] = u.u_arg[2] - u.u_IOParam.m_Count;
{% endhighlight %}


#### Close

{% highlight c %}
void FileManager::Close()
{
	User& u = Kernel::Instance().GetUser();
	int fd = u.u_arg[0];

	File* pFile = u.u_ofiles.GetF(fd);
	if ( NULL == pFile )
		return;
	u.u_ofiles.SetF(fd, NULL);
	this->m_OpenFileTable->CloseF(pFile);
}
{% endhighlight %}

Use `pFile` to fetch the `File` structure and set `File*` in `OpenFiles` to `NULL` then call `CloseF`.