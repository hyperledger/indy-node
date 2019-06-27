from indy_node.test.did.conftest import nym_get
from indy_node.test.helper import sdk_rotate_verkey


def testAddDidWithVerkey(nym_abbrv_vk):
    pass


def testRetrieveAbbrvVerkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_abbrv_vk):
    nwh, ndid, nvk = nym_abbrv_vk
    resp_data = nym_get(looper, sdk_pool_handle, sdk_wallet_trustee, ndid)
    assert ndid == resp_data[0]
    assert nvk == resp_data[1]


def testChangeVerkeyToNewVerkey(looper, tconf, nodeSet, sdk_pool_handle, nym_abbrv_vk):
    wh, did, nvk = nym_abbrv_vk
    new_verkey = sdk_rotate_verkey(looper, sdk_pool_handle, wh, did, did)
    assert nvk != new_verkey


def testRetrieveChangedVerkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_abbrv_vk):
    wh, did, vk = nym_abbrv_vk
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, wh, did, did)
    resp_data = nym_get(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    assert did == resp_data[0]
    assert vk != resp_data[1]
    assert new_vk == resp_data[1]


def testVerifySigWithChangedVerkey(looper, tconf, nodeSet, sdk_pool_handle, nym_abbrv_vk):
    wh, did, vk = nym_abbrv_vk
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, wh, did, did)
    # check sign by getting nym from ledger - if succ then sign is ok
    resp_data = nym_get(looper, sdk_pool_handle, (wh, did), did)
    assert did == resp_data[0]
    assert vk != resp_data[1]
    assert new_vk == resp_data[1]
