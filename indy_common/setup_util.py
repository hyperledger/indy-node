import glob
import os
from shutil import copyfile, copy2

from ledger.genesis_txn.genesis_txn_file_util import genesis_txn_file

from indy_common.constants import Environment


class Setup:

    def __init__(self, basedir):
        self.base_dir = basedir

    def setupCommon(self):
        self.setupTxns("poolLedger")

    def setupNode(self):
        self.setupTxns("domainLedger")

    def setupClient(self):
        self.setupSampleInvites()

    def setupTxns(self, key, force: bool = False):
        """
        Create base transactions

        :param key: ledger
        :param force: replace existing transaction files
        """
        import data
        dataDir = os.path.dirname(data.__file__)

        # TODO: Need to get "test" and "live" from ENVS property in config.py
        # but that gives error due to some dependency issue
        allEnvs = {
            "local": Environment("pool_transactions_local",
                                 "domain_transactions_local"),
            "test": Environment("pool_transactions_sandbox",
                                "domain_transactions_sandbox"),
            "live": Environment("pool_transactions_live",
                                "domain_transactions_live")
        }
        for env in allEnvs.values():
            fileName = getattr(env, key, None)
            if not fileName:
                continue
            sourceFilePath = os.path.join(dataDir, fileName)
            if not os.path.exists(sourceFilePath):
                continue
            destFilePath = os.path.join(
                self.base_dir, genesis_txn_file(fileName))
            if os.path.exists(destFilePath) and not force:
                continue
            copyfile(sourceFilePath, destFilePath)

        return self

    def setupSampleInvites(self):
        import sample
        sdir = os.path.dirname(sample.__file__)
        sidir = os.path.join(self.base_dir, "sample")
        os.makedirs(sidir, exist_ok=True)
        files = glob.iglob(os.path.join(sdir, "*.indy"))
        for file in files:
            if os.path.isfile(file):
                copy2(file, sidir)
        return self
