今日读缓冲区溢出文章时发现了这个好东西：

> https://github.com/0vercl0k/rp

可以在二进制程序中自动搜索用于 ROP 链构造的 gadgets 。目前支持 Intel 32 & 64 ，工具支持 Windows/Linux/Mac OS 平台的程序。它的方便之处在于你可以在任一个平台上使用它。具体地，我可以在 Windows 下使用这个来分析一个 ELF 格式的程序，而不必打开一个 Linux 系统。这为跨平台 Exploit 提供了很大方便。

在 Windows 上分析一个 ELF-64 的 CTF pwn 示例：

```
./rp++ -f E:\ctf\pwn-1\guess -r 4
```

输出：

```
Trying to open 'e:\ctf\pwn-1\guess'..
Loading ELF information..
FileFormat: Elf, Arch: Ia64
Using the Nasm syntax..

Wait a few seconds, rp++ is looking for gadgets..
in PHDR
0 found.

in LOAD
98 found.

A total of 98 gadgets found.
0x00400993: adc al, 0x55 ; mov edi, 0x00601E20 ; mov rbp, rsp ; call rax ;  (1 found)
0x00400c6f: add bl, dh ; ret  ;  (1 found)
0x00400948: add byte [rax-0x7B], cl ; sal byte [rsp+rsi*8+0x5D], cl ; mov rsi, rax ; mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400c6d: add byte [rax], al ; add bl, dh ; ret  ;  (1 found)
0x00400c6b: add byte [rax], al ; add byte [rax], al ; add bl, dh ; ret  ;  (1 found)
0x00400bf1: add byte [rax], al ; add byte [rax], al ; leave  ; ret  ;  (1 found)
0x00400c6c: add byte [rax], al ; add byte [rax], al ; rep ret  ;  (1 found)
0x00400c3d: add byte [rax], al ; add byte [rcx+rcx*4-0x16], cl ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400bf2: add byte [rax], al ; add cl, cl ; ret  ;  (1 found)
0x004007a3: add byte [rax], al ; add rsp, 0x08 ; ret  ;  (1 found)
0x00400bf3: add byte [rax], al ; leave  ; ret  ;  (1 found)
0x00400c3e: add byte [rax], al ; mov rdx, r13 ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400c6e: add byte [rax], al ; rep ret  ;  (1 found)
0x00400c72: add byte [rax], al ; sub rsp, 0x08 ; add rsp, 0x08 ; ret  ;  (1 found)
0x00400c3f: add byte [rcx+rcx*4-0x16], cl ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400978: add byte [rcx], al ; rep ret  ;  (1 found)
0x00400bf4: add cl, cl ; ret  ;  (1 found)
0x00400974: add eax, 0x0020178E ; add ebx, esi ; ret  ;  (1 found)
0x00400979: add ebx, esi ; ret  ;  (1 found)
0x004007a6: add esp, 0x08 ; ret  ;  (1 found)
0x00400c79: add esp, 0x08 ; ret  ;  (1 found)
0x004007a5: add rsp, 0x08 ; ret  ;  (1 found)
0x00400c78: add rsp, 0x08 ; ret  ;  (1 found)
0x00400914: and byte [rax+0x00], ah ; jmp rax ;  (1 found)
0x00400954: and byte [rax+0x00], ah ; jmp rdx ;  (1 found)
0x00400977: and byte [rax], al ; add ebx, esi ; ret  ;  (1 found)
0x00400c49: call qword [r12+rbx*8] ;  (1 found)
0x00400e83: call qword [rax] ;  (1 found)
0x004009ac: call qword [rbp+0x48] ;  (1 found)
0x00400c4a: call qword [rsp+rbx*8] ;  (1 found)
0x0040099d: call rax ;  (1 found)
0x00400e17: call rax ;  (1 found)
0x00400a12: dec dword [rax-0x77] ; retn 0x8D48 ;  (1 found)
0x00400a46: dec ecx ; ret  ;  (1 found)
0x00400c4c: fmul qword [rax-0x7D] ; ret  ;  (1 found)
0x00400910: hlt  ; pop rbp ; mov edi, 0x006020E8 ; jmp rax ;  (1 found)
0x0040094d: hlt  ; pop rbp ; mov rsi, rax ; mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400eeb: jmp qword [rbp+0x00] ;  (1 found)
0x00400917: jmp rax ;  (1 found)
0x00400957: jmp rdx ;  (1 found)
0x00400a47: leave  ; ret  ;  (1 found)
0x00400bf5: leave  ; ret  ;  (1 found)
0x00400973: mov byte [0x0000000000602108], 0x00000001 ; rep ret  ;  (1 found)
0x00400bf0: mov eax, 0x00000000 ; leave  ; ret  ;  (1 found)
0x00400bec: mov ebp, 0xB8FFFFFD ; add byte [rax], al ; add byte [rax], al ; leave  ; ret  ;  (1 found)
0x0040099b: mov ebp, esp ; call rax ;  (1 found)
0x004007a1: mov ebx, 0x48000000 ; add esp, 0x08 ; ret  ;  (1 found)
0x00400995: mov edi, 0x00601E20 ; mov rbp, rsp ; call rax ;  (1 found)
0x00400912: mov edi, 0x006020E8 ; jmp rax ;  (1 found)
0x00400952: mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400c47: mov edi, edi ; call qword [r12+rbx*8] ;  (1 found)
0x00400c46: mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400c41: mov edx, ebp ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400950: mov esi, eax ; mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400c44: mov esi, esi ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x0040099a: mov rbp, rsp ; call rax ;  (1 found)
0x00400c40: mov rdx, r13 ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400c43: mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x0040094f: mov rsi, rax ; mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400975: mov ss, word [rdi] ; and byte [rax], al ; add ebx, esi ; ret  ;  (1 found)
0x00400c38: nop dword [rax+rax+0x00000000] ; mov rdx, r13 ; mov rsi, r14 ; mov edi, r15d ; call qword [r12+rbx*8] ;  (1 found)
0x00400c67: nop dword [rax+rax+0x00000000] ; rep ret  ;  (1 found)
0x00400c68: nop dword [rax+rax+0x00000000] ; rep ret  ;  (1 found)
0x00400c65: nop word [rax+rax+0x00000000] ; rep ret  ;  (1 found)
0x00400c66: nop word [rax+rax+0x00000000] ; rep ret  ;  (1 found)
0x00400c5c: pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret  ;  (1 found)
0x00400c5e: pop r13 ; pop r14 ; pop r15 ; ret  ;  (1 found)
0x00400c60: pop r14 ; pop r15 ; ret  ;  (1 found)
0x00400c62: pop r15 ; ret  ;  (1 found)
0x00400972: pop rbp ; mov byte [0x0000000000602108], 0x00000001 ; rep ret  ;  (1 found)
0x00400911: pop rbp ; mov edi, 0x006020E8 ; jmp rax ;  (1 found)
0x0040094e: pop rbp ; mov rsi, rax ; mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400c5f: pop rbp ; pop r14 ; pop r15 ; ret  ;  (1 found)
0x00400905: pop rbp ; ret  ;  (1 found)
0x00400942: pop rbp ; ret  ;  (1 found)
0x00400c63: pop rdi ; ret  ;  (1 found)
0x00400c61: pop rsi ; pop r15 ; ret  ;  (1 found)
0x00400c5d: pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret  ;  (1 found)
0x00400994: push rbp ; mov edi, 0x00601E20 ; mov rbp, rsp ; call rax ;  (1 found)
0x0040097a: rep ret  ;  (1 found)
0x00400c70: rep ret  ;  (1 found)
0x004007a9: ret  ;  (1 found)
0x00400906: ret  ;  (1 found)
0x00400943: ret  ;  (1 found)
0x0040097b: ret  ;  (1 found)
0x00400a48: ret  ;  (1 found)
0x00400bf6: ret  ;  (1 found)
0x00400c4f: ret  ;  (1 found)
0x00400c64: ret  ;  (1 found)
0x00400c71: ret  ;  (1 found)
0x00400c7c: ret  ;  (1 found)
0x00400a15: retn 0x8D48 ;  (1 found)
0x00400935: retn 0xC148 ;  (1 found)
0x0040094b: sal byte [rsp+rsi*8+0x5D], cl ; mov rsi, rax ; mov edi, 0x006020E8 ; jmp rdx ;  (1 found)
0x00400c75: sub esp, 0x08 ; add rsp, 0x08 ; ret  ;  (1 found)
0x00400c74: sub rsp, 0x08 ; add rsp, 0x08 ; ret  ;  (1 found)
0x00400c6a: test byte [rax], al ; add byte [rax], al ; add byte [rax], al ; rep ret  ;  (1 found)
0x00400c45: test byte [rcx+rcx*4-0x01], 0x00000041 ; call qword [rsp+rbx*8] ;  (1 found)
```

很方便。这个工具很小很有用，可以考虑看一下它的源码。

