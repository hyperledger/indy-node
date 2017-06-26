import argparse
import json
import os
import random
from abc import abstractmethod, ABCMeta
from collections import namedtuple
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually
from stp_core.loop.looper import Looper
from stp_core.network.port_dispenser import genHa
from stp_core.types import HA

from plenum.common.constants import TXN_TYPE, TARGET_NYM, VERKEY, DATA
from plenum.common.signer_simple import SimpleSigner
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.constants import NYM, GET_NYM

STEWARD1_SEED = b"000000000000000000000000Steward1"

logger = getlogger()


class UserScenario(metaclass=ABCMeta):
    def __init__(self, seed):
        self.seed = seed

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
        self._createClientAndWallet()

        self._looper = Looper(debug=True)
        try:
            self._startClient()
            self.do()
        finally:
            self._looper.shutdownSync()
            self._looper = None

    @abstractmethod
    def do(self):
        pass

    def performOperation(self, op):
        req = self._wallet.signOp(op)
        self._client.submitReqs(req)

        def getRequestResult(reqKey):
            reply, error = self._client.replyIfConsensus(*reqKey)
            if reply is None and error is None:
                raise Exception("Request has not been completed yet")
            else:
                return reply, error

        reply, error = self._looper.run(eventually(partial(getRequestResult,
                                                           req.key),
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
        signer = SimpleSigner(seed=self.seed)

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
    def __init__(self, seed, nymsAndVerkeys):
        super().__init__(seed)
        self.nymsAndVerkeys = nymsAndVerkeys

    def do(self):
        for nym, verkey in self.nymsAndVerkeys:
            self.setNym(nym, verkey)

    def setNym(self, dest, verkey):
        logger.info("Setting nym: dest={}, verkey={}".format(dest, verkey))
        self.performOperation({
            TXN_TYPE: NYM,
            TARGET_NYM: dest,
            VERKEY: verkey
        })
        logger.info("Nym set")


class KeyRotationAndReadScenario(UserScenario):
    def __init__(self, seed, iterations):
        super().__init__(seed)
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
        logger.info("Setting my verkey to {}".format(verkey))
        self.performOperation({
            TXN_TYPE: NYM,
            TARGET_NYM: self.identifier,
            VERKEY: verkey
        })
        logger.info("Verkey set")

    def getMyVerkey(self):
        logger.info("Getting my verkey")
        result = self.performOperation({
            TXN_TYPE: GET_NYM,
            TARGET_NYM: self.identifier
        })
        logger.info("Verkey gotten: {}".format(result[VERKEY]))
        return result[VERKEY]


class KeyRotationScenario(UserScenario):
    def __init__(self, seed, iterations):
        super().__init__(seed)
        self.iterations = iterations

    def do(self):
        for i in range(self.iterations):
            newSigner = self.generateNewSigner()
            self.setMyVerkey(newSigner.verkey)
            self.changeSigner(newSigner)

    def setMyVerkey(self, verkey):
        logger.info("Setting my verkey to {}".format(verkey))
        self.performOperation({
            TXN_TYPE: NYM,
            TARGET_NYM: self.identifier,
            VERKEY: verkey
        })
        logger.info("Verkey set")


class ForeignKeysReadScenario(UserScenario):
    def __init__(self, seed, nyms, iterations):
        super().__init__(seed)
        self.nyms = nyms
        self.iterations = iterations

    def do(self):
        for i in range(self.iterations):
            nym = random.choice(self.nyms)
            self.getVerkey(nym)

    def getVerkey(self, dest):
        logger.info("Getting verkey of NYM {}".format(dest))
        result = self.performOperation({
            TXN_TYPE: GET_NYM,
            TARGET_NYM: dest
        })
        logger.info("Verkey gotten: {}".format(result[VERKEY]))
        return result[VERKEY]


def getUserNameAndSeed(clientNo):
    seedFilePath = "{}/load_test_clients.list".format(os.getcwd())

    with open(seedFilePath, "r") as file:
        for i in range(clientNo - 1):
            next(file)
        name, seedStr = next(file).strip().split(":")
        seed = seedStr.encode()

        logger.info("User name: {}".format(name))
        logger.info("Seed: {}".format(seed))

        return name, seed


def generateNymsData(count):
    signers = [SimpleSigner() for i in range(count)]
    Nym = namedtuple("Nym", ["seed", "identifier", "verkey"])
    return [Nym(signer.seed, signer.identifier, signer.verkey)
            for signer in signers]


def main(args):
    numOfWriters = args.writers
    numOfReaders = args.readers
    numOfIterations = args.iterations

    writers = generateNymsData(numOfWriters)
    readers = generateNymsData(numOfReaders)

    with ProcessPoolExecutor(numOfWriters + numOfReaders) as executor:
        allNymsAndVerkeys = [(nym.identifier, nym.verkey)
                             for nym in writers + readers]

        nymsCreationScenarioFuture = \
            executor.submit(NymsCreationScenario.runInstance,
                            seed=STEWARD1_SEED,
                            nymsAndVerkeys=allNymsAndVerkeys)

        nymsCreationScenarioFuture.result()
        logger.info("Created {} nyms".format(numOfWriters + numOfReaders))

        keyRotationScenariosFutures = \
            [executor.submit(KeyRotationScenario.runInstance,
                             seed=writer.seed,
                             iterations=numOfIterations)
             for writer in writers]

        writersNyms = [writer.identifier for writer in writers]

        foreignKeysReadScenariosFutures = \
            [executor.submit(ForeignKeysReadScenario.runInstance,
                             seed=reader.seed,
                             nyms=writersNyms,
                             iterations=numOfIterations)
             for reader in readers]

        futures.wait(keyRotationScenariosFutures +
                     foreignKeysReadScenariosFutures)

        failed = False
        for future in keyRotationScenariosFutures + \
                foreignKeysReadScenariosFutures:
            ex = future.exception()
            if ex:
                failed = True
                logger.exception(ex)

        if failed:
            logger.info("Some writers or readers failed")
        else:
            logger.info("All writers and readers finished successfully")


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--writers",
                        action="store",
                        type=int,
                        dest="writers",
                        help="number of writers")

    parser.add_argument("-r", "--readers",
                        action="store",
                        type=int,
                        dest="readers",
                        help="number of readers")

    parser.add_argument("-i", "--iterations",
                        action="store",
                        type=int,
                        dest="iterations",
                        help="number of iterations")

    return parser.parse_args()


if __name__ == "__main__":
    main(parseArgs())
