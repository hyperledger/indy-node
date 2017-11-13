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
