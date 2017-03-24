#! /usr/bin/env python3

import argparse
import asyncio
import os
import time
import csv
import functools
from collections import namedtuple
from random import randint
from jsonpickle import json

from plenum.common.looper import Looper
from plenum.common.log import getlogger
from plenum.common.types import HA
from plenum.common.util import randomString
from plenum.common.port_dispenser import genHa
from plenum.common.signer_simple import SimpleSigner
from plenum.common.txn import \
    TARGET_NYM, TXN_TYPE, NYM, ROLE, RAW, NODE, DATA, \
    ALIAS, CLIENT_IP, CLIENT_PORT

from plenum.test.helper import eventually, eventuallyAll
from plenum.test.test_client import \
    getAcksFromInbox, getNacksFromInbox, getRepliesFromInbox

from sovrin_common.txn import ATTRIB, GET_ATTR
from sovrin_common.config_util import getConfig
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.client.client import Client
from sovrin_common.identity import Identity

logger = getlogger()
config = getConfig()

TTL = 120.0#60.0
CONNECTION_TTL = 30.0
RETRY_WAIT = 0.25


def parseArgs():

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--num_clients",
                        action="store",
                        type=int,
                        default=1,
                        dest="numberOfClients",
                        help="number of clients to use (set to -1 for all)")

    parser.add_argument("-r", "--num_requests",
                        action="store",
                        type=int,
                        default=1,
                        dest="numberOfRequests",
                        help="number of clients to use")

    parser.add_argument("-t", "--request_type",
                        action="store",
                        type=str,
                        default="ATTRIB",
                        dest="requestType",
                        help="type of requests to send, supported = NYM, ATTRIB")

    parser.add_argument("--at-once",
                        action='store_true',
                        dest="atOnce",
                        help="if set client send all request at once")


    parser.add_argument("--timeout",
                        action="store",
                        type=int,
                        default=1,
                        dest="timeoutBetweenRequests",
                        help="number of seconds to sleep after each request")

    parser.add_argument("--clients-list",
                        action="store",
                        default="{}/load_test_clients.list".format(os.getcwd()),
                        dest="clientsListFilePath",
                        help="path to file with list of client names and keys")

    parser.add_argument("--results-path",
                        action="store",
                        default=os.getcwd(),
                        dest="resultsPath",
                        help="output directory")

    parser.add_argument("--skip-clients",
                        action="store",
                        type=int,
                        default=0,
                        dest="numberOfClientsToSkip",
                        help="number of clients to skip from clients list")

    return parser.parse_args()


def createClientAndWalletWithSeed(name, seed, ha=None):
    if isinstance(seed, str):
        seed = seed.encode()
    if not ha:
    # if not ha and not isLocalKeepSetup(name, config.baseDir):
        port = genHa()[1]
        ha = HA('0.0.0.0', port)
    wallet = Wallet(name)
    wallet.addIdentifier(signer=SimpleSigner(seed=seed))
    client = Client(name, ha=ha)
    return client, wallet


class ClientPoll:

    def __init__(self, filePath, limit=-1, skip=0):
        self.__startPort = 5679
        self.__filePath = filePath
        self.__limit = limit
        self.__skip = skip
        self._clientsWallets = [self._spawnClient(name, seed)
                                for name, seed in self._readCredentials()]

    @property
    def clients(self):
        for cli, _ in self._clientsWallets:
            yield cli

    @staticmethod
    def randomRawAttr():
        d = {"{}_{}".format(randomString(20), randint(100, 1000000)): "{}_{}".
            format(randint(1000000, 1000000000000), randomString(50))}
        return json.dumps(d)

    def submitNym(self, reqsPerClient=1):

        usedIdentifiers = set()

        def newSigner():
            while True:
                signer = SimpleSigner()
                idr = signer.identifier
                if idr not in usedIdentifiers:
                    usedIdentifiers.add(idr)
                    return signer

        def makeRequest(cli, wallet):
            signer = newSigner()
            idy = Identity(identifier=signer.identifier,
                           verkey=signer.verkey)

            wallet.addSponsoredIdentity(idy)

        return self.submitGeneric(makeRequest, reqsPerClient)

    def submitSetAttr(self, reqsPerClient=1):

        def makeRequest(cli, wallet):
            attrib = Attribute(name=cli.name,
                               origin=wallet.defaultId,
                               value=self.randomRawAttr(),
                               ledgerStore=LedgerStore.RAW)
            wallet.addAttribute(attrib)

        return self.submitGeneric(makeRequest, reqsPerClient)

    def submitGeneric(self, makeRequest, reqsPerClient):
        corosArgs = []
        for cli, wallet in self._clientsWallets:
            for _ in range(reqsPerClient):
                makeRequest(cli, wallet)
            reqs = wallet.preparePending()
            sentAt = time.time()
            cli.submitReqs(*reqs)
            for req in reqs:
                corosArgs.append([cli, wallet, req, sentAt])
        return corosArgs

    def _readCredentials(self):
        with open(self.__filePath, "r") as file:
            creds = [line.strip().split(":") for i, line in enumerate(file)]
            return map(lambda x: (x[0], str.encode(x[1])), creds[self.__skip:self.__skip+self.__limit])

    def _spawnClient(self, name, seed, host='0.0.0.0'):
        self.__startPort += randint(100, 1000)
        address = HA(host, self.__startPort)
        logger.info("Seed for client {} is {}, "
                    "its len is {}".format(name, seed, len(seed)))
        return createClientAndWalletWithSeed(name, seed, address)


