from plenum.common.util import get_utc_epoch
from storage.kv_in_memory import KeyValueStorageInMemory
from indy_node.persistence.idr_cache import IdrCache

identifier = "fake_identifier"
committed_items = (0,   # seq_no
                   get_utc_epoch(), # txn_time
                   "committed_ta_value",
                   "committed_role_value",
                   "committed_verkey_value",)
uncommitted_items = (1,
                     get_utc_epoch(), # txn_time
                     "uncommitted_ta_value",
                     "uncommitted_role_value",
                     "uncommitted_verkey_value",)


def make_idr_cache():
    kvs = KeyValueStorageInMemory()
    cache = IdrCache("TestCache", kvs)
    return cache


def test_committed():
    """
    Check that it is possible to set and get committed items
    """
    cache = make_idr_cache()
    cache.set(identifier, *committed_items)
    real_items = cache.get(identifier)
    assert committed_items == real_items
    real_items = cache.get(identifier, isCommitted=False)
    assert committed_items == real_items


def test_uncommitted():
    """
    Check that it is possible to set and get uncommitted items
    """
    cache = make_idr_cache()
    cache.set(identifier, *uncommitted_items, isCommitted=False)
    real_items = cache.get(identifier, isCommitted=False)
    assert uncommitted_items == real_items


def test_committed_and_uncommitted():
    """
    Check that uncommitted and committed can present together
    """
    cache = make_idr_cache()
    cache.set(identifier, *committed_items, isCommitted=True)
    cache.set(identifier, *uncommitted_items, isCommitted=False)
    assert uncommitted_items == cache.get(identifier, isCommitted=False)
    assert committed_items == cache.get(identifier, isCommitted=True)
