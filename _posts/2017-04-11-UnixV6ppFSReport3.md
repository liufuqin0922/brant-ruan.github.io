---
title: Unix v6-plus-plus Filesystem Analysis | Part 3
category: CS
---

## Unix v6-plus-plus Filesystem Analysis | Part 3

### 0x03 Structure of file directory

In this part, our goal is to descript structures of directory file.  
Files below are related:

|File Name|File Name|
|:-:|:-:|
|include/FileManager.h|include/INode.h|

![unixv6pp-Directory-structure]({{ site.url }}/resources/pictures/unixv6pp-Directory-structure.png)

To some extent, the picture above is enough to explain this part. But for completeness, some other explanations are added:

Everything is a file, so is the directory. The data block of one directory file stores `inode-filename` entries. And follow this clue, you can find the inode of one specific file with a specific name.

That's all, thank you :)