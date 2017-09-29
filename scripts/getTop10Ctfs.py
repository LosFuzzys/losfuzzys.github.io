#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

s = requests.session()
resp = s.get('https://ctftime.org/team/8323')
soup = BeautifulSoup(resp.content, 'html.parser')
table = soup.find('table', attrs={'class':'table table-striped'})

events = []
for row in table.find_all('tr'):
    cols = row.find_all('td')
    if len(cols) < 5:
        continue
    event = {
            'place': int(cols[1].text),
            'name': cols[2].text,
            'points': float(cols[4].text),
            }
    events.append(event)

for e in sorted(events, key=lambda k: k['points'], reverse=True)[:10]:
    print('{:3d} {:40s} {:6.3f}'.format(e['place'], e['name'], e['points']))
