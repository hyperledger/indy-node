import os
from sovrin_node.persistence.StateTreeStore import StateTreeStore
from plenum.common.state import PruningState
from sovrin_common.txn import TXN_TYPE, \
    TARGET_NYM, allOpKeys, validTxnTypes, ATTRIB, SPONSOR, NYM,\
    ROLE, STEWARD, GET_ATTR, DISCLO, DATA, GET_NYM, \
    TXN_ID, TXN_TIME, reqOpKeys, GET_TXNS, LAST_TXN, TXNS, \
    getTxnOrderedFields, SCHEMA, GET_SCHEMA, openTxns, \
    ISSUER_KEY, GET_ISSUER_KEY, REF, TRUSTEE, TGB, IDENTITY_TXN_TYPES, \
    CONFIG_TXN_TYPES, POOL_UPGRADE, ACTION, START, CANCEL, SCHEDULE, \
    NODE_UPGRADE, COMPLETE, FAIL, HASH, ENC, RAW, NONCE, DDO
import json
import shutil
import pytest
import datetime
from hashlib import sha256


attrName = "last_name"
attrValue = "Anderson"
mockDid = "mock-did"
schemaName = "name"
schemaVersion = "1.2.3"
schemaSeqNo = 123


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
    path = StateTreeStore._makeAttrPath(mockDid, attrName).decode()
    nameHash = sha256(attrName.encode()).hexdigest()
    assert path.split(":") == [mockDid, "ATTR", nameHash]


def test_ddo_key_path():
    path = StateTreeStore._makeDdoPath(mockDid).decode()
    assert path.split(":") == [mockDid, "DDO"]


def test_schema_key_path():
    path = StateTreeStore\
        ._makeSchemaPath(mockDid, schemaName, schemaVersion)\
        .decode()
    assert path.split(":") == [mockDid, "SCHEMA", schemaName + schemaVersion]


def test_issuerkey_key_path():
    path = StateTreeStore\
        ._makeIssuerKeyPath(mockDid, schemaSeqNo)\
        .decode()
    assert path.split(":") == [mockDid, "IPK", schemaSeqNo]


def test_revockey_key_path():
    revRegSeqNo = 456
    time = datetime.datetime.utcnow().isoformat()
    path = StateTreeStore \
        ._makeRevocKeyPath(mockDid, schemaSeqNo, revRegSeqNo, time) \
        .decode()
    expectedPath = [mockDid, "IPK", schemaSeqNo, "REV_REG", revRegSeqNo, time]
    assert path.split(":") == expectedPath


def test_storing_of_attr_in_state_tree(stateTreeStore):
    txn = {
        TXN_TYPE: ATTRIB,
        TARGET_NYM: mockDid,
        RAW: json.dumps({attrName: attrValue})
    }
    stateTreeStore.addTxn(txn, mockDid)
    gotValue = stateTreeStore.getAttr(attrName, mockDid).decode()
    assert attrValue == gotValue


def test_storing_of_ddo_in_state_tree(stateTreeStore):
    mockDdo = json.dumps({
        "@contextrefid": "did-v1",
        "id": mockDid,
        "control": "21tDAKCERh95uGgKbJNHYp"
    })
    txn = {
        TXN_TYPE: NYM,
        TARGET_NYM: mockDid,
        DDO: mockDdo
    }
    stateTreeStore.addTxn(txn, mockDid)
    gotDdo = stateTreeStore.getDdo(mockDid).decode()
    assert mockDdo == gotDdo


def test_storing_of_schema_in_state_tree(stateTreeStore: StateTreeStore):
    schema = json.dumps({
        "name": schemaName,
        "version": schemaVersion,
    })
    txn = {
        TXN_TYPE: SCHEMA,
        TARGET_NYM: mockDid,
        DATA: schema
    }
    stateTreeStore.addTxn(txn, mockDid)
    gotSchema = stateTreeStore\
        .getSchema(mockDid, schemaName, schemaVersion)\
        .decode()
    assert schema == gotSchema
