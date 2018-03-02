---
layout: page
title: Blog
permalink: /blog/
---

<ul>
{% for post in site.categories.blog %}
<li><a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a> @ {{ post.when }} </li>
{% endfor %}
</ul>

For more news, follow us on Twitter: [@LosFuzzys](https://twitter.com/LosFuzzys)

## Trainings

<p class="small dark">This is a (incomplete) list of some of our special trainings. For all trainings & other events check out <a href="/meetings/">our calendar</a>.</p>

<ul>
{% for post in site.categories.meeting %}
<li><a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a> @ {{ post.when }} </li>
{% endfor %}
</ul>

subscribe [via Atom]({{ "/feed.xml" | prepend: site.baseurl }})


