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


log_file = os.path.join(os.path.dirname(__file__), '../private/logs/%d.log' % int(time.time()))
pkl_dir = os.path.join(os.path.dirname(__file__), '../private/song-pickles')
graph_file = os.path.join(os.path.dirname(__file__), '../data/song-graph-data.csv')

history_length = 150

def log(msg):
    with open(log_file, 'a') as f:
        f.write('[%s] %s\n' % (str(datetime.now()), msg))

def path_days_ago(days_ago):
    date_str = (date.today() - timedelta(days_ago)).isoformat()
    path = os.path.join(pkl_dir, date_str + '.pkl')
    return path

def get_songs_for_date(date_str, page=1):
    log("get_songs_for_date %s %d" % (date_str, page))

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
            counter = get_songs_for_date(os.path.split(path)[1][:-4])
            with open(path, 'wb') as f:
                pickle.dump(counter, f)
            log(str(counter))

def gen_graph_csv():
    m = history_length
    n = 30 # num songs to graph
    sigma = 10

    day_counters = []
    overall_counter = Counter()
    for days_ago in range(m-1, -1, -1):
        path = path_days_ago(days_ago)
        with open(path, 'rb') as f:
            counter = pickle.load(f)
            day_counters.append(counter)
            overall_counter.update(counter)

    with open(graph_file, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['title','count']+['x%d'%i for i in range(m)])
        for title, count in overall_counter.most_common(n):
            arr = np.zeros(m)
            for i in range(m):
                arr[i] = day_counters[i][title]
            arr = gaussian_filter1d(arr, sigma, mode='reflect')
            csv_writer.writerow([title, count] + ['0' if x<0.01 else '%.2f'%x for x in arr])


if __name__ == '__main__':
    if not os.path.exists(pkl_dir):
        os.makedirs(pkl_dir)
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    while True:
        try:
            update_all()
        except:
            log("error on update_all")

        try:
            gen_graph_csv()
        except:
            log("error on gen_graph_csv")
        
        time.sleep(60 * 60)
        # sys.exit(0)
