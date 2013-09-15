from curator import Curator
from mock import Mock, patch

TEST_URL = 'http://test.com/rss'
curator = Curator(TEST_URL)

def test_add_entry_for_unique_url():
    curator = Curator(TEST_URL)
    dao_mock = Mock()
    dao_mock.entry_visited = Mock(return_value=None) 
    curator.dao = dao_mock
    entry = {'link' : TEST_URL}
    curator._Curator__add_entry_if_unique(entry)
    assert len(curator.entries_to_keep) == 1
    assert curator.entries_to_keep[0] == entry

def test_entry_is_unique_when_dao_says_so():
    curator = Curator(TEST_URL)
    curator.dao = Mock()
    curator.dao.entry_visited = Mock(return_value=None)
    assert curator._Curator__is_entry_unique(TEST_URL) == True

def test_cleanup_link_with_trailing_slash():
    assert curator._Curator__cleanup_link_url(TEST_URL + '/') == TEST_URL 

def test_cleanup_link_with_no_trailing_slash():
    assert curator._Curator__cleanup_link_url(TEST_URL) == TEST_URL 

def test_cleanup_link_with_bad_url():
    assert curator._Curator__cleanup_link_url('') == ''


