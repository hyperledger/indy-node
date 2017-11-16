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

from storage.kv_store import KeyValueStorage


class AttributeStore:
    """
    Stores attributes as key value pair where the key is hash of the
    attribute as stored in ledger and value is the actual value if the attribute
    """

    def __init__(self, keyValueStorage: KeyValueStorage):
        self._keyValueStorage = keyValueStorage

    def set(self, key, value):
        self._keyValueStorage.put(key, value)

    def get(self, key):
        val = self._keyValueStorage.get(key)
        return val.decode()

    def remove(self, key):
        self._keyValueStorage.remove(key)

    def close(self):
        self._keyValueStorage.close()
