---
layout: post
title: "CSAW’18 CTF Qualification Round: Tour of x86"
author: yrlf
categories: writeup
tags: [cat/reversing, tool/radare2, tool/pwntools]
---

* **Category:** reversing
* **Points:** 50, 100, 200
* **Description:**

> ## Part 1:
>
> Newbs only!
>
> ```sh
> nc rev.chal.csaw.io 9003
> ```
>
> -Elyk
>
> [stage-1.asm](https://ctf.csaw.io/files/02721fabb0c817ff88eecba00c8af128/stage-1.asm)
> [Makefile](https://ctf.csaw.io/files/dc249873b66ed653d7db4572ce6ef07a/Makefile)
> [stage-2.bin](https://ctf.csaw.io/files/5e0f7fb0d9229a7f878bc388e9fe1b4f/stage-2.bin)
> 
> ## Part 2:
>
> Open stage2 in a disassembler, and figure out how to jump to the rest of the
> code!
>
> -Elyk
>
> [stage-1.asm](https://ctf.csaw.io/files/02721fabb0c817ff88eecba00c8af128/stage-1.asm)
> [Makefile](https://ctf.csaw.io/files/dc249873b66ed653d7db4572ce6ef07a/Makefile)
> [stage-2.bin](https://ctf.csaw.io/files/5e0f7fb0d9229a7f878bc388e9fe1b4f/stage-2.bin)
>
> ## Part 3:
>
> The final boss!
>
> Time to pull together your knowledge of Bash, Python, and stupidly-low-level
> assembly!!
> 
> This time you have to write some assembly that we're going to run.. You'll see
> the output of your code through VNC for 60 seconds.
> 
> Objective: Print the flag.
> 
> What to know:
> 
> Strings need to be alternating between the character you want to print and
> '0x1f'.
> 
> To print a string you need to write those alternating bytes to the frame
> buffer (starting at 0x00b8000...just do it). Increment your pointer to move
> through this buffer.
> 
> If you're having difficulty figuring out where the flag is stored in memory,
> this code snippet might help you out:
>
> ```
> get_ip:
>   call next_line
> next_line:
>   pop rax
>   ret
> ```
>
> That'll put the address of pop rax into rax.
>
> Call serves as an alias for push rip (the instruction pointer - where we are
> in code) followed by `jmp ______` where whatever is next to the call fills in
> the blank.
>
> And in case this comes up, you shouldn't need to know where you are loaded in
> memory if you use that above snippet...
>
> Happy Reversing!!
>
> ```sh
> nc rev.chal.csaw.io 9004
> ```
>
> -Elyk
>
> [Makefile](https://ctf.csaw.io/files/b236e0cc11cba5b5fd134436a0c8c811/Makefile)
> [part-3-server.py](https://ctf.csaw.io/files/d3e7a84ffb4eeca992c9f458bf4c11ec/part-3-server.py)
> [tacOS-base.bin](https://ctf.csaw.io/files/acbf4fe9f0233ce3ed34c55fee34649e/tacOS-base.bin)

## Writeup

This is a challenge in multiple stages, each one having its own flag.

The general theme is low-level x86 code and how it behaves after boot.
The difficulty is quite low, but it was fun.

### Stage 1

In the first stage we have the assembly source code available, but it is heavily
commented. (This actually makes the code LESS readable at times)
The code is running in 16-bit real-mode, with BIOS interrupts available.

When connecting to the provided address and port, we are asked a series of
questions about the values of registers in different parts of the program.

#### What is the value of `dh` after line 129 executes? (one byte)

Line 129 is `xor dh, dh`, which always leaves `dh` as 0x00.

#### What is the value of `gs` after line 145 executes? (one byte)

Line 145 is `mov gs, dx`. `dx` is compared to 0 on line 134, so `gx` must always
be 0x00.

#### What is the value of `si` after line 151 executes? (two bytes)

Line 151 is `mov si, sp`. `sp` is set on line 149 with `mov sp, cx`. `cx` is set
to 0 on line 107, so `si` must always be 0x0000

#### What is the value of ax after line 169 executes? (two bytes)

Line 168 and 169 are `mov al, 't'` and `mov ah, 0x0e`. The hex-value of 't' is
0x74, so the value is 0x0e74.

#### What is the value of ax after line 199 executes for the first time? (two bytes)

Lines 197 and 199 are `mov al, [si]` and `mov ah, 0x0e`, which are part of a
loop.

`si` is initialized as a pointer to the string `"acOS\n\r  by Elyk"`, so
the first iteration should leave `ax` with 0x0e61 (hex-value of 'a' is 0x61).

After answering all the questions, we get the flag:

```
flag{rev_up_y0ur_3ng1nes_reeeeeeeeeeeeecruit5!}
```

### Stage 2

The Stage 2 binary is loaded by Stage 1 on line 230, using BIOS interrupt 0x13.

Near the end of the Stage 1 binary, the used DAP (disk address packet) is
stored. The address to copy to is LOAD_ADDR, defined to be 0x6000 on line 52.

After executing all of the demonstration code in Stage 1, the code jumps to
LOAD_ADDR on line 384.

Opening the stage 2 binary in radare can be done as follows:

```
[yrlf@tuxic ctf/tour-of-x86]$ r2 --
 -- Don’t feed the bugs! (except delicious stacktraces)!
[0x00000000]> o ./stage-2.bin 0x6000 rwx
3
[0x00000000]> e asm.arch = x86
[0x00000000]> e asm.bits = 16
[0000:0000]> s 0x6000
[0000:6000]> pd 61
            0000:6000      f4             hlt
            0000:6001      e492           in al, 0x92
            0000:6003      0c02           or al, 2
            0000:6005      e692           out 0x92, al
            0000:6007      31c0           xor ax, ax
            0000:6009      8ed0           mov ss, ax
            0000:600b      bc0160         mov sp, 0x6001
            0000:600e      8ed8           mov ds, ax
            0000:6010      8ec0           mov es, ax
            0000:6012      8ee0           mov fs, ax
            0000:6014      8ee8           mov gs, ax
            0000:6016      fc             cld
            0000:6017      66bf00000000   mov edi, 0
        ┌─< 0000:601d      eb07           jmp 0x6026
        │   0000:601f      90             nop
        │   0000:6020      0000           add byte [bx + si], al
        │   0000:6022      0000           add byte [bx + si], al
        │   0000:6024      0000           add byte [bx + si], al
        └─> 0000:6026      57             push di
            0000:6027      66b900100000   mov ecx, 0x1000
            0000:602d      6631c0         xor eax, eax
            0000:6030      fc             cld
            0000:6031      f366ab         rep stosd dword es:[di], eax
            0000:6034      5f             pop di
            0000:6035      26668d850010   lea eax, dword es:[di + 0x1000]
            0000:603b      6683c803       or eax, 3
            0000:603f      26668905       mov dword es:[di], eax
            0000:6043      26668d850020   lea eax, dword es:[di + 0x2000]
            0000:6049      6683c803       or eax, 3
            0000:604d      266689850010   mov dword es:[di + 0x1000], eax ; [0x1000:4]=-1
            0000:6053      26668d850030   lea eax, dword es:[di + 0x3000]
            0000:6059      6683c803       or eax, 3
            0000:605d      266689850020   mov dword es:[di + 0x2000], eax ; [0x2000:4]=-1
            0000:6063      57             push di
            0000:6064      8dbd0030       lea di, word [di + 0x3000]
            0000:6068      66b803000000   mov eax, 3
        ┌─> 0000:606e      26668905       mov dword es:[di], eax
        ╎   0000:6072      660500100000   add eax, 0x1000
        ╎   0000:6078      83c708         add di, 8
        ╎   0000:607b      663d00002000   cmp eax, 0x200000
        └─< 0000:6081      72eb           jb 0x606e
            0000:6083      5f             pop di
            0000:6084      b0ff           mov al, 0xff                 ; 255
            0000:6086      e6a1           out 0xa1, al
            0000:6088      e621           out 0x21, al                 ; '!'
            0000:608a      90             nop
            0000:608b      90             nop
            0000:608c      0f011e2060     lidt [0x6020]
            0000:6091      66b8a0000000   mov eax, 0xa0                ; 160
            0000:6097      0f22e0         mov cr4, eax
            0000:609a      6689fa         mov edx, edi
            0000:609d      0f22da         mov cr3, edx
            0000:60a0      66b9800000c0   mov ecx, 0xc0000080
            0000:60a6      0f32           rdmsr
            0000:60a8      660d00010000   or eax, 0x100
            0000:60ae      0f30           wrmsr
            0000:60b0      0f20c3         mov ebx, cr0
            0000:60b3      6681cb010000.  or ebx, 0x80000001
            0000:60ba      0f22c3         mov cr0, ebx
            0000:60bd      0f0116e260     lgdt [0x60e2]
        ┌─< 0000:60c2      ea58610800     ljmp 8:0x6158
```

Interestingly, the code starts with a `hlt` instruction, stopping the rest of
the code from being executed.

There are two ways to solve this:

- patch the `hlt` instruction into a `nop` (0x90)
- jump to `LOAD_ADDR+1` in Stage 1

When running the binary now via `make run`, Stage 1 executes, and actually
executes Stage 2. The flag can be seen on a blue background, but only for a
fraction of a second before QEMU reboots.

Analyzing the code in Stage 2, this seems to be very compact code to switch
directly from 16-bit real-mode to 64-bit long-mode. Afterwards, the code jumps
to address 0x6158.

Disassembling that code can be easily done in radare2:

```
[0000:6000]> s 0x6158
[0000:6158]> e asm.bits = 64
[0x00006158]> pd 37
            0x00006158      66b81000       mov ax, 0x10                ; 16
            0x0000615c      8ed8           mov ds, eax
            0x0000615e      8ec0           mov es, eax
            0x00006160      8ee0           mov fs, eax
            0x00006162      8ee8           mov gs, eax
            0x00006164      8ed0           mov ss, eax
            0x00006166      bf00800b00     mov edi, 0xb8000
            0x0000616b      b9f4010000     mov ecx, 0x1f4              ; 500
            0x00006170      48b8201f201f.  movabs rax, 0x1f201f201f201f20
            0x0000617a      f348ab         rep stosq qword [rdi], rax
            0x0000617d      bf00800b00     mov edi, 0xb8000
            0x00006182      4831c0         xor rax, rax
            0x00006185      4831db         xor rbx, rbx
            0x00006188      4831c9         xor rcx, rcx
            0x0000618b      4831d2         xor rdx, rdx
            0x0000618e      b245           mov dl, 0x45                ; 'E' ; 69
            0x00006190      80ca6c         or dl, 0x6c                 ; 'l'
            0x00006193      b679           mov dh, 0x79                ; 'y' ; 121
            0x00006195      80ce6b         or dh, 0x6b                 ; 'k'
            0x00006198      20f2           and dl, dh
            0x0000619a      b600           mov dh, 0
            0x0000619c      48bee8600000.  movabs rsi, 0x60e8
        ┌─> 0x000061a6      48833c0600     cmp qword [rsi + rax], 0
       ┌──< 0x000061ab      7427           je 0x61d4
       │╎   0x000061ad      b904000000     mov ecx, 4
      ┌───> 0x000061b2      8a1c06         mov bl, byte [rsi + rax]
      ╎│╎   0x000061b5      30d3           xor bl, dl
      ╎│╎   0x000061b7      d0eb           shr bl, 1
      ╎│╎   0x000061b9      881c06         mov byte [rsi + rax], bl
      ╎│╎   0x000061bc      4883c002       add rax, 2
      └───< 0x000061c0      e2f0           loop 0x61b2
       │╎   0x000061c2      4883e808       sub rax, 8
       │╎   0x000061c6      488b0c06       mov rcx, qword [rsi + rax]
       │╎   0x000061ca      48890c07       mov qword [rdi + rax], rcx
       │╎   0x000061ce      4883c008       add rax, 8
       │└─< 0x000061d2      ebd2           jmp 0x61a6
       └──> 0x000061d4      ebd2           invalid
```

This seems to decrypt and print the flag on the framebuffer at 0xb8000 before
running into an invalid instruction at address 0x61d4. Patching this with an
infinite loop (bytes eb fe) should leave the flag on-screen for longer.

Looking at the file-size of the Stage 2 binary, we just need to append the new
bytes.

```
[yrlf@tuxic ctf/tour-of-x86]$ echo -n $'\xeb\xfe' >> stage-2.bin
```

This gives us the flag:

![qemu stage 2 flag](/images/posts/2018-09-20-csawctfquals-tour-of-x86-stage2.png)

The other way of getting the flag is to manually decrypt the flag character
buffer with the XOR key generated from the string 'Elyk' (the key is 0x69):

```py
import binascii

enc = binascii.unhexlify("a5b1aba79f09b5a3d78fb3010b0bd7fdf3c9d7a5b78dd7991905d7b7b50fd7b3018f8f0b85a3d70ba3ab89d701d7db09c393")
print("".join(chr((b ^ 0x69) >> 1) for b in enc))
```

### Stage 3

For Stage 3 we get a host and port again, this time we can send them a
hex-encoded binary that gets appended to the Stage 2 payload to be executed
after the flag is rendered, we then get a port on which we can observe the
binary over VNC.

The flag seems to be appended after our code, so I just wrote some asm that
hexdumps the bytes of our binary and everything after that in an infinite loop:

```as
    call next
next:
    pop rbp

    mov edi, 0xb8000

loop:
    mov rsi, byte [rbp]
    inc rbp
    call draw_byte
    jmp loop

draw_byte:
    /* rdi: framebuffer */
    /* rsi: byte */
    /* == CLOBBERS == */
    /* rsi, rbx, rax */

    mov rbx, rsi

    shr rsi, 4
    call draw_nibble

    mov rsi, rbx
    call draw_nibble

    ret

draw_nibble:
    /* rdi: framebuffer */
    /* rsi: nibble */
    /* == CLOBBERS == */
    /* rax */

    mov rax, rsi
    and al, 0x0f
    cmp al, 0x09
    ja is_char

is_digit:
    add al, 0x30
    jmp output

is_char:
    add al, 0x41 - 0x0a

output:
    mov ah, 0x1f

    mov word [rdi], ax
    add rdi, 2
    
    ret
```

Sending this to the port and connecting via VNC reveals this:

![qemu stage 3 flag](/images/posts/2018-09-20-csawctfquals-tour-of-x86-stage3.png)

Writing this down and decoding this with this:

```py
import binascii

print(binascii.unhexlify(
    "666c61677b53346c31795f53653131535f7461634f5368656c6c5f633064335f62595f7448655f5365345f53683072657d"
).decode())
```

yields the flag:

```
flag{S4l1y_Se11S_tacOShell_c0d3_bY_tHe_Se4_Sh0re}
```
