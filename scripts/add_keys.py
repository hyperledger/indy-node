#! /usr/bin/env python3

"""
This script registers new sponsor (client key)
To add new key you need to use existing Steward and its seed
"""

import sys
from itertools import groupby

from plenum.common.looper import Looper
from plenum.common.signer_simple import SimpleSigner
from plenum.common.types import HA
from plenum.common.log import getlogger
from plenum.test.helper import eventually, eventuallyAll

from sovrin_common.config_util import getConfig
from  sovrin_common.txn import SPONSOR
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet



logger = getlogger()

# loading cluster configuration
config = getConfig()

requestTTL = 10  # seconds

# load test configuration
assert len(sys.argv) >= 3

stewardName = sys.argv[1]
stewardSeed = str.encode(sys.argv[2])
sponsorsSeeds = sys.argv[3:]

def spawnClient(clientName, port, signerSeed, host='0.0.0.0'):
    clientAddress = HA(host, port)
    # from plenum.client.request_id_store import FileRequestIdStore
    # walletFilePath = os.path.join(config.baseDir, "wallet")
    # print("Storing request ids in {}".format(walletFilePath))
    # store = FileRequestIdStore(walletFilePath)
    # wallet = Wallet(clientName, store)
    wallet = Wallet(clientName)
    wallet.addIdentifier(signer=SimpleSigner(seed=signerSeed))
    client = Client(clientName, ha=clientAddress)
    return client, wallet


async def checkReply(client, requestId):
    _, status = client.getReply(requestId)
    logger.debug("Number of received messages {}".format(len(client.inBox)))
    groups = groupby(client.inBox, key=lambda x: x[0])
    for key, group in groups:
        logger.debug("Group {}".format(key['op']))
        for msg in list(group):
            logger.debug("  {}".format(msg))
    succeeded = status == "CONFIRMED"
    return succeeded


async def doRequesting(client, wallet, op):
    signedOp = wallet.signOp(op)
    logger.debug("Client {} sending request {}".format(client, op))
    request = client.submitReqs(signedOp)[0]
    requestId = request.reqId
    args = [client, requestId]
    await eventually(checkReply, *args, timeout=requestTTL)


def checkIfConnectedToAll(client):
    connectedNodes = client.nodestack.connecteds
    connectedNodesNum = len(connectedNodes)
    totalNodes = len(client.nodeReg)
    logger.debug("Connected {} / {} nodes".format(connectedNodesNum, totalNodes))
    for node in connectedNodes:
        logger.debug("  {}".format(node))

    if connectedNodesNum == 0:
        raise Exception("Not connected to any")
    elif connectedNodesNum < totalNodes * 0.8:
        raise Exception("Not connected fully")
    else:
        return True


async def ensureConnectedToNodes(client):
    wait = 5
    logger.debug("waiting for {} seconds to check client connections to nodes...".format(wait))
    await eventuallyAll(lambda : checkIfConnectedToAll(client), retryWait=.5, totalTimeout=wait)


def clearRaetData():
    import glob
    import os.path
    import shutil

    sovrin_path = os.path.join(os.path.expanduser("~"), '.sovrin')
    sovrin_steward_path = os.path.join(sovrin_path, 'Steward*')
    sovrin_sponsor_path = os.path.join(sovrin_path, 'Sponsor*')
    for path in glob.glob(sovrin_steward_path) + glob.glob(sovrin_sponsor_path):
        try:
            shutil.rmtree(path)
            logger.warn("'%s' was deleted because the "
                        "'PacketError: Failed verification.' issue", path)
        except FileNotFoundError:
            pass


def addNyms():
    # clearRaetData()

    with Looper(debug=True) as looper:

        from sovrin_client.test.helper import createNym

        # Starting clients
        print("Spawning client")
        client, wallet = spawnClient(stewardName, 5678, stewardSeed)
        client.registerObserver(wallet.handleIncomingReply)
        print("Adding it to looper")
        looper.add(client)
        print("Running it")
        looper.run(ensureConnectedToNodes(client))

        # Creating request
        print("Creating request")
        for sponsorSeed in sponsorsSeeds:
            signer = SimpleSigner(seed=sponsorSeed.encode())
            nym = signer.identifier
            verkey = signer.verkey
            # Sending requests
            print("Creating nym {} for seed".format(nym , sponsorSeed))
            createNym(looper=looper, nym=nym, creatorClient=client,
                      creatorWallet=wallet, verkey=verkey, role=SPONSOR)


if __name__ == '__main__':
    addNyms()
