---
layout: post
title:  "Hack More Systems! New and old domain"
when: "September 24, 2018"
author: verr
categories: blog
---

Since [the beginning](https://github.com/LosFuzzys/losfuzzys.github.io/commit/5c8986d2dc0ea8531a16221dc0efdf15cef13b0f) our website was hosted on [GitHub Pages](https://pages.github.com/), reachable via **losfuzzys.github.io**. 
When we started to use **hack.more.systems** as our main domain (for email and web), it was not possible to configure GitHub pages to use our custom domain. 

While they [support custom domains](https://help.github.com/articles/using-a-custom-domain-with-github-pages/) since forever, it was not possible to use TLS on them back then. 
Because we wanted proper TLS on our website, we pointed the domain at one of our webservers (hosted at the local hackspace [realraum](https://r3.at)) and redirected users to our GitHub domain from there.
[This obstacle was removed](https://blog.github.com/2018-05-01-github-pages-custom-domains-https/) this year, and GitHub now supports TLS on custom domains as well - thanks to [Let's Encrypt](https://letsencrypt.org/).

And so we finally did it - and our website is now reachable directly on [**https://hack.more.systems**](https://hack.more.systems).

*Happy hacking!*

---

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">Since <a href="https://twitter.com/github?ref_src=twsrc%5Etfw">@GitHub</a> pages started to support TLS for custom domain names this year (thanks, <a href="https://twitter.com/letsencrypt?ref_src=twsrc%5Etfw">@letsencrypt</a>! [*]), we finally got rid of our ugly TLS redirect.<br><br>Come, visit <a href="https://t.co/THDZCkGwjP">https://t.co/THDZCkGwjP</a> 💥<br><br>(Don&#39;t send us your credit card numbers, though.)<br><br>[*] <a href="https://t.co/GuahlH09B3">https://t.co/GuahlH09B3</a> <a href="https://t.co/LQ4Cjuzfc9">pic.twitter.com/LQ4Cjuzfc9</a></p>&mdash; LosFuzzys (@LosFuzzys) <a href="https://twitter.com/LosFuzzys/status/1044251394939727872?ref_src=twsrc%5Etfw">September 24, 2018</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>