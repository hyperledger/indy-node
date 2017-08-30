from plenum.server.validator_info_tool import none_on_fail, \
    ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        info['metrics']['transaction-count'].update(
            config=self.__config_ledger_size
        )
        return info

    @property
    @none_on_fail
    def __config_ledger_size(self):
        return self._node.configLedger.size
