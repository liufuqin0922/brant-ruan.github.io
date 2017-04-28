---
category: Linux
title: ELF Code Injection
---

## ELF Code Injection

### Preface

For ELF standard, see [here](https://brant-ruan.github.io/linux/2016/08/25/ELF-%E6%A0%87%E5%87%86.html).  
For ELF Parser, see [here](https://brant-ruan.github.io/linux/2017/04/28/ELFParse.html).

In this paper, I will discuss ELF code injection.

- Find entry point
- Find image base address
- Find .text section address and size on the disk
- Find code cave to hold shellcode
- Write Shellcode

### Experiment Environment

OS: Red Hat Enterprise Linux 7.1 64-bit  
Kernel Version: 3.10.0  
P.S. VMware workstation

### Entry Point

### Code Cave

### Shellcode

#### Socket Shell

##### TCP Shell

##### Reverse TCP Shell

#### Encoding/Decoding

##### mprotect()

To complete a PoC, we implement **XOR** encoding and decoding here.

### References

- [ELF Binary Code Injection, Loader/'Decrypter'](http://www.pinkstyle.org/elfcrypt.html)