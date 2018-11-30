import importlib

from indy_node.__metadata__ import __version__ as node_pgk_version
from plenum.server.validator_info_tool import none_on_fail, \
    ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool
from plenum.common.constants import POOL_LEDGER_ID, DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        if 'Node_info' in info:
            if 'Metrics' in info['Node_info']:
                info['Node_info']['Metrics']['transaction-count'].update(config=self.__config_ledger_size)
                std_ledgers = [POOL_LEDGER_ID, DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID]
                other_ledgers = {}
                for idx, linfo in self._node.ledgerManager.ledgerRegistry.items():
                    if linfo.id in std_ledgers:
                        continue
                    other_ledgers[linfo.id] = linfo.ledger.size
                info['Node_info']['Metrics']['transaction-count'].update(other_ledgers)

        return info

    @property
    @none_on_fail
    def software_info(self):
        info = super().software_info
        if 'Software' in info:
            info['Software'].update({'indy-node': self.__node_pkg_version})
            try:
                pkg = importlib.import_module(self._config.UPGRADE_ENTRY)
                info['Software'].update({self._config.UPGRADE_ENTRY: pkg.__version__})
            except Exception:
                pass
        return info

    @property
    @none_on_fail
    def __config_ledger_size(self):
        return self._node.configLedger.size

    @property
    @none_on_fail
    def __node_pkg_version(self):
        return node_pgk_version
