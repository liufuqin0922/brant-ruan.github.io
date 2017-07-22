---
title: Coursera | Software Security Notes
category: CS
---

## Coursera | Software Security Notes

### Overview and Preparation

Low-level Vulnerabilities:

- Programs written in C and C++
    - Buffer Overflows
        + On the stack
        + On the heap
        + Due to integer overflow
        + Over-writing and over-reading
    - Format string mismatches
    - Dangling pointer dereferences

So, Attacks:

- Stack smashing
- Format string attack
- Stale memory access
- Return-oriented programming (ROP)

Ensuring Memory Safety:

- Use a memory-safe programming language
- For C/C++, use automated defenses
    + Stack canaries
    + Non-executable data (W+X or DEP)
    + Address space layout randomization (ASLR)
    + Memory-safety enforcement (e.g. SoftBound)
    + Control-flow Integrity (CFI)

Secure Software development:

- Apply coding rules
- Apply automated code review techniques
    + Static analysis and symbolic execution (whitebox fuzz testing)
- Apply penetration testing

**Notes come from both videos and my learning from websites in references. And reference marked with √ is the one I have read and learnt.**

### Week 1 | Memory-based Attacks

> Analyzing security requires a whole-systems view.

##### Memory Layout

0x00000000 ~ 0xffffffff

Image from the lesson:

![]({{ site.url }}/resources/pictures/SoftwareSecurityNotes-0.jpg)

##### Buffer Overflows

```c
void func(char *arg1)
{
    char buffer[4];
    strcpy(buffer, arg1);
    ...
}
int main()
{
    char *mystr = "AuthMe!";
    func(mystr);
    ...
}
```

##### Code Injection

- Load code into memory
    + it can not contain any all-zero bytes
    + can not use loader (must self-contained)
    + goal: general-purpose shell
    + code to launch a shell is called shellcode

```c
#include <stdio.h>

int main()
{
    char *name[2];
    name[0] = "/bin/sh";
    name[1] = NULL;
    execve(name[0], name, NULL);
}
```

```asm
xor eax, eax
push eax
push 0x68732f2f
push 0x6e69622f
mov ebx, esp
push ebx
...
```

- Getting injected code to run
    + Overwrite eip

- Finding the return address
    + Without address randomization
        * Stack always starts from the same fixed address
        * Stack will grow, but usually does not grow very deeply
        * Improving chances: nop sleds

![]({{ site.url }}/resources/pictures/SoftwareSecurityNotes-1.jpg)

##### Other Memory Exploits

The code injection attack we have just considered is call **stack smashing** attack.

Now let's see some other types of attack:

###### Heap Overflow

```c
typedef struct _vulnerable_struct{
    char buff[MAX_LEN];
    int (*cmp)(char *, char *);
} vulnerable;

int foo(vulnerable *s, char *one, char *two)
{
    strcpy(s->buff, one);
    strcat(s->buff, two);
    return s->cmp(s->buff, "file://foobar");
}
```

Variants:

- Overflow into C++ object vtable
    + C++ objects are represented using a vtable, containing pointers to the objects's methods
    + vtable is analogous to s->cmp in the previous example
- Overflow into adjacent objects
- Overflow heap metadata
    + Hidden header just before the pointer returned by malloc
    + Flow into that header to corrupt the heap itself

###### Integer Overflow

```c
void vulnerable()
{
    char *response;
    int nresp = packet_get_int();
    if(nresp > 0){
        response = malloc(nresp * sizeof(char *));
        for(i = 0; i < nresp; i++)
            response[i] = packet_get_string(NULL);
    }
}
```

If we set `nresp` to `1073741824` and `sizeof(char *)` is `4`, then `nresp * sizeof(char *)` overflows to become 0 

###### Read Overflow

```c
int main()
{
    char buf[100], *p;
    int i, len;
    while(1){
        // input an integer as length
        p = fgets(buf, sizeof(buf), stdin);
        if(p == NULL)
            return 0;
        len = atoi(p);
        // input message
        p = fgets(buf, sizeof(buf), stdin);
        if(p == NULL)
            return 0;
        // echo message
        for(i = 0; i < len; i++){
            if(!iscntrl(buf[i]))
                putchar(buf[i]);
            else
                putchar('.');
        }
        printf("\n");
    }
}
```

If `len > sizeof(buf)` then read overflow occurs.

Heartbleed is just a read overflow.

###### Stale Memory

A dangling pointer bug occurs when a pointer is freed, but the program continues to use it.

An attacker can arrange for the freed memory to be reallocated and under his control.

When dangling pointer is dereferenced, it will access attacker-controlled data

```c
struct foo{
    int (*cmp)(char *, char *);
};

struct foo *p = malloc(...);
free(p);

... // time goes by

q = malloc(...); // reuses memory

*q = 0xdeadbeef; // if attacker controls

...

p->cmp("hello", "hello"); // reuses dangling ptr
```

##### Format String Vulnerabilities

```c
void vulnerable()
{
    char buf[80];
    if(fgets(buf, sizeof(buf), stdin) == NULL)
       return;
    printf(buf); 
}
```

- printf("%d"); // four bytes above stored eip
- printf("%s");
- print("100%no way!"); // writes `3` to address pointed to by stack entry

