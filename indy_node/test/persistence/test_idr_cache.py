#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import pytest
from plenum.common.util import get_utc_epoch
from storage.kv_in_memory import KeyValueStorageInMemory
from indy_node.persistence.idr_cache import IdrCache

identifier = "fake_identifier"
committed_items = (0, # seq_no
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
