from bs4 import BeautifulSoup
import requests
import os

url = 'https://www.last.fm/user/evanxq/library/tracks?date_preset=LAST_90_DAYS'
r = requests.get(url).text
soup = BeautifulSoup(r, 'html.parser')

fname = os.path.join(os.path.dirname(__file__), 'top_songs.txt')
with open(fname,'w',encoding='utf-8') as f:
    for item in soup.find_all('td', 'chartlist-name'):
        song = item.find('a', 'link-block-target').attrs['title']
        f.write(song.format('utf-8') + '\n')
