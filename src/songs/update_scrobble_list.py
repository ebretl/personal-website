from bs4 import BeautifulSoup
import requests
import os, sys
import csv
from datetime import datetime, timedelta
from collections import Counter
import time


headers = ['date', 'name']


def merge_song_list_dicts(dst, src):
    for date, new_list in src.items():
        if not date in dst:
            dst[date] = list()
        dst[date] += new_list

def get_songs(nAlreadyRecorded, page_num=1):
    url = 'https://www.last.fm/user/evanxq/library?date_preset=ALL&page=%d' \
            % page_num
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')

    today = datetime.date(datetime.now())

    nNeeded = 0
    for meta in soup.find_all("li", "metadata-item"):
        if meta.h2.string == "Scrobbles":
            nNeeded = int(meta.p.string)
            # print(nNeeded)

    print("page", page_num, "already recorded", nAlreadyRecorded,
        "/", nNeeded)

    song_lists = dict()
    for section in soup.find_all("section", "tracklist-section"):
        if nAlreadyRecorded >= nNeeded: break

        date_str = section.h2.string
        if date_str == 'Today':
            date = today
        elif date_str == 'Yesterday':
            date = today - timedelta(days=1)
        else:
            split = date_str.split(' ')[1:]
            date_str = "%02d %s %s" % tuple([int(split[0])] + split[1:])
            date = datetime.date(datetime.strptime(date_str, "%d %B %Y"))
        
        songs = list()
        for list_item in section.find_all('td', 'chartlist-name'):
            if nAlreadyRecorded >= nNeeded: 
                break
            link_block_targets = list_item.select('.link-block-target')
            song = link_block_targets[0].attrs['title']
            songs.append(song.format('utf-8'))
            nAlreadyRecorded += 1
        song_lists[str(date)] = songs

    isLastPage = soup.find("li", "pagination-next") == None

    if not isLastPage and nAlreadyRecorded < nNeeded:
        # time.sleep(1.0)
        new_lists = get_songs(nAlreadyRecorded, page_num + 1)
        merge_song_list_dicts(song_lists, new_lists)

    return song_lists
    


if __name__ == '__main__':
    
    fname = os.path.join(os.path.dirname(__file__), 'scrobbles.csv')

    data = dict()
    nAlreadyRecorded = 0
    if os.path.exists(fname):
        with open(fname,'r',encoding='utf-8') as f:
            reader = csv.reader(f)
            for line in reader:
                if len(line) > 0:
                    date, name = line
                else:
                    continue
                if date == headers[0]:
                    continue
                if not date in data:
                    data[date] = list()
                data[date].append(name)
                nAlreadyRecorded += 1

    newSongs = get_songs(nAlreadyRecorded)
    merge_song_list_dicts(data, newSongs)
    # print(data)

    with open(fname,'w',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for date in sorted(data.keys()):
            for name in data[date]:
                writer.writerow([date, name])
