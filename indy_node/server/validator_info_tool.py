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

import importlib

from indy_node.__metadata__ import __version__ as node_pgk_version
from plenum.server.validator_info_tool import none_on_fail, \
    ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        info['metrics']['transaction-count'].update(
            config=self.__config_ledger_size
        )
        info.update(
            software={
                'indy-node': self.__node_pkg_version,
                'sovrin': self.__sovrin_pkg_version,
            }
        )
        return info

    @property
    @none_on_fail
    def __config_ledger_size(self):
        return self._node.configLedger.size

    @property
    @none_on_fail
    def __node_pkg_version(self):
        return node_pgk_version

    @property
    @none_on_fail
    def __sovrin_pkg_version(self):
        return importlib.import_module('sovrin').__version__
