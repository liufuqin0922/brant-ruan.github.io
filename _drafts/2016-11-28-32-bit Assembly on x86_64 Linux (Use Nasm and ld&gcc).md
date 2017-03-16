### Assembly on x86_64 Linux

---

Some instructions in Intel assembly set are invalid in x86_64 env.

**e.g.**

```
aaa
push eax
```

and so on.

---

### Solutions

- Use 64-bit instructions instead.(You can refer to Intel developer manual)

- Add 32-bit options:

For nasm:   

```
nasm -f elf32 xxx.asm
```

For ld:

```
ld -o xxx -m elf_i386 xxx.o
```

---

**If you want to use gcc for linking (do what the author of *Assembly Language Step by Step* does), you will meet some new troubles.**

### Solutions

- Use 64-bit instructions instead and:

```
nasm -f elf64 xxx.asm
gcc -o xxx xxx.o -nostartfiles
```

- Use 32-bit libraries:

```
dpkg --print-architecture  # to ensure your 64-bit kernel
dpkg --print-foreign-architectures # To ensure you have turned on function for support of multi-architecture. 
# And if the output is "i386", it is OK. Or you'd better follow:
# sudo dpkg --add-architecture i386
# sudo apt-get update
# sudo apt-get dist-upgrade
# Then:
sudo apt-get install gcc-multilib g++-multilib
# Bingo !
# Now you can use instructions below to continue your progress:
nasm -f elf xxx.asm
gcc -o xxx xxx.o -m32
(if using GDB) nasm -f elf -g -F stabs xxx.asm
```

### For more details, please refer to "man gcc"