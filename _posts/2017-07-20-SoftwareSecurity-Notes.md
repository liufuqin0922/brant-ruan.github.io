---
title: Software Security Notes
category: CS
---

## Coursera | Software Security Notes

### Overview and Preparation

Goals:

- Better design
- Better implementation
- Better assurance

Views:

- Black hat
- White hat

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
- Format string attact
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

Web vulnerabilities and attacks:

- SQL injection
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Session hijacking

Secure Software development:

- Apply coding rules
- Apply automated code review techniques
    + Static analysis and symbolic execution (whitebox fuzz testing)
- Apply penetration testing

Lessons Content:

- Memory attacks
- Memory defenses
- Web security
- Security design/development
- Automated code review
- Penetration testing

### Week 1 | Memory-based Attacks



##### References

- [Common vulnerabilities guide for C programmers](https://security.web.cern.ch/security/recommendations/en/codetools/c.shtml)
- [How to Open a File and Not Get Hacked](http://research.cs.wisc.edu/mist/presentations/kupsch_miller_secse08.pdf)
- [Memory Layout of C Programs](http://www.geeksforgeeks.org/memory-layout-of-c-program/)
- [How security flaws work: The buffer overflow](https://arstechnica.com/security/2015/08/how-security-flaws-work-the-buffer-overflow/)
- [Smashing the Stack for Fun and Profit](http://insecure.org/stf/smashstack.html)
- [Exploiting Format String Vulnerabilities](https://crypto.stanford.edu/cs155/papers/formatstring-1.2.pdf)
- [Basic Integer Overflows](http://phrack.org/issues/60/10.html)