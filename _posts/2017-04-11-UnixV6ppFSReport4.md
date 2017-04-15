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

{% highlight c %}
while (true){
    if ( 0 == u.u_IOParam.m_Count ){ // search over
        if ( NULL != pBuf )
            bufMgr.Brelse(pBuf);
        // if create new file
        if ( FileManager::CREATE == mode && curchar == '\0' ){
            // check whether have right to write
            if ( this->Access(pInode, Inode::IWRITE) ){
                u.u_error = User::EACCES;
                goto out;
            }
            // store parent inode for WriteDir()
            u.u_pdir = pInode;
            if ( freeEntryOffset )
                u.u_IOParam.m_Offset = freeEntryOffset - (DirectoryEntry::DIRSIZ + 4); // store offset for WriteDir()
            else
                pInode->i_flag |= Inode::IUPD;
            return NULL; // find the free entry so return
        }
        u.u_error = User::ENOENT;
        goto out;
    }
    // current block been read out, read the next block
    if ( 0 == u.u_IOParam.m_Offset % Inode::BLOCK_SIZE ){
        if ( NULL != pBuf )
            bufMgr.Brelse(pBuf);
        int phyBlkno = pInode->Bmap(u.u_IOParam.m_Offset / Inode::BLOCK_SIZE );
        pBuf = bufMgr.Bread(pInode->i_dev, phyBlkno );
    }
    // read the next directory entry into u.u_dent
    int* src = (int *)(pBuf->b_addr + (u.u_IOParam.m_Offset % Inode::BLOCK_SIZE));
    Utility::DWordCopy( src, (int *)&u.u_dent, sizeof(DirectoryEntry)/sizeof(int) );
    u.u_IOParam.m_Offset += (DirectoryEntry::DIRSIZ + 4);
    u.u_IOParam.m_Count--;
    if ( 0 == u.u_dent.m_ino ){ // skip empty entry
        if ( 0 == freeEntryOffset )
            freeEntryOffset = u.u_IOParam.m_Offset;
        continue;
    }
    int i;
    // compare entry string
    for ( i = 0; i < DirectoryEntry::DIRSIZ; i++ )
        if ( u.u_dbuf[i] != u.u_dent.m_name[i] )
            break;
    if( i < DirectoryEntry::DIRSIZ ) // not the same
        continue;
    else
        break; // same, break
}
{% endhighlight %}

We should pay attention to some variables: `pInode` points to current directory we search in; `curchar` points to the next `char` in current part of path; `u.u_dbuf[]` stores string we look for; `u.u_dent.m_name[]` stores one directory entry's name.

If the `sub-while` is `break`, it means part matches successfully. And go ahead:

{% highlight c %}
// if this is DELETE operation
if ( FileManager::DELETE == mode && '\0' == curchar ){
    if ( this->Access(pInode, Inode::IWRITE) ){
        u.u_error = User::EACCES;
        break;	/* goto out; */
    }
    return pInode;
}
{% endhighlight %}

Arriving here, there is a `home` entry in `/`. So program will dive into `home` and continue:

{% highlight c %}
short dev = pInode->i_dev;
this->m_InodeTable->IPut(pInode);
pInode = this->m_InodeTable->IGet(dev, u.u_dent.m_ino);
if ( NULL == pInode )
    return NULL;
{% endhighlight %}

`NameI` is complex, but not awesome.

**Open1**

Now let's dive into `Open1`.

In *Part 2*, we see the open structure in details. Now let's see it from the view of methods and classes:

![unixv6pp-openfile-methods]({{ site.url }}/resources/pictures/unixv6pp-openfile-methods.png)

#### Seek

We all know the function of `Seek`. Now let's see how it make it.

{% highlight c %}
int fd = u.u_arg[0];
pFile = u.u_ofiles.GetF(fd);
if ( NULL == pFile ) // no such file in memory (maybe not open)
    return;
{% endhighlight %}

`PIPE` file is not allowed to be sought:

{% highlight c %}
if ( pFile->f_flag & File::FPIPE ){
    u.u_error = User::ESPIPE;
    return;
}
{% endhighlight %}

Unit of length will change from byte to 512 bytes if u_arg[2] > 2:

{% highlight c %}
int offset = u.u_arg[1];
if ( u.u_arg[2] > 2 ){
    offset = offset << 9;
    u.u_arg[2] -= 3;
}
{% endhighlight %}

Code below sets the r/w offset:

{% highlight c %}
switch ( u.u_arg[2] ){
    case 0:
        pFile->f_offset = offset;
        break;
    case 1:
        pFile->f_offset += offset;
        break;
    case 2:
        pFile->f_offset = pFile->f_inode->i_size + offset;
        break;
}
{% endhighlight %}

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
pFile = u.u_ofiles.GetF(u.u_arg[0]); /* fd */
if ( NULL == pFile )
    return;
if ( (pFile->f_flag & mode) == 0 ){ // r/w mode invalid
    u.u_error = User::EACCES;
    return;
}
u.u_IOParam.m_Base = (unsigned char *)u.u_arg[1];
u.u_IOParam.m_Count = u.u_arg[2]; // r/w bytes
u.u_segflg = 0;
if(pFile->f_flag & File::FPIPE){ // pipe r/w
    if ( File::FREAD == mode )
        this->ReadP(pFile);
    else
        this->WriteP(pFile);
}
else{
    pFile->f_inode->NFlock();
    u.u_IOParam.m_Offset = pFile->f_offset; // set offset
    if ( File::FREAD == mode )
        pFile->f_inode->ReadI();
    else
        pFile->f_inode->WriteI();
    pFile->f_offset += (u.u_arg[2] - u.u_IOParam.m_Count); // update offset
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