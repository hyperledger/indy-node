# #! /usr/bin/env python3
#
# import pytest
# import os
# import shutil
#
# import indy_client.test.cli.test_tutorial as testTutorialMod
# import indy_client.test.cli.conftest as cliConftestMod
#
# curDirPath = os.path.dirname(os.path.abspath(__file__))
# pathForPoolTxnFile = '/home/rkalaria/.indy/pool_transactions_sandbox'
#
#
# # default/common monkeypatching required for any env
# def performDefaultMonkeyPatching(config, monkeypatch):
#
#     @pytest.fixture(scope="module")
#     def mockedAgentIpAddress():
#         return config.get("agentIpAddress")
#
#     @pytest.fixture(scope="module")
#     def mockedFaberAgentPort():
#         return config.get("faberAgentPort")
#
#     @pytest.fixture(scope="module")
#     def mockedAcmeAgentPort():
#         return config.get("acmeAgentPort")
#
#     @pytest.fixture(scope="module")
#     def mockedThriftAgentPort():
#         return config.get("thriftAgentPort")
#
#     @pytest.fixture(scope="module")
#     def mockedPoolNodesStarted(tdir, tconf):
#         source = os.path.join(config.get("poolTxnFilePath"))
#         target = os.path.join(tdir, tconf.poolTransactionsFile)
#         os.mkdir(tdir)
#         if os.path.exists(target):
#             os.remove(target)
#         shutil.copy2(source, target)
#
#     @pytest.fixture(scope="module")
#     def mockedTdirWithPoolTxns(tdir):
#         return tdir
#
#     @pytest.fixture(scope="module")
#     def mockedTdirWithDomainTxns(tdir):
#         return None
#
#     @pytest.fixture(scope="module")
#     def mockedPreRequisite(poolNodesStarted):
#         pass
#
#     monkeypatch.setattr(cliConftestMod, 'tdirWithPoolTxns',
#                         mockedTdirWithPoolTxns)
#
#     monkeypatch.setattr(cliConftestMod, 'tdirWithDomainTxns',
#                         mockedTdirWithDomainTxns)
#
#     monkeypatch.setattr(cliConftestMod, 'poolNodesStarted',
#                         mockedPoolNodesStarted)
#
#     monkeypatch.setattr(testTutorialMod, 'preRequisite',
#                         mockedPreRequisite)
#
#     monkeypatch.setattr(cliConftestMod, 'agentIpAddress',
#                         mockedAgentIpAddress)
#     monkeypatch.setattr(cliConftestMod, 'faberAgentPort',
#                         mockedFaberAgentPort)
#     monkeypatch.setattr(cliConftestMod, 'acmeAgentPort',
#                         mockedAcmeAgentPort)
#     monkeypatch.setattr(cliConftestMod, 'thriftAgentPort',
#                         mockedThriftAgentPort)
#
#
# # define test specific monkey patching
# def tutorialMonkeyPatching(config, monkeypatch):
#     pass
#
#
# # define env specific test config
# sandboxConfig = {
#     "poolTxnFilePath": "/home/rkalaria/.indy/pool_transactions_sandbox",
#     "testModulePaths": {
#         'cli/test_tutorial.py': tutorialMonkeyPatching
#     },
#     "agentIpAddress": "127.0.0.1",
#     "faberAgentPort": "5555",
#     "acmeAgentPort": "6666",
#     "thriftAgentPort": "7777",
# }
#
#
# # add all different env configs to this one config against which
# # you want to run specific tests
#
# envConfigs = {
#     "sandbox": sandboxConfig
# }
#
# # TODO: Need to properly test this and make sure monkey patching
# # doesn't break any other tests (which run after this one)
# def testSpecificModTest(monkeypatch):
#     envExitCodes = {}
#     curDirPath = os.path.dirname(os.path.abspath(__file__))
#
#     for ename, econf in envConfigs.items():
#         testModulePaths = econf.get("testModulePaths")
#         performDefaultMonkeyPatching(econf, monkeypatch)
#         exitCodes = {}
#         for testModName, testMonkeyPatchFunc in testModulePaths.items():
#             testModulePath = os.path.join(
#                 curDirPath, '../indy_client/test', testModName)
#             if testMonkeyPatchFunc:
#                 testMonkeyPatchFunc(econf, monkeypatch)
#             exitCodes[testModName] = pytest.main(['-s', testModulePath])
#
#         envExitCodes[ename] = exitCodes
#
#     for ename, exitCodes in envExitCodes.items():
#         for testMod, testResult in exitCodes.items():
#             assert testResult == 0
