---
layout: page
title: Meetings
permalink: /meetings/
---

**IMPORTANT:**
All our meetings are open to everyone, so if you are not part of LosFuzzys, feel free to come anyway. And if you know some people interested in what we do, please invite them. :-)

(see also [our announcements below](#announcements).)


## Calendar

You can subscribe to our calendar with your favorite application using [our iCal feed](https://calendar.google.com/calendar/ical/2904.cc_lq509kkank97fftfkjm3gmbq70%40group.calendar.google.com/public/basic.ics).

The calendar contains LosFuzzys' trainings and meetings. Furthermore, we add interesting CTFs (details and discussions about our participation on the mailinglist). In addition, the calendar features events we consider relevant for our people (like conferences and important local events).

<iframe src="https://calendar.google.com/calendar/embed?showPrint=0&title=LosFuzzys%27%20Calendar&amp;showTitle=0&amp;showCalendars=0&amp;height=600&amp;wkst=2&amp;bgcolor=%23c0c0c0&amp;src=2904.cc_lq509kkank97fftfkjm3gmbq70%40group.calendar.google.com&amp;color=%238C500B&amp;ctz=Europe%2FVienna" style="border-width:0" width="800" height="600" frameborder="0" scrolling="no"></iframe>


## Weekly Trainings?

LosFuzzys and friends meet every Wednesday at 18:30 to discuss current topics, look at some CTF challenges together in a relaxed atmosphere, and talk about the security stuff we recently learned or the cool tool we just discovered.
It is always a good idea to bring your computer.

**The meetings are very informal an open to everyone!** For special meetings and topic announcements check out the calender (above) or the announcements (below).

We usually meet in IAIK's [Meeting room (IFEG074)](https://online.tugraz.at/tug_online/ris.ris?pOrgNr=983&pQuellGeogrBTypNr=5&pZielGeogrBTypNr=5&pZielGeogrBerNr=3020009&pRaumNr=4839&pActionFlag=A&pShowEinzelraum=J) or [Seminar room (IFEG042)](https://online.tugraz.at/tug_online/ris.ris?pOrgNr=983&pQuellGeogrBTypNr=5&pZielGeogrBTypNr=5&pZielGeogrBerNr=3020009&pRaumNr=4844&pActionFlag=A&pShowEinzelraum=J). Both rooms are part of TU Graz' [Inffeldgasse Campus](https://tu4u.tugraz.at/fileadmin/public/Studierende_und_Bedienstete/Bilder/Campusplan/Gebaeudebereich-IFG.gif) and located at the ground floor of Inffeldgasse 16a.

In case you are interested in participating (or just curious), feel free to visit us at the [FuzzyLab (IFEG064)](https://online.tugraz.at/tug_online/ris.ris?pOrgNr=983&pQuellGeogrBTypNr=5&pZielGeogrBTypNr=5&pZielGeogrBerNr=3020009&pRaumNr=4838&pActionFlag=A&pShowEinzelraum=J).


## Announcements

<ul>
{% for post in site.categories.meeting %}
<li><a href="{{ post.url | prepend: site.baseurl }}">{{ post.title }}</a> @ {{ post.when }} </li>
{% endfor %}
</ul>

subscribe [via Atom]({{ "/feed.xml" | prepend: site.baseurl }})


