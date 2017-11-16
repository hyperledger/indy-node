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

# Some unit tests for upgrader
from indy_node.server.upgrader import Upgrader


def comparator_test(lower_versrion, higher_version):
    assert Upgrader.compareVersions(lower_versrion, higher_version) == 1
    assert Upgrader.compareVersions(higher_version, lower_versrion) == -1
    assert Upgrader.compareVersions(higher_version, higher_version) == 0
    assert not Upgrader.is_version_upgradable(higher_version, higher_version)
    assert Upgrader.is_version_upgradable(
        higher_version, higher_version, reinstall=True)
    assert Upgrader.is_version_upgradable(lower_versrion, higher_version)
    assert not Upgrader.is_version_upgradable(higher_version, lower_versrion)


def test_versions():
    comparator_test('0.0.5', '0.0.6')
    comparator_test('0.1.2', '0.2.6')
    comparator_test('1.10.2', '2.0.6')
