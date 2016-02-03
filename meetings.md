---
layout: page
title: Meetings
permalink: /meetings/
---

<ul>
{% for post in site.categories.meeting %}
<li><a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a> @ {{ post.when }} </li>
{% endfor %}
</ul>

**IMPORTANT:**
All our meetings are open to everyone, so if you are not part of LosFuzzys, feel free to come anyway. And if you know some people interested in what we do, please invite them. :-)

## Past CTF participations

<!-- generated using scripts/getPastCTFs.py  -->

* 2016
  * Insomni'hack teaser <span class="discreet">(place 44 of 245)</span>
* 2015
  * 32C3 CTF <span class="discreet">(place 58 of 389)</span>
  * FAUST CTF <span class="discreet">(place 6 of 62)</span>
  * 9447 Security Society CTF <span class="discreet">(place 24 of 595)</span>
  * RuCTFE <span class="discreet">(place 22 of 140)</span>
  * TUM CTF Teaser <span class="discreet">(place 45 of 445)</span>
  * Defcamp CTF Qualification <span class="discreet">(place 96 of 378)</span>
  * PoliCTF <span class="discreet">(place 71 of 325)</span>
  * DEF CON CTF Qualifier <span class="discreet">(place 145 of 284)</span>
  * Boston Key Party CTF <span class="discreet">(place 90 of 822)</span>
  * Ghost in the Shellcode <span class="discreet">(place 283 of 321)</span>
* 2014
  * RuCTFE <span class="discreet">(place 62 of 133)</span>
  * Hack.lu CTF <span class="discreet">(place 85 of 395)</span>
  * PlaidCTF <span class="discreet">(place 133 of 867)</span>


subscribe [via Atom]({{ "/feed.xml" | prepend: site.baseurl }})