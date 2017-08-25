from plenum.server.validator_info_tool import ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        info['metrics']['transaction-count'].update(
            config=self.__node.configLedger.size
        )
        return info
