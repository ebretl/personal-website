from bs4 import BeautifulSoup
import requests
import os, sys
import csv
from datetime import datetime, timedelta

history_length = 50
favorites_period = 30
n_favorites = 25
headers = ['date'] + list(range(1, 1+n_favorites))

def get_top_songs_list(date):
    start_date = date - timedelta(days=favorites_period)

    url = 'https://www.last.fm/user/evanxq/library/tracks?from=%s&to=%s' \
            % (str(start_date), str(date))
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')

    faves = []
    for item in soup.find_all('td', 'chartlist-name'):
        song = item.find('a', 'link-block-target').attrs['title']
        faves.append(song.format('utf-8'))
    
    return faves[:n_favorites]


if __name__ == '__main__':

    data = dict()
    fname = os.path.join(os.path.dirname(__file__), 'top_songs.csv')

    if os.path.exists(fname):
        with open(fname,'r',encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= n_favorites+1:
                    k = row[0]
                    v = row[1:n_favorites+1]
                    data[k] = v

    h0 = headers[0]
    if h0 in data:
        del data[h0]

    today = datetime.date(datetime.now())
    ago = lambda i: today - timedelta(days=i)
    date_targets = set(str(ago(i)) for i in range(history_length))
    dates_existing = set(data.keys())

    remove = dates_existing - date_targets
    for date_str in iter(remove):
        del data[date_str]

    unchecked = date_targets - dates_existing

    if str(today) in unchecked:
        data[str(today)] = get_top_songs_list(today)

    elif unchecked:
        date_str = next(iter(unchecked))
        date = datetime.date(datetime.strptime(date_str, "%Y-%m-%d"))
        data[date_str] = get_top_songs_list(date)

    else:
        #overwrite
        data[str(today)] = get_top_songs_list(today)

    with open(fname,'w',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([str(x) for x in headers])
        for k in sorted(data.keys()):
            writer.writerow([k] + data[k])
