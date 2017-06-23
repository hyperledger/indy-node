import argparse
import json
import os
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

logger = getlogger()


class ReadWriteTest:
    def __init__(self, clientNo, numOfRequests):
        self.clientNo = clientNo
        self.numOfRequests = numOfRequests

        self.userName, self.seed = getUserNameAndSeed(self.clientNo)

        self.client = None
        self.wallet = None

        self.looper = None

    def run(self):
        self.initializeClientAndWallet()
        identifier = self.wallet.defaultId

        with Looper(debug=True) as looper:
            self.looper = looper
            self.startClient()

            for r in range(self.numOfRequests):
                newSigner = SimpleSigner(identifier=identifier)
                self.setVerkey(identifier, newSigner.verkey)

                gottenVerkey = self.getVerkey(identifier)
                assert gottenVerkey == newSigner.verkey, \
                    "Got wrong verkey: expected was {}, actual was {}".format(
                        newSigner.verkey, gottenVerkey)

                self.wallet.updateSigner(identifier, newSigner)
                logger.info("Updated signer")

            self.looper = None

    def initializeClientAndWallet(self):
        port = genHa()[1]
        ha = HA('0.0.0.0', port)
        self.client = Client(name=self.userName, ha=ha)

        self.wallet = Wallet(self.userName)
        self.wallet.addIdentifier(signer=SimpleSigner(seed=self.seed))

        logger.info("Identifier: {}".format(self.wallet.defaultId))
        logger.info("Verkey: {}".format(
            self.wallet.getVerkey(self.wallet.defaultId)))

    def startClient(self):
        self.looper.add(self.client)

        def ensureConnectedToAll():
            connectedNodes = self.client.nodestack.connecteds
            connectedNodesNum = len(connectedNodes)
            totalNodes = len(self.client.nodeReg)

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

        self.looper.run(eventually(ensureConnectedToAll,
                                   retryWait=.5,
                                   timeout=5))

    def setVerkey(self, identifier, verkey):
        req = self.wallet.signOp({
            TXN_TYPE: NYM,
            TARGET_NYM: identifier,
            VERKEY: verkey
        })

        logger.info("Setting verkey of NYM {} to {}".format(identifier, verkey))
        reply = self.performRequest(req)
        logger.info("Verkey set")

    def getVerkey(self, identifier):
        req = self.wallet.signOp({
            TXN_TYPE: GET_NYM,
            TARGET_NYM: identifier
        })

        logger.info("Getting verkey of NYM {}".format(identifier))
        reply = self.performRequest(req)
        data = json.loads(reply[DATA])
        verkey = data[VERKEY]
        logger.info("Verkey gotten: {}".format(verkey))

        return verkey

    def performRequest(self, req):
        self.client.submitReqs(req)

        def getRequestResult(reqKey):
            reply, error = self.client.replyIfConsensus(*reqKey)
            if reply is None and error is None:
                raise Exception("Request has not been completed yet")
            else:
                return reply, error

        reply, error = self.looper.run(eventually(partial(getRequestResult,
                                                          req.key),
                                                  retryWait=.5,
                                                  timeout=5))
        assert not error, error
        return reply


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


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--client_no",
                        action="store",
                        type=int,
                        dest="clientNo",
                        help="client number")

    parser.add_argument("-r", "--num_of_requests",
                        action="store",
                        type=int,
                        dest="numOfRequests",
                        help="number of requests")

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArgs()
    ReadWriteTest(args.clientNo, args.numOfRequests).run()
