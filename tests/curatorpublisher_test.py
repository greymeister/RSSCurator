import re

from curatorpublisher import CuratorPublisher
from mock import patch, Mock
from sets import Set

TEST_URL = 'http://test.com/rss'

# Bucket restictions are from this source:
# http://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
# Test 100 or so... more users than I expect 
def test_bucket_names():
    curator_publisher = CuratorPublisher(TEST_URL) 
    bucket_set = Set([]) 
    for i in range (0, 100):
        bucket_name = get_bucket_name(curator_publisher)
        yield bucket_name_bigger_than_3, bucket_name
        yield bucket_name_smaller_than_63, bucket_name
        yield bucket_name_uniqueish, bucket_name, bucket_set
        yield bucket_name_starts_with_letter_or_digit, bucket_name
        yield bucket_name_ends_with_letter_or_digit, bucket_name
        yield bucket_name_has_no_dots, bucket_name
        bucket_set.add(bucket_name)

def bucket_name_bigger_than_3(name):
    assert len(name) > 3

def bucket_name_smaller_than_63(name):
    assert len(name) < 63

def bucket_name_uniqueish(name, set):
    assert name not in set

def bucket_name_starts_with_letter_or_digit(name):
    assert re.match('^[A-Za-z0-9]', name) is not None

def bucket_name_ends_with_letter_or_digit(name):
    assert re.match('.*[A-Za-z0-9]$', name) is not None

def bucket_name_has_no_dots(name):
    assert re.match('\.', name) is None

def get_bucket_name(curator_publisher):
    return curator_publisher._CuratorPublisher__generate_bucket_name()
