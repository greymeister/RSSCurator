import datetime
import sqlite3

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
