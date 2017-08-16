#! /usr/bin/env python3

"""
This script registers new trust anchors (client keys)
To add new key you need to use existing Steward and it's seed
"""

import os
import sys
from itertools import groupby

from stp_core.loop.looper import Looper
from plenum.common.signer_did import DidSigner
from plenum.common.types import HA
from stp_core.common.log import getlogger
from plenum.test.helper import eventually, eventuallyAll

from sovrin_common.config_util import getConfig
from sovrin_common.constants import TRUST_ANCHOR
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
trustAnchorSeeds = sys.argv[3:]

if not trustAnchorSeeds:
    seed_file_path = "{}/load_test_clients.list".format(os.getcwd())
    trustAnchorSeeds = []
    with open(seed_file_path, "r") as file:
        trustAnchorSeeds = [line.strip().split(":")[1] for line in file]


def spawnClient(clientName, port, signerSeed, host='0.0.0.0'):
    clientAddress = HA(host, port)
    # from plenum.client.request_id_store import FileRequestIdStore
    # walletFilePath = os.path.join(config.baseDir, "wallet")
    # print("Storing request ids in {}".format(walletFilePath))
    # store = FileRequestIdStore(walletFilePath)
    # wallet = Wallet(clientName, store)
    wallet = Wallet(clientName)
    wallet.addIdentifier(signer=DidSigner(seed=signerSeed))
    client = Client(clientName, ha=clientAddress)
    return client, wallet


async def checkReply(client, requestId):
    _, status = client.getReply(requestId)
    logger.info("Number of received messages {}".format(len(client.inBox)))
    groups = groupby(client.inBox, key=lambda x: x[0])
    for key, group in groups:
        logger.info("Group {}".format(key['op']))
        for msg in list(group):
            logger.info("  {}".format(msg))
    succeeded = status == "CONFIRMED"
    return succeeded


async def doRequesting(client, wallet, op):
    signedOp = wallet.signOp(op)
    logger.info("Client {} sending request {}".format(client, op))
    request = client.submitReqs(signedOp)[0][0]
    requestId = request.reqId
    args = [client, requestId]
    await eventually(checkReply, *args, timeout=requestTTL)


def checkIfConnectedToAll(client):
    connectedNodes = client.nodestack.connecteds
    connectedNodesNum = len(connectedNodes)
    totalNodes = len(client.nodeReg)
    logger.info("Connected {} / {} nodes".format(connectedNodesNum, totalNodes))
    for node in connectedNodes:
        logger.info("  {}".format(node))

    if connectedNodesNum == 0:
        raise Exception("Not connected to any")
    elif connectedNodesNum < totalNodes * 0.8:
        raise Exception("Not connected fully")
    else:
        return True


async def ensureConnectedToNodes(client):
    wait = 5
    logger.info("waiting for {} seconds to check client connections to nodes...".format(wait))
    await eventuallyAll(lambda : checkIfConnectedToAll(client), retryWait=.5, totalTimeout=wait)


def addNyms():
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
        bad = []
        for seed in trustAnchorSeeds:
            signer = DidSigner(seed=seed.encode())
            nym = signer.identifier
            verkey = signer.verkey
            # Sending requests
            print("Creating nym for seed {}".format(seed))
            try:
                createNym(looper=looper, nym=nym, creatorClient=client,
                          creatorWallet=wallet, verkey=verkey, role=TRUST_ANCHOR)
                print("Successfully created nym for {}".format(seed))
            except Exception as ex:
                bad.append(seed)
                print("Failed to create nym for {}".format(seed))


        print("=======================")
        if not bad:
            print("All nyms created successfully")
        else:
            print("Failed to created nyms for:")
            for nym in bad:
                print("-", nym)
        print("=======================")


if __name__ == '__main__':
    addNyms()
