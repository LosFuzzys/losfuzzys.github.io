---
layout: post
title: "Security Week Graz 2018: Printer Update"
author: yrlf, exo
categories: writeup
tags: [cat/forensics, tool/radare2]
---

* **Category:** forensics
* **Points:** 50
* **Description:**

> My new printer has a really convenient method of updating the firmware. I
> wonder if I can emulate the firmware to learn some secrets?
>
> [\[manual.pdf\]](https://ctf.attacking.systems/files/23cc29240cb957a92be04bcb2828c80f/manual.pdf)

## Writeup

I tackled this challenge together with exo on Tuesday, the second day of the
CTF. We had already finished most of the challenges, so I looked at this
challenge, even though I don't usually do forensics challenges often.

This challenge also has a little bit of a twist concerning the category, but
they chose forensics in order to not spoil the challenge.

## The Challenge

We get a `manual.pdf` for a fictional printer called an "Integrator CP-E8M
LaserPhaser" by E-Corp (someone has seen Mr Robot it seems).

Interestingly, the text says we can update the printer by printing this PDF.
I can already imagine something weird must be hidden in the PDF. A firmware
image? An update URL?

## The PDF

PDF files usually start with the magic string "%PDF-1.5" (or whatever version is
used). This magic can however be placed at different locations in the file.

This file has 4 weird bytes before that, but they aren't any of the usual magic
numbers of any format that I know of.

The PDF then contains this:

```
(...4 weird bytes here)
%PDF-1.5
9999 0 obj
<<>>
stream
(...huge blob here)
endstream
endobj
%PDF-1.5
(...rest of pdf)
```

So there is a _second_ PDF header here?
Looking at this, PDF viewers only seem to display the second PDF. The first PDF
only contains that huge blob.

## The Blob

The blob _also_ doesn't have any intersting file magic at the front, but there
are some _very_ telling strings inside:

```
TU Graz
Printer Firmware Update
v1.0.7
[+] Getting device... Done
[+] Found Integrator/CP ARMv7 CPU
[+] Checking kernel integrity... Done
[+] Preparing update
[-] Authentication required!
[ ] Please enter password:
update
[-] Password '%s' is wrong!
[-] Firmware update aborted
[+] Press any key to continue
[+] Password is correct!
[*] Firmware updated to version
       %s
[+] Please restart printer now!
```

_Integrator/CP ARMv7_? "%s"?

This is starting to look a lot like a binary reversing challenge to me.
And sure enough, the blob contains things that look like reasonable ARM
instructions. But where does it start running code from?

At this point I tried opening the whole PDF in radare, and tried to see if the 4
magic header bytes are a valid ARM instruction. (Spoiler alert: they were)

```
[yrlf@tuxic ctf/printer_update]$ r2 -a arm -b 32 manual.pdf
 -- No fix, no sleep
[0x00000000]> pd 1
        ┌─< 0x00000000      070000ea       b 0x24
```

A branch! And interestingly, it jumps right after the "stream" indicator, where
the blob starts. Now we can start reversing the binary

## Reversing the "Firmware Updater"

So, looking at the first few things the binary does, we get this:

```
; PDF file starts here
entry:
    b start

; blob starts here
start:
    mov sp, 0x6000
    bl main

main:
    ; lots of code
```

It sets up a stack pointer and calls main. Main seems to be a quite huge
function, and it calls lots of other functions, so this seems to be the core of
the application. But without knowing what this does it's hard to reverse it.

Since it seems to be a bare-metal ARM Integrator/CP binary, why not run it with
QEMU?

## Emulating with QEMU

Since QEMU supports Integrator/CP, we can just run this:

```
[yrlf@tuxic ctf/printer_update]$ qemu-system-arm -M integratorcp -kernel manual.pdf
```

![qemu screenshot](/images/posts/2018-09-07-securityweekctf-printer-update-qemu.png)

And there it is!

With this out of the way, we now know that the binary must draw to the screen
somewhere, which we will find in the binary as drawing to some framebuffer.
Since the screen is 640x480, we are going to search for some loops or constants
for e.g. clearing the screen first.

And since we saw "%s" in some of the strings, there is probably also
a `printf` somewhere.

## Reversing the first function

``` 
main:
    ; ... snip
    ldr r2, [0x00000720]; [0x720:4]=0x1234c
    sub r3, fp, 0x4c
    mov r1, r2
    mov r2, 0x1b
    mov r0, r3
    bl fcn.000007bc
    ; ... snip
```

This is what the first call looks like. It seems `r0` here is some buffer on the
stack, while `r1` is probably another address, but 0x1234c looks weird. `r2` is
most likely a length, or something else small:

- 0x1234c is still in the PDF, but waaay outside the blob
- 0x234c _is_ inside the blob, and there is also some null-terminated thing
  there, which is exactly 0x1b bytes long.

So, this could mean that our binary is instead loaded at 0x10000. (Further
reversing confirms this). Also, looking at the actual function called, this is
definitely `memcpy`.

## Remapping the binary

Now, on to some radare-fu:

```
[yrlf@tuxic ctf/printer_update]$ r2 --
 -- Feed the bugs!
[0x00000000]> o manual.pdf 0x10000 rwx
3
[0x00000000]> e asm.arch = arm
[0x00000000]> e asm.bits = 32
[0x00000000]> pd 1 @ 0x10000
        ┌─< 0x00010000      070000ea       b 0x10024
```

1. start radare without opening anything
2. map the binary as read/write/execute at address 0x10000
3. set the architecture to arm
4. set the bits to 32 (not thumb mode)
5. print the entry branch to test if it's mapped correctly

Then we do some additional stuff to make radare analyze the binary correctly:

```
[0x00000000]> s 0x1002c
[0x0001002c]> e anal.bb.maxsize = 4096
[0x0001002c]> af
[0x0001002c]> afn main
[0x0001002c]> aaaaaa
[x] Analyze all flags starting with sym. and entry0 (aa)
[ ]
[Value from 0x00010000 to 0x0003789a
aav: 0x00010000-0x0003789a in 0x10000-0x3789a
[x] Analyze function calls (aac)
[x] Analyze len bytes of instructions for references (aar)
[x] Constructing a function name for fcn.* and sym.func.* functions (aan)
[x] Type matching analysis for all functions (afta)
[x] Emulate code to find computed references (aae)
[x] Analyze consecutive function (aat)
```

1. move to the address of main
2. set maximum size of a basic block to 4096 (main has a basic block too large
   for the default)
3. analyze the function
4. name it "main"
5. analyze everything

## Seeing the big picture

With the graph of the main function now analyzed by radare, we can guess what
the binary does now:

1. It sets up some stuff (before the main loop)
2. It probably draws everything on the screen
3. It waits for input (loops and calls the same function until it doesn't return
   NULL)
4. It processes the input and then either loops back to 2 or continues
5. It does some more stuff before hanging itself in an infinite loop

Right before the input loop it calls the same function repeatedly, with a
pointer argument that is different each time.

Checking that address with `px @ address` reveals that this is a string.
(printing the string can also be done with `ps @ address`)

Judging from the strings passed to this function, this is probably printf.

After the input loop, the value from the input function is passed to another
function along with the string "update", and when that function returns 0, we go
into the "password correct" path. Could this be `strcmp`? Yes, it is!

## Getting the flag

Now, we just need to input that string in QEMU:

![qemu screenshot with flag](/images/posts/2018-09-07-securityweekctf-printer-update-qemu-flag.png)

## Retrospective

During the CTF the solution to this was not quite as straight-forward as this.
We got sidetracked a lot and reversed a lot of functions internally before we
found out what they were, and we also got confused by either disassembling as
thumb when we shouldn't, or trying to interpret the data at the wrong address
(before we found out the binary was mapped at 0x10000).

In the end it was a really fun reversing challenge!
