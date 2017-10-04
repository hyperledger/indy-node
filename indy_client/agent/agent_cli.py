from indy_client.cli.cli import IndyCli


class AgentCli(IndyCli):
    def __init__(self, name=None, agentCreator=None, *args, **kwargs):
        if name is not None:
            self.name = name

        init_agent = kwargs.get('agent', None)
        if 'agent' in kwargs:
            kwargs.pop('agent')

        super().__init__(*args, **kwargs)

        self._activeWallet = None

        if init_agent is not None:
            self.agent = init_agent
            if name is None:
                self.name = init_agent.name

    @property
    def actions(self):
        if not self._actions:
            self._actions = [self._simpleAction, self._helpAction,
                             self._listIdsAction, self._changePrompt,
                             self._listWalletsAction, self._showFile,
                             self._showConnection, self._pingTarget,
                             self._listConnections, self._sendProofRequest]
        return self._actions

    def getKeyringsBaseDir(self):
        return self.agent.getContextDir()

    def getContextBasedKeyringsBaseDir(self):
        return self.agent.getContextDir()

    def getAllSubDirNamesForKeyrings(self):
        return ["issuer"]

    def getTopComdMappingKeysForHelp(self):
        return ['helpAction']

    def getComdMappingKeysToNotShowInHelp(self):
        allowedCmds = [func.__name__.replace("_", "") for func in self.actions]
        return {k: v for (k, v) in
                self.cmdHandlerToCmdMappings().items() if k not in allowedCmds}

    def getBottomComdMappingKeysForHelp(self):
        return ['licenseAction', 'exitAction']

    def restoreLastActiveWallet(self):
        pass

    def _saveActiveWallet(self):
        pass

    def printSuggestion(self, msgs):
        self.print("\n")
        # TODO: as of now we are not printing the suggestion (msg)
        # because, those suggestion may not be intented or may not work
        # correctly for agents, so when such requirement will come,
        # we can look this again.

    @property
    def activeWallet(self):
        return self.agent._wallet

    @activeWallet.setter
    def activeWallet(self, wallet):
        pass

    @property
    def walletSaver(self):
        return self.agent.walletSaver
