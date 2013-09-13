from curator import Curator
from mock import Mock

TEST_URL = 'http://test.com/rss'
curator = Curator(TEST_URL)

def test_cleanup_link_with_trailing_slash():
    assert curator._Curator__cleanup_link_url(TEST_URL + '/') == TEST_URL 

def test_cleanup_link_with_no_trailing_slash():
    assert curator._Curator__cleanup_link_url(TEST_URL) == TEST_URL 

def test_cleanup_link_with_bad_url():
    assert curator._Curator__cleanup_link_url('') == ''


