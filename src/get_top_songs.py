from bs4 import BeautifulSoup
import requests

url = 'https://www.last.fm/user/evanxq/library/tracks?date_preset=LAST_90_DAYS'
r = requests.get(url).text
soup = BeautifulSoup(r, 'html.parser')

with open('top_songs.txt','w',encoding='utf-8') as f:
    for item in soup.find_all('td', 'chartlist-name'):
        song = item.find('a', 'link-block-target').attrs['title']
        f.write(song.format('utf-8') + '\n')
