---
layout: post
title: "Security Week Graz 2018: Flight Radar"
author: dux, exo
categories: writeup
tags: [cat/crypto]
---

* **Category:** crypto
* **Points:** 30
* **Description:**

> You captured some messages from planes flying over you using a simple SDR.
> Unfortunately, most of them are encrypted.
> Find out what the encrypted status message of the planes is.
>
> [\[flight-data.zip\]](https://ctf.attacking.systems/files/70130b13eb84f521329ad213e16d35d6/flight-data.zip)

## Observations

We parsed the pcap file and printed each packet in one line.
We then notice that most of the packets consist of rubish:
{% raw %}
```
b'wgm=,H|yymQMmUJ=U,m|U,wu\x7f,wu\x7f,yJyy,U=Q{,2h4zOzh\\n\\gjLP'
b'gum=,H{QQyJM|m|U{,yQy,H4b,GKL,UQyU,y{|{,2h4zOzh\\n\\gjLP'
b'h6mJ,bjQ=Q>9>m{jU,QQj,\x7fss,OnE,U{yU,QQU{,2h4zOzh\\n\\gjLP'
b'g]m{,H=|||Q9={J|J,y=>,]bw,\x7fOb,y=U>,yUmQ,2h4zOzh\\n\\gjLP'
b'h6mj,bU=myQM>Q{Qj,{{J,\x7fOb,Lz8,yUU>,U{|m,2h4zOzh\\n\\gjLP'
b'Egmy,by{{=Q9j=={|,jJ=,4Ob,Hhb,QjUy,UJyQ,2h4zOzh\\n\\gjLP'
b'h\\m=,by|yU|9yy=>>,m{|,\x7f~6,\x7f~6,Q>yy,U=ym,2h4zOzh\\n\\gjLP'
b'~Hmj,bm>J={9>UQQ|,m||,4Ob,GKL,yQyU,UQmy,2h4zOzh\\n\\gjLP'
b'hmm=,bQ|>{UMQy>yU,=Uy,Hhb,hng,U|U=,UJy{,2h4zOzh\\n\\gjLP'
```
{% endraw %}

However, there are some packets of the form:

```
b'SU36,S24992W00807,730,IAD,ATL,2503,2044,STATUS {OK}'
```

This gives us the format and contents of each packet, the
encrypted ones probably also have the same format. We then
notice that for the coordinate fields like `S24992W00807` the
encryption always starts with the same two characters `b` and `H`,
which are then the encryptions of `S` and `N`, but we don't know
which is which. This also gives us the working theory that the
encryption used is a substitution cipher.

## Solution

We filtered out all the unencrypted packets and looked for
parts which are repeated. Most notably, the *from* and *to* fields
of each packet always contain the same city signatures.

Unencrypted *from* and *to* fields:

```
SAN, SFO, HKG, MUC, LHR, ATL, KIL, DEL, CTU, DXB, PVG, IST, ORD, IAD, HND, BOM, IBZ, BKK, SIN, DFW, GRZ, PEK, BCN, CAN, LAX, MAD, JFK, YYZ, VIE, CDG, ICN, CGK, AMS, FRA
```

Encrypted *from* and *to* fields:
```
b'OnE', b's4g', b']bw', b'4\x7f8', b']sL', b'w9g', b'4Hn', b'\\zh', b'OLs', b'ghu', b'K49', b'\x7f~6', b'f\\s', b'4Ob', b'H4b', b'Hhb', b'hng', b'6hw', b'Lz8', b'\x7fOb', b'GKL', b'~zw', b'\x7fss', b'4hw', b'w\\M', b'wu\x7f', b'6EO', b'OwL', b'H\\~', b'g]z', b'Ohb', b'::8', b'h6H', b'G9s'
```

Now, to calculate the substitution table, we just need to
match the unencrypted and encrypted *form* and *to* fields.
One would usually do this with a constraint solver, but ain't
nobody got time for that, so we did it by hand.

We started by assuming that `S` and `N` map to `b` and `H`, and then
figured out which had to be which, based on the occurrences. Then we used
the cities which have two identical letters and constrained further
and further until we had a lookup table for all characters in the alphabet.

The mapping is shown below:
```
[('h', 'A'), ('\x7f', 'B'), ('O', 'C'), ('w', 'D'), ('9', 'E'),
('\\', 'F'), ('L', 'G'), (']', 'H'), ('4', 'I'), ('f', 'J'), ('s', 'K'),
('g', 'L'), ('6', 'M'), ('b', 'N'), ('~', 'O'), ('G', 'P'), ('z', 'R'),
('H', 'S'), ('n', 'T'), ('E', 'U'), ('K', 'V'), ('M', 'W'), ('u', 'X'),
(':', 'Y'), ('8', 'Z')]
```

We then decrypted one of the encrypted packets and received:

```
DL???S?????W??????????DXB?DXB????????????AIRCRAFTFL?G?
```

## Flag

The part that contains the flag is the status, as mentioned in the
challenge description. We then just figured the missing letter had
to be hexspeak and recovered the flag `{AIRCRAFTFL4G}`
