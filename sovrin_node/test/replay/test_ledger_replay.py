import pytest
import json

from pyorient import OrientBinaryObject

from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from anoncreds.protocol.types import Schema, ID
from anoncreds.protocol.wallet.issuer_wallet import IssuerWalletInMemory
from anoncreds.test.conftest import GVT

from stp_core.loop.eventually import eventually
from plenum.common.util import randomString
from plenum.test import waits as plenumWaits
from plenum.test.test_node import checkNodesConnected
from plenum.test.node_catchup.helper import checkNodeLedgersForEquality

from sovrin_client.test.conftest import primes1
from sovrin_client.anon_creds.sovrin_public_repo import SovrinPublicRepo
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.client.client import Client

from sovrin_client.test.helper import addRole, getClientAddedWithRole
from sovrin_client.test.conftest import userWalletA
from sovrin_common.constants import TGB

from sovrin_node.test.helper import addAttributeAndCheck
from sovrin_node.test.upgrade.conftest import validUpgrade
from sovrin_node.test.helper import TestNode


@pytest.fixture(scope="module")
def anotherTGB(nodeSet, tdir, looper, trustee, trusteeWallet):
    return getClientAddedWithRole(nodeSet, tdir, looper,
                                  trustee, trusteeWallet,
                                  'newTGB', TGB)


@pytest.fixture(scope="module")
def addNymTxn(looper, anotherTGB):
    """
    Make new NYM transaction
    The new TGB adds a NYM to ledger
    """
    addRole(looper, *anotherTGB, name=randomString())


@pytest.fixture(scope="module")
def addedRawAttribute(userWalletA: Wallet, trustAnchor: Client,
                      trustAnchorWallet: Wallet, looper):
    attrib = Attribute(name='test attribute',
                       origin=trustAnchorWallet.defaultId,
                       value=json.dumps({'name': 'Mario'}),
                       dest=userWalletA.defaultId,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    return attrib


@pytest.fixture(scope="module")
def publicRepo(steward, stewardWallet):
    return SovrinPublicRepo(steward, stewardWallet)


@pytest.fixture(scope="module")
def schemaDefGvt(stewardWallet):
    return Schema('GVT', '1.0', GVT.attribNames(), stewardWallet.defaultId)


@pytest.fixture(scope="module")
def submittedSchemaDefGvt(publicRepo, schemaDefGvt, looper):
    return looper.run(publicRepo.submitSchema(schemaDefGvt))


@pytest.fixture(scope="module")
def submittedPublicKey(submittedPublicKeys):
    return submittedPublicKeys[0]


@pytest.fixture(scope="module")
def issuerGvt(publicRepo):
    return Issuer(IssuerWalletInMemory('issuer1', publicRepo),
                  AttributeRepoInMemory())


@pytest.fixture(scope="module")
def publicSecretKey(submittedSchemaDefGvtID, issuerGvt, primes1, looper):
    return looper.run(
        issuerGvt._primaryIssuer.genKeys(submittedSchemaDefGvtID, **primes1))


@pytest.fixture(scope="module")
def publicSecretRevocationKey(issuerGvt, looper):
    return looper.run(issuerGvt._nonRevocationIssuer.genRevocationKeys())


@pytest.fixture(scope="module")
def submittedSchemaDefGvtID(submittedSchemaDefGvt):
    return ID(schemaKey=submittedSchemaDefGvt.getKey(),
              schemaId=submittedSchemaDefGvt.seqId)


@pytest.fixture(scope="module")
def submittedPublicKeys(submittedSchemaDefGvtID, publicRepo, publicSecretKey,
                        publicSecretRevocationKey, looper):
    pk, sk = publicSecretKey
    pkR, skR = publicSecretRevocationKey
    return looper.run(
        publicRepo.submitPublicKeys(id=submittedSchemaDefGvtID, pk=pk, pkR=pkR))


def compareGraph(table, nodeSet):
    """
    compare stopped node graph(db) with
    other nodes
    """
    stoppedNodeRecords = []
    stoppedNodeClient = nodeSet[0].graphStore.client
    stoppedNodeRecordCount = stoppedNodeClient.db_count_records()

    tableRecodesStoppedNode = stoppedNodeClient.query("SELECT * FROM {}".format(table))
    for nodeRecord in tableRecodesStoppedNode:

        if table == "ClaimDef" and isinstance(nodeRecord.oRecordData["data"], str):
            nodeRecord.oRecordData["data"] = json.loads(nodeRecord.oRecordData["data"])

        stoppedNodeRecords.append({k: v for k, v in nodeRecord.oRecordData.items()
                                   if not isinstance(v, OrientBinaryObject)
                                   })

    for node in nodeSet[1:4]:
        client = node.graphStore.client
        recordCount = client.db_count_records()
        assert recordCount == stoppedNodeRecordCount

        records = []
        tableRecodes = client.query("SELECT * FROM {}".format(table))
        for record in tableRecodes:

            if table == "ClaimDef" and isinstance(record.oRecordData["data"], str):
                record.oRecordData["data"] = json.loads(record.oRecordData["data"])

            records.append({k: v for k, v in record.oRecordData.items()
                            if not isinstance(v, OrientBinaryObject)
                            })
        assert records == stoppedNodeRecords

def testReplayLedger(addNymTxn, addedRawAttribute, submittedPublicKeys,
                     nodeSet, looper, tconf, tdirWithPoolTxns,
                     allPluginsPath, txnPoolNodeSet):
    """
    stop first node (which will clean graph db too)
    then restart node
    """
    nodeToStop = nodeSet[0]
    nodeToStop.cleanupOnStopping = False
    looper.removeProdable(nodeToStop)
    nodeToStop.stop()
    name = nodeToStop.name
    nha = nodeToStop.nodestack.ha
    cha = nodeToStop.clientstack.ha
    del nodeToStop

    #client = nodeToStop.graphStore.client
    #client.db_drop(client._connection.db_opened)
    newNode = TestNode(name, basedirpath=tdirWithPoolTxns,
                       config=tconf, pluginPaths=allPluginsPath,
                       ha=nha, cliha=cha)
    looper.add(newNode)
    nodeSet[0] = newNode
    looper.run(checkNodesConnected(nodeSet))
    timeout = plenumWaits.expectedPoolLedgerCheck(len(txnPoolNodeSet))
    looper.run(eventually(checkNodeLedgersForEquality, newNode,
                          *txnPoolNodeSet[1:4], retryWait=1, timeout=timeout))

    compareGraph("NYM", nodeSet)
    compareGraph("ClaimDef", nodeSet)
    compareGraph("Schema", nodeSet)
