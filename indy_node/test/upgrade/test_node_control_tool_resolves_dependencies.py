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

import multiprocessing
from indy_node.utils.node_control_tool import NodeControlTool
from plenum.test.helper import randomText


m = multiprocessing.Manager()
whitelist = ['Unexpected error in _upgrade test']

def testNodeControlResolvesDependencies(monkeypatch):
    nct = NodeControlTool()
    node_package = ('indy-node', '0.0.1')
    anoncreds_package = ('indy-anoncreds', '0.0.2')
    plenum_package = ('indy-plenum', '0.0.3')
    node_package_with_version = '{}={}'.format(*node_package)
    plenum_package_with_version = '{}={}'.format(*plenum_package)
    anoncreds_package_with_version = '{}={}'.format(*anoncreds_package)
    mock_info = {
        node_package_with_version: '{}{} (= {}){}{} (= {}){}'.format(
            randomText(100),
            *plenum_package,
            randomText(100),
            *anoncreds_package,
            randomText(100)),
        plenum_package_with_version: '{}'.format(
            randomText(100)),
        anoncreds_package_with_version: '{}'.format(
            randomText(100))}

    def mock_get_info_from_package_manager(self, package):
        return mock_info.get(package, None)

    monkeypatch.setattr(nct.__class__, '_get_info_from_package_manager',
                        mock_get_info_from_package_manager)
    monkeypatch.setattr(
        nct.__class__, '_update_package_cache', lambda *x: None)
    ret = nct._get_deps_list(node_package_with_version)
    assert ret.split() == [
        anoncreds_package_with_version,
        plenum_package_with_version,
        node_package_with_version]