from indy_node.test.did.conftest import nym_get
from indy_node.test.helper import sdk_rotate_verkey


def testAddDidWithoutAVerkey(nym_empty_vk):
    pass


def testRetrieveEmptyVerkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_empty_vk):
    nwh, ndid = nym_empty_vk
    resp_data = nym_get(looper, sdk_pool_handle, sdk_wallet_trustee, ndid)
    assert ndid == resp_data[0]
    assert not resp_data[1]


def testChangeEmptyVerkeyToNewVerkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_empty_vk):
    _, did = nym_empty_vk
    trw, trd = sdk_wallet_trustee
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, trw, trd, did)
    assert new_vk


def testRetrieveChangedVerkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_empty_vk):
    _, did = nym_empty_vk
    trw, trd = sdk_wallet_trustee
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, trw, trd, did)
    resp_data = nym_get(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    assert did == resp_data[0]
    assert new_vk == resp_data[1]


def testVerifySigWithChangedVerkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_empty_vk):
    wh, did = nym_empty_vk
    trw, trd = sdk_wallet_trustee
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, trw, trd, did)
    # check sign by getting nym from ledger - if succ then sign is ok
    resp_data = nym_get(looper, sdk_pool_handle, (wh, did), did)
    assert did == resp_data[0]
    assert new_vk == resp_data[1]
