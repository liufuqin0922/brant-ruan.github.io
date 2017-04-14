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

Now dive into `NameI`.

#### Seek

#### Read/Write/Rdwr

#### Close