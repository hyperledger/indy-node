import importlib
import time
import os

from indy_node.__metadata__ import __version__ as node_pgk_version
from plenum.server.validator_info_tool import none_on_fail, \
    ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool
from plenum.common.constants import POOL_LEDGER_ID, DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        ts_str = "{}".format(time.strftime(
            "%A, %B %{0}d, %Y %{0}I:%M:%S %p %z".format('#' if os.name == 'nt' else '-'),
            time.localtime(info["timestamp"])))
        info.update({"Update time": ts_str})
        if 'Node_info' in info:
            if 'Metrics' in info['Node_info']:
                std_ledgers = [POOL_LEDGER_ID, DOMAIN_LEDGER_ID, CONFIG_LEDGER_ID]
                other_ledgers = {}
                for idx, linfo in self._node.ledgerManager.ledgerRegistry.items():
                    if linfo.id in std_ledgers:
                        continue
                    other_ledgers[linfo.id] = linfo.ledger.size
                info['Node_info']['Metrics']['transaction-count'].update(other_ledgers)

        return info

    @none_on_fail
    def _generate_software_info(self):
        sfv = super()._generate_software_info()
        sfv['Software'].update({'indy-node': self.__node_pkg_version})
        sfv['Software'].update({'sovrin': "unknown"})
        try:
            pkg = importlib.import_module(self._config.UPGRADE_ENTRY)
            sfv['Software'].update({self._config.UPGRADE_ENTRY: pkg.__version__})
        except Exception:
            pass

        return sfv

    @property
    @none_on_fail
    def __node_pkg_version(self):
        return node_pgk_version
