from operator import itemgetter
from indy_common.util import getIndex


def test_getIndex():
    items = [('a', {'key1': 1}), ('b', {'key2': 2})]
    getDict = itemgetter(1)

    def containsKey(key):
        return lambda x: key in getDict(x)

    assert 0 == getIndex(containsKey('key1'), items)
    assert 1 == getIndex(containsKey('key2'), items)
    assert -1 == getIndex(containsKey('key3'), items)
