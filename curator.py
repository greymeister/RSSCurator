#!/usr/bin/env python

import datetime
import feedparser
import sqlite3
import sys

from jinja2 import Template

def get_feed_url_from_args():
    return sys.argv[1]

def get_db_connection():
    return sqlite3.connect('curator.db')

def get_feed_from_url(url):
    return feedparser.parse( url )

def get_timestamp():
    return datetime.datetime.now().strftime( "%Y-%m-%d" ) 

def create_table_if_necessary( conn ) :
    c = conn.cursor()
    c.execute( '''create table if not exists unique_links
              (curated_at text, link text)''')

def select_item_url_from_db( conn, item_url ):
    c = conn.cursor()
    t = (item_url,)
    c.execute( 'select link from unique_links where link=?', t)
    return c.fetchone()

def insert_url_into_db( conn, item_url ):
    c = conn.cursor()
    t = (get_timestamp(), item_url,)
    c.execute( 'insert into unique_links values (?, ?)', t )
    conn.commit()

# Setup
#url = "http://news.ycombinator.com/rss"
url = get_feed_url_from_args()
conn = get_db_connection() 
create_table_if_necessary( conn )
feed = get_feed_from_url( url ) 
entries = feed[ 'entries' ]
entries_to_keep = []


for i in range(len(entries)):
    entry = entries[i]
    entry_url = entry[ 'link' ]
    entry_already_exists = select_item_url_from_db( conn, entry_url )
    if entry_already_exists is None:
        entries_to_keep.append(entry)
        insert_url_into_db( conn, entry_url )

with open('template.xml') as f:
    template = Template(f.read())
    output_text = template.render(feed=feed, entries=entries_to_keep)
    print output_text

