import importlib

from indy_node.__metadata__ import __version__ as node_pgk_version
from plenum.server.validator_info_tool import none_on_fail, \
    ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        if 'Node_info' in info:
            if 'Metrics' in info['Node_info']:
                info['Node_info']['Metrics']['transaction-count'].update(
                    config=self.__config_ledger_size
                )
        return info

    @property
    @none_on_fail
    def software_info(self):
        info = super().software_info
        if 'Software' in info:
            info['Software'].update({'indy-node': self.__node_pkg_version})
        return info

    @property
    @none_on_fail
    def __config_ledger_size(self):
        return self._node.configLedger.size

    @property
    @none_on_fail
    def __node_pkg_version(self):
        return node_pgk_version
