#!/usr/bin/env python

#
# Run script and copy output to bottom of meetings.md
#

import re
import time
import requests
from bs4 import BeautifulSoup

BASEURL = 'https://ctftime.org'
TEAMURL = '/team/8323' # LosFuzzys
# TEAMURL = '/team/59774' # KuK Hofhackerei

# API (not usefull):
# * https://ctftime.org/api/v1/teams/8323/ --> not enough infos :(
# * https://ctftime.org/api/v1/events/212/ --> wrong numbers :(

re_overall = '<p align=\"left\">Overall rating place: <b>\s*(\d+)\s*</b> with <b>(\d*\.\d*)</b> pts in (\d+)</p>'

headers = { # since CTFtime started to block python requests ...
    'User-Agent': 'LosFuzzys Crawler 2018.08.24'
   }

def getNumberOfParticipatingTeams(ctf_url):
    team_html = requests.get(BASEURL + ctf_url, headers=headers).text
    soup = BeautifulSoup(team_html, 'html.parser')

    return soup.find_all('td', {'class': 'place'})[-1].string


def logScore(year, place, points):
    with open(year + '.log', "a") as logfile:
        logfile.write('%d;%s;%s\n' % (int(time.time()), place, points))


def getPastCTFs():
    team_html = requests.get(BASEURL + TEAMURL, headers=headers).text
    soup = BeautifulSoup(team_html, 'html.parser')

    for year_data in soup.find_all('div', id=re.compile("rating_")):
        year = year_data.get('id')[7:]
        print '* %s' % year
        p = str(year_data.find_all('p')[0])
        score = re.search(re_overall, p)
        place, points = score.group(1), score.group(2)
        scorestring = '<!-- place %s (%s points) -->' % (place, points)
        logScore(year, place, points)
        for ctf in year_data.find_all('tr'):
            cols = ctf.find_all('td')
            if len(cols) <= 0:  # if idx == 0
                print '  %s' % scorestring
                continue
            ctf_place = cols[1].string
            ctf_name = cols[2].string.replace(year, '').strip()
            ctf_name = ctf_name[:-1] if ctf_name.endswith('-') else ctf_name
            ctf_url = cols[2].find('a').get('href')
            ctf_participants = getNumberOfParticipatingTeams(ctf_url)
            print '  * %s <span class="discreet">(place %s of %s)</span>' % (ctf_name, ctf_place, ctf_participants)

if __name__ == '__main__':
    getPastCTFs()
