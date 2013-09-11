import feedparser
import re

from jinja2 import Template
from curatordao import CuratorDao 

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
            entry_url = self.__cleanup_link_url( entry[ 'link' ] )
            entry_already_exists = dao.entry_visited( entry_url )
            if entry_already_exists is None:
                self.entries_to_keep.append(entry)
                dao.mark_entry_visited( entry_url )

    def __cleanup_link_url( self, url ):
       m = re.search(r'/$', url )
       if m is not None:
           return url[:-1]
       else:
           return url
    
    def __get_feed(self):
        return feedparser.parse( self.url )
