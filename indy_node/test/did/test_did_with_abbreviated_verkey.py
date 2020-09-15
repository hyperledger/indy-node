import pytest

from indy_node.test.did.conftest import nym_get
from indy_node.test.helper import sdk_rotate_verkey


@pytest.mark.did
def test_add_did_with_verkey(nym_abbrv_vk):
    pass


@pytest.mark.did
def test_retrieve_abbrv_verkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_abbrv_vk):
    nwh, ndid, nvk = nym_abbrv_vk
    resp_data = nym_get(looper, sdk_pool_handle, sdk_wallet_trustee, ndid)
    assert ndid == resp_data[0]
    assert nvk == resp_data[1]


@pytest.mark.did
def test_change_verkey_to_new_verkey(looper, tconf, nodeSet, sdk_pool_handle, nym_abbrv_vk):
    wh, did, nvk = nym_abbrv_vk
    new_verkey = sdk_rotate_verkey(looper, sdk_pool_handle, wh, did, did)
    assert nvk != new_verkey


@pytest.mark.did
def test_retrieve_changed_verkey(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee, nym_abbrv_vk):
    wh, did, vk = nym_abbrv_vk
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, wh, did, did)
    resp_data = nym_get(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    assert did == resp_data[0]
    assert vk != resp_data[1]
    assert new_vk == resp_data[1]


@pytest.mark.did
def test_verify_sig_with_changed_verkey(looper, tconf, nodeSet, sdk_pool_handle, nym_abbrv_vk):
    wh, did, vk = nym_abbrv_vk
    new_vk = sdk_rotate_verkey(looper, sdk_pool_handle, wh, did, did)
    # check sign by getting nym from ledger - if succ then sign is ok
    resp_data = nym_get(looper, sdk_pool_handle, (wh, did), did)
    assert did == resp_data[0]
    assert vk != resp_data[1]
    assert new_vk == resp_data[1]
