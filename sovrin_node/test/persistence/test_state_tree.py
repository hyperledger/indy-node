import json
import os
import shutil
from hashlib import sha256

import pytest
from plenum.common.state import PruningState
from sovrin_common.txn import TXN_TYPE, \
    TARGET_NYM, ATTRIB, DATA, SCHEMA, ISSUER_KEY, REF, RAW

from sovrin_node.persistence.state_tree_store import StateTreeStore


attrName = "last_name"
attrValue = "Anderson"
mockDid = "mock-did"
schemaName = "name"
schemaVersion = "1.2.3"
schemaSeqNo = "123"


@pytest.fixture(scope="function")
def dataLocation():
    import random
    path = "/tmp/sovrin-node/test/{}".format(random.randint(0, 100))
    print("OK = ", path)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path


@pytest.fixture(scope="function")
def state(dataLocation):
    return PruningState(dataLocation)


@pytest.fixture(scope="function")
def stateTreeStore(state):
    return StateTreeStore(state)


def test_attr_key_path():
    path = StateTreeStore\
        ._makeAttrPath(mockDid, attrName)\
        .decode()
    nameHash = sha256(attrName.encode()).hexdigest()

    assert path.split(":") == [mockDid,
                               StateTreeStore.MARKER_ATTR,
                               nameHash]


def test_schema_key_path():
    path = StateTreeStore\
        ._makeSchemaPath(mockDid, schemaName, schemaVersion)\
        .decode()
    assert path.split(":") == [mockDid,
                               StateTreeStore.MARKER_SCHEMA,
                               schemaName + schemaVersion]


def test_issuerkey_key_path():
    path = StateTreeStore._makeIssuerKeyPath(mockDid, schemaSeqNo).decode()
    assert path.split(":") == [mockDid,
                               StateTreeStore.MARKER_IPK,
                               schemaSeqNo]


def test_storing_of_attr_in_state_tree(stateTreeStore):
    txn = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: mockDid,
        RAW: json.dumps({attrName: attrValue})
    }
    stateTreeStore.addTxn(txn)
    gotValue = stateTreeStore.getAttr(mockDid, attrName, isCommitted=False)
    assert attrValue == gotValue


def test_storing_of_schema_in_state_tree(stateTreeStore):
    schema = json.dumps({
        "name": schemaName,
        "version": schemaVersion,
    })
    txn = {
        TXN_TYPE: SCHEMA,
        TARGET_NYM: mockDid,
        DATA: schema
    }
    stateTreeStore.addTxn(txn)
    gotSchema = stateTreeStore.getSchema(mockDid, schemaName, schemaVersion, isCommitted=False)
    assert schema == gotSchema


def test_storing_of_issuerkey_in_state_tree(stateTreeStore):
    key = json.dumps({
        "N": "some n",
        "R": "some r",
        "S": "some s",
        "Z": "some z"
    })
    txn = {
        TXN_TYPE: ISSUER_KEY,
        TARGET_NYM: mockDid,
        DATA: key,
        REF: schemaSeqNo
    }
    stateTreeStore.addTxn(txn)
    gotKey = stateTreeStore.getIssuerKey(mockDid, schemaSeqNo, isCommitted=False)
    assert key == gotKey
