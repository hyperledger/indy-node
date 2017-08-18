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

from stp_core.loop.looper import Looper

from stp_core.common.log import getlogger
from plenum.common.types import HA
from plenum.common.util import randomString
from stp_core.network.port_dispenser import genHa
from plenum.common.signer_did import DidSigner

from plenum.common.constants import \
    TARGET_NYM, TXN_TYPE, NYM, \
    ROLE, RAW, NODE,\
    DATA, ALIAS, CLIENT_IP, \
    CLIENT_PORT

from plenum.test.helper import eventually
from plenum.test.test_client import \
    getAcksFromInbox, getNacksFromInbox, getRepliesFromInbox

from sovrin_common.constants import ATTRIB, GET_ATTR
from sovrin_common.config_util import getConfig
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.client.client import Client
from sovrin_common.identity import Identity
from sovrin_common.constants import GET_NYM


logger = getlogger()
config = getConfig()

TTL = 120.0  # 60.0
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

    parser.add_argument(
        "-t",
        "--request_type",
        action="store",
        type=str,
        default="NYM",
        dest="requestType",
        help="type of requests to send, supported = NYM, GET_NYM, ATTRIB")

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
                        default="{}/load_test_clients.list".format(
                            os.getcwd()),
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
    wallet.addIdentifier(signer=DidSigner(seed=seed))
    client = Client(name, ha=ha)
    return client, wallet


class Rotator:

    def __init__(self, collection):
        self._collection = collection
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if len(self._collection) == 0:
            raise StopIteration()
        if self._index >= len(self._collection):
            self._index = 0
        x = self._collection[self._index]
        self._index += 1
        return x


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
                signer = DidSigner()
                idr = signer.identifier
                if idr not in usedIdentifiers:
                    usedIdentifiers.add(idr)
                    return signer

        def makeRequest(cli, wallet):
            signer = newSigner()
            idy = Identity(identifier=signer.identifier,
                           verkey=signer.verkey)

            wallet.addTrustAnchoredIdentity(idy)

        return self.submitGeneric(makeRequest, reqsPerClient)

    def submitGetNym(self, reqsPerClient=1):

        ids = Rotator([wallet.defaultId
                       for _, wallet in self._clientsWallets])

        def makeRequest(cli, wallet):
            op = {
                TARGET_NYM: next(ids),
                TXN_TYPE: GET_NYM,
            }
            req = wallet.signOp(op)
            wallet.pendRequest(req)

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
            return map(lambda x: (x[0], str.encode(x[1])),
                       creds[self.__skip:self.__skip + self.__limit])

    def _spawnClient(self, name, seed, host='0.0.0.0'):
        self.__startPort += randint(100, 1000)
        address = HA(host, self.__startPort)
        logger.info("Seed for client {} is {}, "
                    "its len is {}".format(name, seed, len(seed)))
        return createClientAndWalletWithSeed(name, seed, address)


resultsRowFieldNames = [
    'signerName',
    'signerId',
    'dest',
    'reqId',
    'transactionType',
    'sentAt',
    'quorumAt',
    'latency',
    'ackNodes',
    'nackNodes',
    'replyNodes']
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
    acks, nacks, replies = [], [], []
    try:
        # acks = client.reqRepStore.getAcks(requestId)
        # nacks = client.reqRepStore.getNacks(requestId)
        # replies = client.reqRepStore.getReplies(requestId)
        acks = getAcksFromInbox(client, requestId)
        nacks = getNacksFromInbox(client, requestId)
        replies = getRepliesFromInbox(client, requestId)
        hasConsensus = client.hasConsensus(identifier, requestId)
    except KeyError:
        logger.info("No replies for {}:{} yet".format(identifier, requestId))
    except Exception as e:
        logger.warn(
            "Error occured during checking replies: {}".format(
                repr(e)))
    finally:
        return hasConsensus, (hasConsensus, acks, nacks, replies)


async def checkReplyAndLogStat(client, wallet, request, sentAt, writeResultsRow, stats):
    hasConsensus, ackNodes, nackNodes, replyNodes = \
        await eventuallyAny(checkReply, client,
                            request.reqId, wallet.defaultId,
                            retryWait=RETRY_WAIT, timeout=TTL
                            )

    endTime = time.time()
    # TODO: only first hasConsensus=True make sense
    quorumAt = endTime if hasConsensus else ""
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
    stats.append((latency, hasConsensus))
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


def printCurrentTestResults(stats, testStartedAt):
    totalNum = len(stats)
    totalLatency = 0
    successNum = 0
    for lat, hasConsensus in stats:
        totalLatency += lat
        successNum += int(bool(hasConsensus))
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
        ================================
        """.format(secSinceTestStart, avgLatency, throughput,
                   errRate, successNum, failNum)
    )


def main(args):

    resultsFileName = \
        "perf_results_{x.numberOfClients}_" \
        "{x.numberOfRequests}_{0}.csv".format(int(time.time()), x=args)
    resultFilePath = os.path.join(args.resultsPath, resultsFileName)
    logger.info("Results file: {}".format(resultFilePath))

    def writeResultsRow(row):
        if not os.path.exists(resultFilePath):
            resultsFd = open(resultFilePath, "w")
            resultsWriter = csv.DictWriter(
                resultsFd, fieldnames=resultsRowFieldNames)
            resultsWriter.writeheader()
            resultsFd.close()
        resultsFd = open(resultFilePath, "a")
        resultsWriter = csv.DictWriter(
            resultsFd, fieldnames=resultsRowFieldNames)
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
            connectionCoros.append(
                functools.partial(checkIfConnectedToAll, cli))
        for coro in connectionCoros:
            looper.run(eventually(coro,
                                  timeout=CONNECTION_TTL,
                                  retryWait=RETRY_WAIT,
                                  verbose=False))

        testStartedAt = time.time()
        stats.clear()

        requestType = args.requestType
        sendRequests = {
            "NYM": clientPoll.submitNym,
            "GET_NYM": clientPoll.submitGetNym,
            "ATTRIB": clientPoll.submitSetAttr,
            "ATTR": clientPoll.submitSetAttr
        }.get(requestType)

        if sendRequests is None:
            raise ValueError("Unsupported request type, "
                             "only NYM and ATTRIB/ATTR are supported")

        def sendAndWaitReplies(numRequests):
            corosArgs = sendRequests(numRequests)
            coros = buildCoros(checkReplyAndLogStat, corosArgs)
            for coro in coros:
                task = eventually(coro,
                                  retryWait=RETRY_WAIT,
                                  timeout=TTL,
                                  verbose=False)
                looper.run(task)
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
