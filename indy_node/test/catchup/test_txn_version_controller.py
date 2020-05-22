import pytest

from indy_common.constants import POOL_UPGRADE, ACTION, START, SCHEDULE, NODE_UPGRADE, COMPLETE
from indy_node.server.txn_version_controller import TxnVersionController
from plenum.common.constants import TXN_PAYLOAD_TYPE, TXN_PAYLOAD, TXN_PAYLOAD_DATA, DATA, VERSION, \
    TXN_PAYLOAD_METADATA_FROM, TXN_PAYLOAD_METADATA, TXN_METADATA, TXN_METADATA_TIME

node_count = 4


@pytest.fixture()
def txn_version_controller():
    return TxnVersionController()


@pytest.fixture()
def pool_upgrade_txn():
    return {TXN_METADATA: {TXN_METADATA_TIME: 0},
            TXN_PAYLOAD: {TXN_PAYLOAD_TYPE: POOL_UPGRADE,
                          TXN_PAYLOAD_DATA: {ACTION: START,
                                             SCHEDULE: {i for i in list(range(node_count))}}}}


def create_node_upgrade_txn(version, frm, timestamp=0):
    return {TXN_METADATA: {TXN_METADATA_TIME: timestamp},
            TXN_PAYLOAD: {TXN_PAYLOAD_TYPE: NODE_UPGRADE,
                          TXN_PAYLOAD_METADATA: {TXN_PAYLOAD_METADATA_FROM: frm},
                          TXN_PAYLOAD_DATA: {DATA: {ACTION: COMPLETE,
                                                    VERSION: version}}}}


def test_update_version_without_pool_upgrade(txn_version_controller):
    version = "version1"
    assert txn_version_controller.version is None

    txn_version_controller.update_version(create_node_upgrade_txn(version, "Node1"))
    assert txn_version_controller.version == version


def test_update_version_with_pool_upgrade(txn_version_controller, pool_upgrade_txn):
    version = "version1"
    assert txn_version_controller.version is None

    txn_version_controller.update_version(pool_upgrade_txn)
    txn_version_controller.update_version(create_node_upgrade_txn(version, "Node1"))
    assert txn_version_controller.version is None

    txn_version_controller.update_version(create_node_upgrade_txn(version, "Node1"))
    assert txn_version_controller.version is None

    txn_version_controller.update_version(create_node_upgrade_txn(version, "Node2"))
    assert txn_version_controller.version == version


def test_cleanup_after_update_version(txn_version_controller, pool_upgrade_txn):
    version1 = "version1"
    version2 = "version2"
    assert txn_version_controller.version is None

    txn_version_controller.update_version(pool_upgrade_txn)
    # send NODE_UPGRADE for the old version, check that the version didn't changed (doesn't has a quorum)
    txn_version_controller.update_version(create_node_upgrade_txn(version1, "Node1"))
    assert txn_version_controller.version is None

    # send NODE_UPGRADE for the new version, check that the version changed
    txn_version_controller.update_version(create_node_upgrade_txn(version2, "Node1"))
    txn_version_controller.update_version(create_node_upgrade_txn(version2, "Node2"))
    assert txn_version_controller.version == version2

    # send NODE_UPGRADE for the old version, check that the version didn't change (doesn't has a quorum)
    txn_version_controller.update_version(create_node_upgrade_txn(version1, "Node2"))
    assert txn_version_controller.version == version2


def test_get_version_with_timestamp(txn_version_controller, pool_upgrade_txn):
    version1 = "version1"
    version2 = "version2"

    txn_version_controller.update_version(create_node_upgrade_txn(version1, "Node1", 10))
    txn_version_controller.update_version(create_node_upgrade_txn(version2, "Node1", 100))

    assert txn_version_controller.get_pool_version(0) is None
    assert txn_version_controller.get_pool_version(11) == version1
    assert txn_version_controller.get_pool_version(200) == version2