##### Project 1

Tasks are easy. But the `runbin.sh` is useful even when you do actual exploits, which allows you inputing hex value directly:

```sh
#!/bin/bash

while read -r line; do echo -e $line; done | ./wisdom-alt
```

##### Open File Safely

Opening safely should be simple, but is not.

Strategies for safe open:

- Verify path is trusted
    + Do not use if not trusted
- Safely open an untrusted file
    + Prevents common security problems with
        * symbolic links
        * misuse of API leading to weak permissions
    + Detect attacks of the path

###### Untrusted File



###### Symbolic Link Attack

Checking whether a files exists or not before creating it is good, but cracker may create a file between your check and the moment you actually use the file (race condition).

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define MY_TMP_FILE "/tmp/file.tmp"

int main(int argc, char **argv)
{
    FILE *f;
    if(!access(MY_TMP_FILE, F_OK)){
        printf("File exists!\n");
        return EXIT_FAILURE;
    }
    /* At this point the attacker creates a symlink 
       from /tmp/file.tmp to /etc/passwd
     */
    tmpFile = fopen(MY_TMP_FILE, "w");
    if(tmpFile == NULL){
        return EXIT_FAILURE;
    }
    fputs("Some text...\n", tmpFile);
    fclose(tmpFile);
    // now you overwrite /etc/passwd
    return EXIT_SUCCESS;
}
``` 

Mitigation:

```c
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
 
#define MY_TMP_FILE "/tmp/file.tmp"
 
enum { FILE_MODE = 0600 };
 
int main(int argc, char* argv[])
{
    int fd;
    FILE* f;
 
    /* Remove possible symlinks */
    unlink(MY_TMP_FILE);
    /* Open, but fail if someone raced us and restored the symlink (secure version of fopen(path, "w") */
    fd = open(MY_TMP_FILE, O_WRONLY|O_CREAT|O_EXCL, FILE_MODE);
    if (fd == -1) {
        perror("Failed to open the file");
        return EXIT_FAILURE;
    }
    /* Get a FILE*, as they are easier and more efficient than plan file descriptors */
    f = fdopen(fd, "w");
    if (f == NULL) {
        perror("Failed to associate file descriptor with a stream");
        return EXIT_FAILURE;
    }
    fprintf(f, "Hello, world\n");
    fclose(f);
    /* fd is already closed by fclose()!!! */
    return EXIT_SUCCESS;
}
```

##### References

- [Common vulnerabilities guide for C programmers √](https://security.web.cern.ch/security/recommendations/en/codetools/c.shtml)
- [How to Open a File and Not Get Hacked √](http://research.cs.wisc.edu/mist/presentations/kupsch_miller_secse08.pdf)
- [Memory Layout of C Programs](http://www.geeksforgeeks.org/memory-layout-of-c-program/)
- [How security flaws work: The buffer overflow](https://arstechnica.com/security/2015/08/how-security-flaws-work-the-buffer-overflow/)
- [Smashing the Stack for Fun and Profit](http://insecure.org/stf/smashstack.html)
- [Exploiting Format String Vulnerabilities](https://crypto.stanford.edu/cs155/papers/formatstring-1.2.pdf)
- [Basic Integer Overflows](http://phrack.org/issues/60/10.html)

### Week 2 | Defenses Against Low-level Attacks

##### References

- [What is memory safety?](http://www.pl-enthusiast.net/2014/07/21/memory-safety/)
- [What is type safety?](www.pl-enthusiast.net/2014/08/05/type-safety/)
- [On the Effectiveness of Address-Space Randomization](http://cseweb.ucsd.edu/~hovav/papers/sppgmb04.html)
- [Smashing the Stack in 2011](https://paulmakowski.wordpress.com/2011/01/25/smashing-the-stack-in-2011/)
- [Low-Level Software Security by Example](https://courses.cs.washington.edu/courses/cse484/14au/reading/low-level-security-by-example.pdf)
- [Geometry of Innocent Flesh on the Bone: Return to libc without Function Calls (on the x86)](https://cseweb.ucsd.edu/~hovav/dist/geometry.pdf)
- [Exploit Hardening Made Easy](https://www.usenix.org/legacy/event/sec11/tech/full_papers/Schwartz.pdf)
- [Blind ROP](http://www.scs.stanford.edu/brop/)
- [Control-Flow Integrity](https://www.microsoft.com/en-us/research/publication/control-flow-integrity/?from=http%3A%2F%2Fresearch.microsoft.com%2Fpubs%2F64250%2Fccs05.pdf#)
- [Enforcing Forward-Edge Control Flow Integrity](https://www.usenix.org/conference/usenixsecurity14/technical-sessions/presentation/tice)
- [MoCFI](www.cse.lehigh.edu/~gtan/paper/mcfi.pdf)
- [Secure Programming HOWTO](https://www.dwheeler.com/secure-programs/Secure-Programs-HOWTO/internals.html)
- [Robust Programming](http://nob.cs.ucdavis.edu/bishop/secprog/robust.html)
- [CERT C coding standard](https://www.securecoding.cert.org/confluence/display/c/SEI+CERT+C+Coding+Standard)
- [DieHard project](http://plasma.cs.umass.edu/emery/diehard.html)