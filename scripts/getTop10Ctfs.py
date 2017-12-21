#!/usr/bin/env python3

import requests
import argparse
from sys import exit
from bs4 import BeautifulSoup
from datetime import datetime as d


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--year', default=d.now().year)
    parser.add_argument('--team', default=8323) # LosFuzzys
    args = parser.parse_args()

    s = requests.session()
    resp = s.get('https://ctftime.org/team/{}'.format(args.team))
    soup = BeautifulSoup(resp.content, 'html.parser')
    year = soup.find('div', attrs={'id': 'rating_{}'.format(args.year)})
    if not year:
        print("Nothing find for year {}.".format(args.year))
        exit(-1)
    table = year.find('table', attrs={'class':'table table-striped'})

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
