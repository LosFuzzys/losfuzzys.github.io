---
layout: post
title: "Security Week Graz 2018: Encrypted Blob"
author: exo, dux
categories: writeup
tags: [cat/crypto]
---

* **Category:** crypto
* **Points:** 50
* **Description:**

> While updating my new IoT device, I sniffed this encrypted blob from the
> unsecured network communication. Maybe it contains something interesting.
>
> [\[blob\]](https://ctf.attacking.systems/files/73ba17893ccfb9403d64fecca333f283/blob)

## Writeup

We get an encrypted "firmware" image.
Our first approach is using `strings` to see if there are any readable strings in the file:

```
$ strings blob
< ... omitted ... >
y`bF6
Y.M=~*
{d2u
y`bF6
Y.M=~*
{d2u
y`bF6
Y.M=~*
{d2u
y`bF6
Y.M=~*
{d2u
```

We did not find anything readable but there seems to be a lot of repetition in the file.
Using `xxd` we see:

```
$ xxd blob
007ff6b0: 3ae4 b447 0c59 2e4d 3d7e 2acd d735 ec4f  :..G.Y.M=~*..5.O
< ... omitted ... >
007ff8b0: 3ae4 b447 0c59 2e4d 3d7e 2acd d735 ec4f  :..G.Y.M=~*..5.O
< ... omitted ... >
007ffab0: 3ae4 b447 0c59 2e4d 3d7e 2acd d735 ec4f  :..G.Y.M=~*..5.O
< ... omitted ... >
007ffcb0: 3ae4 b447 0c59 2e4d 3d7e 2acd d735 ec4f  :..G.Y.M=~*..5.O
< ... omitted ... >
007ffeb0: 3ae4 b447 0c59 2e4d 3d7e 2acd d735 ec4f  :..G.Y.M=~*..5.O
```

We can see that a large part of the binary repeats itself after 256 bytes.
This must be the block size that was used to encrypt the file.

We then created a python script to display the file and assign a random color
to each block:

![\[visualization\]](/images/posts/2017-09-07-securityweekctf-encrypted-blob.png)

We can see that a large part of the file consists of the same block repeating
over and over.

We initially concluded that the file must have been encrypted with a block
cipher that does not use a special mode to prevent us from seeing the structure
of the plain text. But if something like AES ECB mode was used, we would not
be able to decrypt the file without the key. So it must be something else.

What if someone just used an XOR pad with 256 bytes on each block? It would
result in the same structure as we found. So we extdended our script to XOR
every block with the block that is repeating, because we believe this is a block
that only contains zeros.

As a result we get a correctly decrypted ext3 filesystem image. We can mount:

```
$ sudo mkdir /mnt/router
$ sudo mount -o loop decr.bin /mnt/router
```

Now we search for something like flag. So we use `find`:

```
$ sudo -s
# cd /mnt/router
# find . -iname "*flag*"./etc/profile.d/flag.10
./etc/profile.d/flag.04
./etc/profile.d/flag.01
./etc/profile.d/flag.06
./etc/profile.d/flag.11
./etc/profile.d/flag.05
./etc/profile.d/flag.08
./etc/profile.d/flag.09
./etc/profile.d/flag.07
./etc/profile.d/flag.03
./etc/profile.d/flag.02
# cat etc/profile.d/flag*
{C0NGR4TZ_CRYPT0_CH3F}
```

So the flag was in `/etc/profile.d/` and was scattered over 11 files.

Interestingly, we can see the files in our original plot file as 11 dots separated
from the rest:

![\[visualization\]](/images/posts/2017-09-07-securityweekctf-encrypted-blob-2.png)

## Script

```python
import numpy as np
from PIL import Image
from random import randint

def slize_data(data, width):
    return [data[x*width:(x+1)*width] for x in range(len(data)//width)]

def xor_block(a, b):
    return bytes(x^y for x,y in zip(a,b))

def decrypt(blocks):
    return [xor_block(blocks[0], x) for x in blocks]

def blocks_to_file(blocks, filename):
    with open(filename, "wb") as f:
        for b in blocks:
            f.write(b)

def interpret(blocks):
    interp = []
    mapping = {}

    for b in blocks:
        if b in mapping:
            rep = mapping[b]
        else:
            rep = [randint(0, 256), randint(0, 256), randint(0, 256)]
            mapping[b] = rep
        interp.append(rep)
    return (interp, mapping)

def as_arr(arr, width):
    l = len(arr)
    height = l // width
    rest = (width - (l % width))%width
    if rest != 0:
        height += 1
    arr += [tuple((0, 0, 0)) for _ in range(rest)]
    print(len(arr), width, height)
    return np.array(arr, dtype='uint8').reshape((width, height, 3))

def save(array, filename):
    img = Image.fromarray(array.astype('uint8'), 'RGB')
    img.save(filename)

data = open("blob", "rb").read()
blocks256 = slize_data(data, 16*32)
colored = interpret(blocks256)[0]
matrix = as_arr(colored, 136)
save(matrix, 'out.png')

decrypted = decrypt(blocks256)
blocks_to_file(decrypted, "decr.bin")
```
