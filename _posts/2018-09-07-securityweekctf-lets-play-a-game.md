---
layout: post
title: "Security Week Graz 2018: Let's Play a Game"
author: exo, yrlf
categories: writeup
tags: [cat/misc, tool/xxd]
---

* **Category:** misc
* **Points:** 50
* **Description:**

> ![i want you](https://ctf.attacking.systems/files/9b3e4bd7368ab13ed691d3b7ba50ab66/game.jpeg)
> This one is simple - just beat the NES game, go to "Extra features" and watch the credits!
>
> [\[nova.nes\]](https://ctf.attacking.systems/files/d32c7fa5e65fe27d56e6c513611b76bc/nova.nes)

## Writeup

We were given a NES ROM file, so we started out by putting it into an emulator (we used RetroArch) and see what it does.
It appears to be a game in which we play a squirrel named "Pwnie" in a classic jump and run style environment.
After clicking around a bit, we found the URL http://novasquirrel.com in the pause menu, which is a link to the original game.
We were then able to download the original ROM file.

Now we were able to compare the two files using `xxd` and `meld`.
`xxd` is a simple Linux program that lets you create hexdumps of files.
`meld` is a graphical tool to compare files.
Because we cannot compare two binary files directly, we first create hexdumps of both and compare the results:

```
$ xxd nova.nes > nova.xxd
$ xxd nova_original.nex > nova_original.xxd
$ meld nova_original.nex nova_original.xxd
```

As it turns out, most of the file was not edited at all.
Both have the same file size.
However, some parts of the binary were modified, like the string constants.
Scrolling though it, we discovered this very interesting part:

```
00035900: 1001 4e6f 7661 2074 6865 2053 7175 6972  ..Nova the Squir
00035910: 7265 6c00 0241 2070 6c61 7466 6f72 6d65  rel..A platforme
00035920: 7220 666f 7220 7468 6520 4e45 5300 0362  r for the NES..b
00035930: 7920 4a6f 7368 2048 6f66 666d 616e 0002  y Josh Hoffman..
00035940: 1159 116f 1375 7220 4612 6c11 1161 6700  .Y.o.ur F.l..ag.
00035950: 0312 7b11 1213 5412 4811 3454 5f11 5713  ..{...T.H.4T_.W.
00035960: 4153 115f 4612 5512 114e 7d00 0143 4f44  AS._F.U..N}..COD
00035970: 4500 0250 7269 6e63 6573 7320 456e 6769  E..Princess Engi
00035980: 6e65 0002 6674 3270 656e 746c 7920 6d75  ne..ft2pently mu
00035990: 7369 6320 746f 6f6c 0003 4a6f 7368 2048  sic tool..Josh H
```

So someone inserted new string constants that say: `Y.o.ur F.l..ag...{...T.H.4T_.W.AS._F.U..N}`.
The dots in the hexdump signify that there is a non-printable character.
It was likeley inserted to prevent us from using simple string search tools such as `strings` and `grep`.

When read without the dots, the flag is `{TH4T_WAS_FUN}`
