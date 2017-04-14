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

Now dive into `NameI`. This method is so important that it translates pathname to `Inode`. But this method is complex, so be patient :)

![unixv6pp-NameI-structure]({{ site.url }}/resources/pictures/unixv6pp-NameI-structure.png)

We will follow the picture above to explain it. And we will take a pathname example: `/home/temp`.

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

Before program goes into `while`, `pInode` points to `Inode` of `/` and `curchar` is `h`.

#### Seek

#### Read/Write/Rdwr

#### Close