resultsRowFieldNames = ['signerName', 'signerId', 'dest', 'reqId', 'transactionType',
                        'sentAt', 'quorumAt', 'latency', 'ackNodes',
                        'nackNodes', 'replyNodes']
ResultRow = namedtuple('ResultRow', resultsRowFieldNames)


async def eventuallyAny(coroFunc, *args, retryWait: float = 0.01,
                        timeout: float = 5):
    start = time.perf_counter()

    def remaining():
        return start + timeout - time.perf_counter()

    remain = remaining()
    data = None
    while remain >= 0:
        res = await coroFunc(*args)
        (complete, data) = res
        if complete:
            return data
        remain = remaining()
        if remain > 0:
            await asyncio.sleep(retryWait)
            remain = remaining()
    return data


async def checkReply(client, requestId, identifier):
    hasConsensus = False
    acks, nacks, replies, queryTime = [], [], [], 0
    try:
        # acks = client.reqRepStore.getAcks(requestId)
        # nacks = client.reqRepStore.getNacks(requestId)
        # replies = client.reqRepStore.getReplies(requestId)
        nodeCount = len(client.nodeReg)
        acks = getAcksFromInbox(client, requestId, maxm=nodeCount)
        nacks = getNacksFromInbox(client, requestId, maxm=nodeCount)
        replies = getRepliesFromInbox(client, requestId, maxm=nodeCount)
        hasConsensus = client.hasConsensus(identifier, requestId)
        queryTime = sum(map(lambda f:  f.__wrapped__.elapsed,
                               [getAcksFromInbox, getNacksFromInbox,
                                getRepliesFromInbox, client.hasConsensus]))
    except Exception as e:  # TODO: Can be a problem?
        pass
    finally:
        return hasConsensus, (hasConsensus, acks, nacks, replies, queryTime)


async def checkReplyAndLogStat(client, wallet, request, sentAt, writeResultsRow, stats):
    hasConsensus, ackNodes, nackNodes, replyNodes, queryTime = \
        await eventuallyAny(checkReply, client,
                            request.reqId, wallet.defaultId,
                            retryWait=RETRY_WAIT, timeout=TTL)

    endTime = time.time()
    quorumAt = endTime if hasConsensus else ""  # TODO: only first hasConsensus=True make sense
    latency = endTime - sentAt

    row = ResultRow(signerName=wallet.name,
                    signerId=wallet.defaultId,
                    dest=request.operation.get('dest'),
                    reqId=request.reqId,
                    transactionType=request.operation['type'],
                    sentAt=sentAt,
                    quorumAt=quorumAt,
                    latency=latency,
                    ackNodes=",".join(ackNodes),
                    nackNodes=",".join(nackNodes.keys()),
                    replyNodes=",".join(replyNodes.keys()))
    logger.info("COUNTER {}".format(row))
    stats.append((latency, hasConsensus, queryTime))
    writeResultsRow(row._asdict())


def checkIfConnectedToAll(client):
    connectedNodes = client.nodestack.connecteds
    connectedNodesNum = len(connectedNodes)
    totalNodes = len(client.nodeReg)
    logger.info("Connected {} / {} nodes".
                 format(connectedNodesNum, totalNodes))

    if connectedNodesNum == 0:
        raise Exception("Not connected to any")
    elif connectedNodesNum < totalNodes * 0.8:
        raise Exception("Not connected fully")
    else:
        return True


