---
category: Sec
title: GNU Screen 4.5.0 - Privilege Escalation
---

## GNU Screen 4.5.0 - Privilege Escalation

### Introduction

Refer to `man screen` to learn `screen` as it is a useful tool. Here we just talk about the vulnerability below.

This PRIVILEGE-ESCALATION only makes sense within v4.5.0((Screen version 4.05.00 (GNU) 10-Dec-16)).

Firstly I am not sure about the power of this exploit in that if you can log in as a common user, and `screen` is `SUID`, then you can just `sudo screen` to open a new root shell. If you come across a situation where you DO NOT know the current user's password, this exploit makes sense.

### Vulnerability

### Exp&PoC

### References

- [XiphosResearch/exploits](https://github.com/XiphosResearch/exploits/tree/master/screen2root)
- [GNU Screen 4.5.0 - Privilege Escalation](https://www.exploit-db.com/exploits/41154/)
- [GNU Screen 4.5.0 - Privilege Escalation (PoC)](https://www.exploit-db.com/exploits/41152/)