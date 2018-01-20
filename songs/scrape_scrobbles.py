from bs4 import BeautifulSoup
import requests
import os, sys
from datetime import date, datetime, timedelta
import time
from collections import Counter
import pickle
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
import csv
import lzma
import re

base_dir = os.path.dirname(__file__)
log_file = os.path.join(base_dir, '../private/logs/%d.log' % int(time.time()))
pkl_dir = os.path.join(base_dir, '../private/song-pickles')
song_graph_file = os.path.join(base_dir, '../data/song-graph-data.csv')
artist_graph_file = os.path.join(base_dir, '../data/artist-graph-data.csv')

history_length = 90

def log(msg):
    print(msg)
    with open(log_file, 'a') as f:
        f.write('[%s] %s\n' % (str(datetime.now()), msg))

def path_days_ago(days_ago):
    date_str = (date.today() - timedelta(days_ago)).isoformat()
    path = os.path.join(pkl_dir, date_str + '.pkl.lzma')
    return path

def get_songs_for_date(date_str, page=1):
    # log("get_songs_for_date %s %d" % (date_str, page))

    url = 'https://www.last.fm/user/evanxq/library?to=%s&from=%s&page=%d' \
            % (date_str, date_str, page)
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    counter = Counter()

    for span in soup.select('.chartlist-ellipsis-wrap'):
        artist_title = span('a')[1].get('title').lower()
        counter[artist_title] += 1

    if soup.find("li", "pagination-next"):
        counter.update(get_songs_for_date(date_str, page + 1))

    return counter

def update_all():
    for days_ago in range(history_length-1, -1, -1):
        path = path_days_ago(days_ago)
        
        if not os.path.exists(path) or days_ago < 2:
            counter = get_songs_for_date(os.path.split(path)[1].split('.')[0])
            with lzma.open(path, 'wb') as f:
                pickle.dump(counter, f)
            # log(str(counter))

def split_artist_list(list_str):
    artists_tmp = list_str.split(', ')
    artists = []
    for a in artists_tmp:
        artists += a.split(' & ')
    return artists

def song_to_artists(song_str):
    splt = song_str.split(' — ')
    if len(splt) != 2:
        log("song string %s cannot be converted to artists" % song_str)
        return Counter()
    artists = split_artist_list(splt[0])

    m = re.search(r'\(.* remix\)', splt[1])
    if m:
        # print(split_artist_list(m.string[m.start()+1:m.end()-7]))
        artists += split_artist_list(m.string[m.start()+1:m.end()-7])
    return artists

def songs_to_artists(songs_counter):
    artists = Counter()
    for song, count in songs_counter.items():
        this_artists = song_to_artists(song)
        artists.update(this_artists * count)
    return artists

def gen_graph_csv():
    m = history_length
    n = 15 # num songs to graph
    sigma = 4

    day_counters = []
    overall_counter = Counter()
    for days_ago in range(m-1, -1, -1):
        path = path_days_ago(days_ago)
        with lzma.open(path, 'rb') as f:
            counter = pickle.load(f)
            day_counters.append(counter)
            overall_counter.update(counter)

    with open(song_graph_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['name','count']+['x%d'%i for i in range(m)])
        for title, count in overall_counter.most_common(n):
            arr = np.zeros(m)
            for i in range(m):
                arr[i] = day_counters[i][title]
            arr = gaussian_filter1d(arr, sigma, mode='reflect')
            csv_writer.writerow([title, count] + ['0' if x<0.01 else '%.2f'%x for x in arr])


    n = 15 # num artists to graph
    sigma = 3

    day_counters = []
    overall_counter = Counter()
    for days_ago in range(m-1, -1, -1):
        path = path_days_ago(days_ago)
        with lzma.open(path, 'rb') as f:
            counter = pickle.load(f)
            day_artists = songs_to_artists(counter)
            day_counters.append(day_artists)
            overall_counter.update(day_artists)

    with open(artist_graph_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['name','count']+['x%d'%i for i in range(m)])
        for artist, count in overall_counter.most_common(n):
            arr = np.zeros(m)
            for i in range(m):
                arr[i] = day_counters[i][artist]
            arr = gaussian_filter1d(arr, sigma, mode='reflect')
            csv_writer.writerow([artist, count] + ['0' if x<0.01 else '%.2f'%x for x in arr])


if __name__ == '__main__':
    if not os.path.exists(pkl_dir):
        os.makedirs(pkl_dir)
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    try:
        update_all()
    except:
        log("error on update_all: " + str(sys.exc_info()[0]))

    try:
        gen_graph_csv()
    except:
        log("error on gen_graph_csv: " + str(sys.exc_info()[0]))