def clearRaetData():
    """
    Workaround for problems when sponsor's configuration
    needs to be recreated before each test script run
    """
    import glob
    import os.path
    import shutil

    sovrin_path = os.path.join(os.path.expanduser("~"), '.sovrin')
    sovrin_sponsor_path = os.path.join(sovrin_path, 'Sponsor*')
    for path in glob.glob(sovrin_sponsor_path):
        shutil.rmtree(path)
        logger.warn("'%s' was deleted because the "
                    "'PacketError: Failed verification.' issue", path)


def printCurrentTestResults(stats, testStartedAt):
    totalNum = len(stats)
    totalLatency = 0
    successNum = 0
    queryTime = 0
    for lat, hasConsensus, qt in stats:
        totalLatency += lat
        successNum += int(bool(hasConsensus))
        queryTime += qt
    avgLatency = totalLatency / totalNum if totalNum else 0.0
    secSinceTestStart = time.time() - testStartedAt
    failNum = totalNum - successNum
    throughput = successNum / secSinceTestStart
    errRate = failNum / secSinceTestStart
    logger.info(
        """
        ================================
        Test time: {}
        Average latency: {}
        Throughput: {}
        Error rate: {}
        Succeeded: {}
        Failed: {}
        Query Time: {}
        ================================
        """.format(secSinceTestStart, avgLatency, throughput,
                   errRate, successNum, failNum, queryTime)
    )


def main(args):
    # clearRaetData()  # !WARN workaround PacketError

    resultsFileName = \
        "perf_results_{x.numberOfClients}_" \
        "{x.numberOfRequests}_{0}.csv".format(int(time.time()), x=args)
    resultFilePath = os.path.join(args.resultsPath, resultsFileName)
    logger.info("Results file: {}".format(resultFilePath))

    def writeResultsRow(row):
        if not os.path.exists(resultFilePath):
            resultsFd = open(resultFilePath, "w")
            resultsWriter = csv.DictWriter(resultsFd, fieldnames=resultsRowFieldNames)
            resultsWriter.writeheader()
            resultsFd.close()
        resultsFd = open(resultFilePath, "a")
        resultsWriter = csv.DictWriter(resultsFd, fieldnames=resultsRowFieldNames)
        resultsWriter.writerow(row)
        resultsFd.close()

    stats = []

    def buildCoros(coroFunc, corosArgs):
        coros = []
        for args in corosArgs:
            argsExt = args + [writeResultsRow, stats]
            coros.append(functools.partial(coroFunc, *argsExt))
        return coros

    clientPoll = ClientPoll(args.clientsListFilePath,
                            args.numberOfClients, args.numberOfClientsToSkip)

    with Looper(debug=True) as looper:

        # connect

        connectionCoros = []
        for cli in clientPoll.clients:
            looper.add(cli)
            connectionCoros.append(functools.partial(checkIfConnectedToAll, cli))
        looper.run(eventuallyAll(*connectionCoros,
                                 totalTimeout=CONNECTION_TTL,
                                 retryWait=RETRY_WAIT))

        testStartedAt = time.time()
        stats.clear()


        requestType = args.requestType
        sendRequests = {
            "NYM": clientPoll.submitNym,
            "ATTRIB": clientPoll.submitSetAttr,
            "ATTR": clientPoll.submitSetAttr
        }.get(requestType)

        if sendRequests is None:
            raise ValueError("Unsupported request type, "
                             "only NYM and ATTRIB/ATTR are supported")

        def sendAndWaitReplies(numRequests):
            corosArgs = sendRequests(numRequests)
            coros = buildCoros(checkReplyAndLogStat, corosArgs)
            looper.run(eventuallyAll(*coros,
                                     totalTimeout=numRequests * TTL,
                                     retryWait=RETRY_WAIT))
            printCurrentTestResults(stats, testStartedAt)
            logger.info("Sent and waited for {} {} requests"
                        .format(len(coros), requestType))

        if args.atOnce:
            sendAndWaitReplies(numRequests=args.numberOfRequests)
        else:
            for i in range(args.numberOfRequests):
                sendAndWaitReplies(numRequests=1)


if __name__ == '__main__':
    commandLineArgs = parseArgs()
    main(commandLineArgs)
