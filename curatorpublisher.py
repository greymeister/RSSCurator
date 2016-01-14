# Store Curated Feed in AWS S3 for self hosting

import boto
import hashlib
import os
from boto.s3.key import Key
from curatordao import CuratorDao

class CuratorPublisher:
    def __init__(self, feed_url):
        self.url = feed_url

    def publish_feed_to_s3(self, content):
        bucket = self.__get_bucket()
        k = Key(bucket)
        k.key = self.url
        k.set_contents_from_string(content,headers={'Content-Type': 'application/rss+xml'})
        k.set_acl('public-read')
        feed_url = k.generate_url(0, query_auth=False, force_http=True)
        print "Your RSS Subscription is available at:\n%s" % feed_url

    def __get_bucket(self):
        if not boto.config.has_section('Credentials'):
            raise Exception("Boto configuration not found! Cannot Continue.")
        s3 = boto.connect_s3()
        return s3.create_bucket(self.__get_bucket_name())

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
