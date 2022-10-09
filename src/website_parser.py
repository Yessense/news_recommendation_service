# Скрипт подгрузки и анализа свежих новостей с RSS
import os.path
from typing import List

import torch
from rss_parser import Parser
from requests import get
import requests

import psycopg2
import time
from dateutil import parser
from psycopg2 import sql
import pickle

N = 5
NEWS_BUFFER = []
ROLES_EMBEDDINGS = []
THRES = 0.8

# Get buffer

def get_last_n_news_from_bd(N:int=100) -> list:
    conn = psycopg2.connect("host=89.208.231.41 dbname=VTB-Hack user=user password=262}ym2C0A79vdFw")
    query = sql.SQL(f'SELECT embedding, id FROM "RSSTable" ORDER BY id DESC LIMIT {N}')
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    
    return result


# [embedding, индекс]- 100 ПОСЛЕДНИХ НОВОСТЕЙ вместе с эмбеддингами.
def download_NEWS_BUFFER():
    global NEWS_BUFFERG
    NEWS_BUFFER = get_last_n_news_from_bd(100)
    # print(NEWS_BUFFER[0])
    
# E M B S

def get_emb_from_string(s):
    text = {'news': [s]}
    emb = requests.post("http://127.0.0.1:8080/get_embeddings", json=text).text

    return eval(emb)

def get_embs_from_strings(strings: List[str]) -> list:
    """Описание ролей, сохраненное в виде эмбеддингов"""
    """ибо любой другой текст"""
    text = {'news': strings}
    embs = requests.post("http://127.0.0.1:8080/get_embeddings", json=text).text
    return embs

def has_similarities(emb, embs):
    embs = [e for e in embs if e is not None]
    json = {'target': emb,
            'source': embs}
    similarities = requests.post("http://127.0.0.1:8080/get_similarity", json=json).text
    similarities = eval(similarities)
    similarities = torch.tensor(similarities)
    similarities = similarities >= THRES
    is_unique = sum(similarities) == 0
    return is_unique, similarities

# if not has similarities: update queue and db !!!

def update_queue(emb):
    global NEWS_BUFFER
    NEWS_BUFFER.pop()

    conn = psycopg2.connect("host=89.208.231.41 dbname=VTB-Hack user=user password=262}ym2C0A79vdFw")
    query = sql.SQL(f'SELECT id FROM "RSSTable" ORDER BY id DESC LIMIT 1')
    cursor = conn.cursor()
    cursor.execute(query)
    db_ind = cursor.fetchall()[0]

    new = [emb, db_ind]
    NEWS_BUFFER.insert(0, new)
    
# if has similarities: increment in db

def increment_num_of_similarities_in_db(similarities):
    """ Увеличивает на 1 количество повторений для новости"""
    for i, elem in enumerate(similarities):
        if elem:
            db_ind = NEWS_BUFFER[i][1] # ИНдекс новости в базе
            conn = psycopg2.connect("host=89.208.231.41 dbname=VTB-Hack user=user password=262}ym2C0A79vdFw")
            cur = conn.cursor()
            if isinstance(db_ind, tuple):
                db_ind = db_ind[0]

            query = sql.SQL(f"UPDATE \"RSSTable\" SET score=score+1 WHERE id={db_ind}")
            cur.execute(query)
            conn.commit()

            
    

# П А Р С И Н Г

def dump_to_pickle(url, feed):
    with open(url.replace('/', '').replace(':', '').replace('.', '') + '.pickle', 'wb') as handle:
        pickle.dump(feed, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_from_pickle(url):
    with open(url.replace('/', '').replace(':', '').replace('.', '')+ '.pickle', 'rb') as handle:
        b = pickle.load(handle)
        return b


def date_to_format(rss_date):
    dt = parser.parse(rss_date)
    return dt.strftime("%d.%m.%Y")

def get_feed(rss_url, n=None):
    xml = get(rss_url)
    parser = Parser(xml=xml.content, limit=n)
    feed = parser.parse()
    return feed

def get_feed_without_dubs(feed, last_feed):
    new_feed = []
    got_feed = []
    for item in feed.feed:
        is_new = True
        if last_feed:
            for last_item in last_feed:
                if item == last_item:
                    is_new = False
                    break
        got_feed.append(item)
        if is_new:
            new_feed.append(item)
    return got_feed, new_feed

# В Ы Г Р У З К А  В  Б Д

def get_cort(n, item, emb, verbose=True):

    keys = ['title',
             'link',
             'category',
             'publish_date',
             'description']

    vals = []
        
    if verbose:
        print("№:", n)
            
    for key in keys:
        val = getattr(item, key)
        if key == 'publish_date':
            val = date_to_format(val)
        if verbose:
            print(key.capitalize() + ':', val)
        
        vals.append(val)
            
    if verbose:
        print()    
                
    cort = tuple(map(str, vals+[emb]))
    return cort

def dump_feed_to_db(new_feed, verbose=True):
    
    conn = psycopg2.connect("host=89.208.231.41 dbname=VTB-Hack user=user password=262}ym2C0A79vdFw")
    cursor = conn.cursor()
    
    # # #
    for n, item in enumerate(new_feed):
        emb = item.description
        emb = get_emb_from_string(emb)[0]
        embs = [elem[0] for elem in NEWS_BUFFER]
        is_unique, similarities = has_similarities(emb, embs)
        
        if is_unique:
            cort = get_cort(n, item, emb)
            cursor.execute("INSERT INTO \"RSSTable\" (title, link, subjects_category, publish_date, description, embedding) VALUES(%s, %s, %s, %s, %s, %s)", cort)
            update_queue(emb)
        else:
            increment_num_of_similarities_in_db(similarities)
        
    conn.commit()
    cursor.close()
    conn.close()

def iteration(rss_url, last_feed):
    feed = get_feed(rss_url)
    got_feed, new_feed = get_feed_without_dubs(feed, last_feed)
    dump_feed_to_db(new_feed)
    # dump_to_pickle(rss_url, got_feed)
    
    return got_feed

def cycle():
    
    urls = ["https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
            "https://www.klerk.ru/xml/index.xml",
            "https://www.glavbukh.ru/rss/news.xml",
            "http://www.consultant.ru/rss/db.xml",
            "https://finance.rambler.ru/rss/business/",
            "https://www.business-gazeta.ru/rss.xml"
            ]

    d = dict.fromkeys(urls, None)
            
    while True:
        for url in urls:
            last_feed = d[url]
            if not last_feed:
                try:
                    last_feed = load_from_pickle(os.path.join('../rss/', url))
                except Exception as err:
                    pass
            d[url] = iteration(url, last_feed)

        time.sleep(300) # 60 * 10
        
# Main

if __name__ == '__main__':
    download_NEWS_BUFFER()
    cycle()
