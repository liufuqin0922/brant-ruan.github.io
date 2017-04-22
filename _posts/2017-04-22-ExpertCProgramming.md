---
category: CS
title: Expert C Programming Notes
---

## Expert C Programming Notes

> 0 then 1, 1 then B, B then C, C then EVERYTHING :)

### 0x00 Preface

我们不时会犯下面这个错误：

```
if(i = 3){...}
```

事实上我们希望表达的是

```
if(i == 3){...}
```

一个小技巧是把两边的量反过来写：

```
if(3 = i){...}
```

上面这样可以让编译器报错，从而让你发现错误。这个技巧在判断与一个常量或字面量的相等关系时很有用。

### 0x01 C Through the Mists of Time

### 0x02 It's Not a Bug, It's a Language Feature

### 0x03 Unscrambling Declarations in C

### 0x04 The Shocking Truth: C Arrays and Pointers Are NOT the Same!

### 0x05 Thinking of Linking

### 0x06 Poetry in Motion: Runtime Data Structures

### 0x07 Thanks for the Memory

### 0x08 Why Programmers Can't Tell Halloween from Christmas Day

### 0x09 More about Arrays

### 0x0A More About Pointers

### 0x0B You Know C, So C++ is Easy!
