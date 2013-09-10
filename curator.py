#!/usr/bin/env python

import boto
import datetime
import feedparser
import hashlib
import os
import sqlite3
import sys
import time

from boto.s3.key import Key
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

    def get_s3_bucket( self ):
        return self.__select_s3_bucket_from_db()

    def set_s3_bucket( self, name ):
        self.__insert_s3_bucket_into_db( name ) 

    def __select_item_url_from_db( self, item_url ):
        self.__create_unique_links_table_if_necessary()
        c = self.conn.cursor()
        t = (item_url,)
        c.execute( 'select link from unique_links where link=?', t)
        return c.fetchone()

    def __insert_url_into_db( self, item_url ):
        self.__create_unique_links_table_if_necessary()
        c = self.conn.cursor()
        t = (self.__get_date(), item_url,)
        c.execute( 'insert into unique_links values (?, ?)', t )
        self.conn.commit()

    def __create_unique_links_table_if_necessary(self) :
        c = self.conn.cursor()
        c.execute( '''create table if not exists unique_links
              (curated_at text, link text)''')

    def __select_s3_bucket_from_db( self ):
        self.__create_s3_bucket_table_if_necessary()
        c = self.conn.cursor()
        c.execute( 'select bucket_name from s3_bucket' )
        return c.fetchone()

    def __insert_s3_bucket_into_db( self, name ):
        self.__create_s3_bucket_table_if_necessary()
        c = self.conn.cursor()
        t = (name,)
        c.execute( 'insert into s3_bucket values (?)', t )
        self.conn.commit()

    def __create_s3_bucket_table_if_necessary(self) :
        c = self.conn.cursor()
        c.execute( '''create table if not exists s3_bucket 
              (bucket_name text)''')

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
        with open('rss2_template.xml') as f:
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

# Store Curated Feed in AWS S3 for self hosting
class CuratorPublisher:
    def __init__(self, feed_url):
        self.url = feed_url

    def publish_feed_to_s3(self, content):
        if not boto.config.has_section('Credentials'): 
            raise Exception("Boto configuration not found! Cannot Continue.")
        s3 = boto.connect_s3()
        bucket = s3.create_bucket(self.__get_bucket_name())
        k = Key(bucket)
        k.key = self.url
        k.set_contents_from_string(content,headers={'Content-Type': 'application/rss+xml'})
        k.set_acl('public-read')
        feed_url = k.generate_url(0, query_auth=False, force_http=True)
        print "Your RSS Subscription is available at:\n%s" % feed_url 
       
    def __get_bucket_name(self):
        dao = CuratorDao()
        bucket_name = dao.get_s3_bucket()
        if bucket_name is None:
            bucket_name = self.__generate_bucket_name()
            dao.set_s3_bucket(bucket_name)
            return bucket_name
        else:
            return bucket_name[0]

    def __generate_bucket_name(self):
        suffix = 'greymeistercurator'
        noise = os.urandom(1024)
        return  ''.join([hashlib.sha1(noise).hexdigest(), suffix])

# Script Function
def get_feed_url_from_args():
    return sys.argv[1]


# Command Line
if len(sys.argv) < 2:
    sys.exit('usage: %s feed_name_or_url' % sys.argv[0])
    
url = get_feed_url_from_args()
curator = Curator(url)
curator.curate()
content = curator.generate_template() 
publisher = CuratorPublisher(url)
publisher.publish_feed_to_s3(content)

