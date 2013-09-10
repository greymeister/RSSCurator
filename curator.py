#!/usr/bin/env python

import datetime
import feedparser
import sqlite3
import sys

from jinja2 import Template

# Data access object for Curator
class CuratorDao:
    def __init__(self):
        self.db_name = 'curator.db'
        self.conn = self.__get_db_connection()

    def entry_visited( self, url ):
        return self.__select_item_url_from_db(url)

    def mark_entry_visited( self, url ):
        self.__insert_url_into_db( url )

    def __select_item_url_from_db( self, item_url ):
        self.__create_table_if_necessary()
        c = self.conn.cursor()
        t = (item_url,)
        c.execute( 'select link from unique_links where link=?', t)
        return c.fetchone()

    def __insert_url_into_db( self, item_url ):
        self.__create_table_if_necessary()
        c = self.conn.cursor()
        t = (self.__get_date(), item_url,)
        c.execute( 'insert into unique_links values (?, ?)', t )
        self.conn.commit()

    def __create_table_if_necessary(self) :
        c = self.conn.cursor()
        c.execute( '''create table if not exists unique_links
              (curated_at text, link text)''')

    def __get_db_connection(self):
            return sqlite3.connect(self.db_name)

    def __get_date(self):
        return datetime.datetime.now().strftime( "%Y-%m-%d" ) 

# Curator : Handle feed parsing for duplicates
class Curator:
    def __init__(self, feed_url):
        self.url = feed_url
        self.feed = self.__get_feed()
        self.entries_to_keep = []

    def curate(self):
        feed = self.__get_feed()
        entries = feed[ 'entries' ]
        self.__calculate_unique_entries(entries)

    def generate_template(self):
        with open('template.xml') as f:
            template = Template(f.read())
            output_text = template.render(feed=self.feed, entries=self.entries_to_keep)
        return output_text

    def __calculate_unique_entries( self, entries ):
        dao = CuratorDao()
        for i in range(len(entries)):
            entry = entries[i]
            entry_url = entry[ 'link' ]
            entry_already_exists = dao.entry_visited( entry_url )
            if entry_already_exists is None:
                self.entries_to_keep.append(entry)
                dao.mark_entry_visited( entry_url )

    def __get_feed(self):
        return feedparser.parse( self.url )

# Script Function
def get_feed_url_from_args():
    return sys.argv[1]


# Command Line
if len(sys.argv) < 2:
    sys.exit('usage: %s feed_name_or_url' % sys.argv[0])
    
url = get_feed_url_from_args()
curator = Curator(url)
curator.curate()
print curator.generate_template() 

