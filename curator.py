import feedparser
import re

from jinja2 import Template
from curatordao import CuratorDao 

# Curator : Handle feed parsing for duplicates
class Curator:
    def __init__(self, feed_url):
        self.url = feed_url
        self.feed = None
        self.entries_to_keep = []
        self.dao = CuratorDao()

    def curate(self):
        self.feed = self.__get_parsed_feed()
        entries = self.feed[ 'entries' ]
        self.__calculate_unique_entries(entries)

    def generate_template(self):
        with open('rss2_template.xml') as f:
            template = Template(f.read())
            output_text = template.render(feed=self.feed, entries=self.entries_to_keep)
        return output_text

    def __calculate_unique_entries( self, entries ):
        for i in range(len(entries)):
            self.__add_entry_if_unique(entries[i])

    def __add_entry_if_unique(self, entry):
        entry_url = self.__cleanup_link_url( entry[ 'link' ] )
        if self.__is_entry_unique( entry_url ) is True:
            self.__mark_entry_visited( entry, entry_url )

    def __is_entry_unique(self, entry_url):
        return self.dao.entry_visited( entry_url ) == None

    def __mark_entry_visited(self, entry, entry_url):
        self.entries_to_keep.append( entry )
        self.dao.mark_entry_visited( entry_url )

    def __cleanup_link_url( self, url ):
       m = re.search(r'/$', url )
       if m is not None:
           return url[:-1]
       else:
           return url
    
    def __get_parsed_feed(self):
        return feedparser.parse( self.url )
