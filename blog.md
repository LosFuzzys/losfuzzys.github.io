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

<ul>
{% for post in site.categories.meeting %}
<li><a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a> @ {{ post.when }} </li>
{% endfor %}
</ul>

subscribe [via Atom]({{ "/feed.xml" | prepend: site.baseurl }})


