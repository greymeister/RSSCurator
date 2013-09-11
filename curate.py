#!/usr/bin/env python

import os
import sys

from curator import Curator
from curatorpublisher import CuratorPublisher

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

