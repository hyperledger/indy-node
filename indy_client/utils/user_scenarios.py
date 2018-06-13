import json
import random
from abc import abstractmethod, ABCMeta
from collections import namedtuple
from functools import partial

from stp_core.common.log import getlogger, Logger
from stp_core.crypto.util import randomSeed
from stp_core.loop.eventually import eventually
from stp_core.loop.looper import Looper
from stp_core.network.port_dispenser import genHa
from stp_core.types import HA

from plenum.common.constants import TXN_TYPE, TARGET_NYM, VERKEY, DATA
from plenum.common.signer_simple import SimpleSigner
from indy_client.client.client import Client
from indy_client.client.wallet.wallet import Wallet
from indy_common.constants import NYM, GET_NYM
from indy_common.config_util import getConfig
from indy_common.util import get_reply_if_confirmed

logger = getlogger()


class UserScenario(metaclass=ABCMeta):
    def __init__(self, seed, logFileName=None):
        if logFileName:
            Logger().enableFileLogging(logFileName)

        self._seed = seed

        self._client = None
        self._wallet = None

        self._looper = None

    @property
    def identifier(self):
        if self._wallet:
            return self._wallet.defaultId
        else:
            return None

    @property
    def verkey(self):
        if self._wallet:
            return self._wallet.getVerkey()
        else:
            return None

    @classmethod
    def runInstance(cls, *args, **kwargs):
        cls(*args, **kwargs).run()

    def run(self):
        try:
            self._createClientAndWallet()

            self._looper = Looper(debug=getConfig().LOOPER_DEBUG)
            try:
                self._startClient()
                self.do()
            finally:
                self._looper.shutdownSync()
                self._looper = None

        except BaseException as ex:
            logger.exception(
                "User scenario throws out exception: {}".format(ex),
                exc_info=ex)
            raise ex

    @abstractmethod
    def do(self):
        pass

    def performOperation(self, op):
        req = self._wallet.signOp(op)
        self._client.submitReqs(req)

        def getRequestResult(reqKey):
            reply, error = get_reply_if_confirmed(self._client, *reqKey)
            if reply is None and error is None:
                raise Exception("Request has not been completed yet")
            else:
                return reply, error

        reply, error = self._looper.run(eventually(partial(getRequestResult,
                                                           (req.identifier,
                                                            req.reqId)),
                                                   retryWait=.5,
                                                   timeout=5))
        assert not error, error

        if reply[DATA]:
            result = json.loads(reply[DATA])
        else:
            result = None

        return result

    def generateNewSigner(self):
        assert self.identifier
        return SimpleSigner(identifier=self.identifier)

    def changeSigner(self, newSigner):
        assert newSigner.identifier == self.identifier
        self._wallet.updateSigner(self.identifier, newSigner)
        logger.info("Changed signer. New verkey: {}".format(self.verkey))

    def _createClientAndWallet(self):
        signer = SimpleSigner(seed=self._seed)

        port = genHa()[1]
        ha = HA('0.0.0.0', port)
        self._client = Client(name=signer.identifier, ha=ha)

        self._wallet = Wallet(name=signer.identifier)
        self._wallet.addIdentifier(signer=signer)

        logger.info("Identifier: {}".format(self.identifier))
        logger.info("Signer's verkey: {}".format(self.verkey))

    def _startClient(self):
        self._looper.add(self._client)

        def ensureConnectedToAll():
            connectedNodes = self._client.nodestack.connecteds
            connectedNodesNum = len(connectedNodes)
            totalNodes = len(self._client.nodeReg)

            logger.info(
                "Connected {} / {} nodes".format(connectedNodesNum, totalNodes))
            for node in connectedNodes:
                logger.info("  {}".format(node))

            if connectedNodesNum == 0:
                raise Exception("Not connected to any")
            elif connectedNodesNum < totalNodes * 0.8:
                raise Exception("Not connected fully")
            else:
                return True

        self._looper.run(eventually(ensureConnectedToAll,
                                    retryWait=.5,
                                    timeout=5))


class NymsCreationScenario(UserScenario):
    def __init__(self, seed, nymsIdsAndVerkeys, logFileName=None):
        super().__init__(seed, logFileName)
        self.nymsIdsAndVerkeys = nymsIdsAndVerkeys

    def do(self):
        for id, verkey in self.nymsIdsAndVerkeys:
            self.setNym(id, verkey)

    def setNym(self, dest, verkey):
        logger.info("Setting nym: dest={}, verkey={}...".format(dest, verkey))
        self.performOperation({
            TXN_TYPE: NYM,
            TARGET_NYM: dest,
            VERKEY: verkey
        })
        logger.info("Nym set")


class KeyRotationAndReadScenario(UserScenario):
    def __init__(self, seed, iterations, logFileName=None):
        super().__init__(seed, logFileName)
        self.iterations = iterations

    def do(self):
        for i in range(self.iterations):
            newSigner = self.generateNewSigner()
            self.setMyVerkey(newSigner.verkey)
            newVerkey = self.getMyVerkey()

            assert newVerkey == newSigner.verkey, \
                "Got wrong verkey: expected was {}, actual was {}".format(
                    newSigner.verkey, newVerkey)

            self.changeSigner(newSigner)

    def setMyVerkey(self, verkey):
        logger.info("Setting my verkey to {}...".format(verkey))
        self.performOperation({
            TXN_TYPE: NYM,
            TARGET_NYM: self.identifier,
            VERKEY: verkey
        })
        logger.info("Verkey set")

    def getMyVerkey(self):
        logger.info("Getting my verkey...")
        result = self.performOperation({
            TXN_TYPE: GET_NYM,
            TARGET_NYM: self.identifier
        })
        logger.info("Verkey gotten: {}".format(result[VERKEY]))
        return result[VERKEY]


class KeyRotationScenario(UserScenario):
    def __init__(self, seed, iterations, logFileName=None):
        super().__init__(seed, logFileName)
        self.iterations = iterations

    def do(self):
        for i in range(self.iterations):
            newSigner = self.generateNewSigner()
            self.setMyVerkey(newSigner.verkey)
            self.changeSigner(newSigner)

    def setMyVerkey(self, verkey):
        logger.info("Setting my verkey to {}...".format(verkey))
        self.performOperation({
            TXN_TYPE: NYM,
            TARGET_NYM: self.identifier,
            VERKEY: verkey
        })
        logger.info("Verkey set")


class ForeignKeysReadScenario(UserScenario):
    def __init__(self, seed, nymsIds, iterations, logFileName=None):
        super().__init__(seed, logFileName)
        self.nymsIds = nymsIds
        self.iterations = iterations

    def do(self):
        for i in range(self.iterations):
            id = random.choice(self.nymsIds)
            self.getVerkey(id)
            # TODO: Add an assertion verifying that the gotten verkey is
            # from the expected section of the nym's verkey values history

    def getVerkey(self, dest):
        logger.info("Getting verkey of NYM {}...".format(dest))
        result = self.performOperation({
            TXN_TYPE: GET_NYM,
            TARGET_NYM: dest
        })
        logger.info("Verkey gotten: {}".format(result[VERKEY]))
        return result[VERKEY]


def generateNymsData(count):
    signers = [SimpleSigner(seed=randomSeed()) for i in range(count)]
    Nym = namedtuple("Nym", ["seed", "identifier", "verkey"])
    return [Nym(signer.seed, signer.identifier, signer.verkey)
            for signer in signers]
