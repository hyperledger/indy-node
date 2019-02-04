import pytest
import json

from indy.did import abbreviate_verkey, create_and_store_my_did
from indy.ledger import build_get_nym_request, build_nym_request

from plenum.common.util import randomString
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request


def add_new_nym(looper, sdk_pool_handle, creators_wallet, dest, verkey=None):
    wh, submitter_did = creators_wallet
    nym_request = looper.loop.run_until_complete(build_nym_request(submitter_did, dest, verkey, None, None))
    req = sdk_sign_and_send_prepared_request(looper, creators_wallet, sdk_pool_handle, nym_request)
    sdk_get_and_check_replies(looper, [req])
    return wh, dest


@pytest.fixture(scope='function')
def nym_full_vk(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    wh, tr_did = sdk_wallet_trustee
    (new_did, new_verkey) = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': randomString(32)})))
    assert not new_verkey.startswith("~")
    nwh, nd = add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee, dest=new_did, verkey=new_verkey)
    return nwh, nd, new_verkey


@pytest.fixture(scope='function')
def nym_abbrv_vk(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    wh, tr_did = sdk_wallet_trustee
    (new_did, new_verkey) = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': randomString(32)})))
    abbrv_vk = looper.loop.run_until_complete(abbreviate_verkey(new_did, new_verkey))
    assert abbrv_vk.startswith("~")
    nwh, nd = add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee, dest=new_did, verkey=abbrv_vk)
    return nwh, nd, abbrv_vk


@pytest.fixture(scope='function')
def nym_empty_vk(looper, tconf, nodeSet, sdk_pool_handle, sdk_wallet_trustee):
    wh, tr_did = sdk_wallet_trustee
    (new_did, new_verkey) = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': randomString(32)})))
    nwh, nd = add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee, dest=new_did)
    return nwh, nd


def nym_get(looper, sdk_pool_handle, sdk_wallet_sign, did):
    sign_w, sign_did = sdk_wallet_sign
    get_nym_req = looper.loop.run_until_complete(build_get_nym_request(sign_did, did))
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_sign, sdk_pool_handle, get_nym_req)
    repl_data = sdk_get_and_check_replies(looper, [req])[0][1].get("result", {}).get("data", "")
    dt = json.loads(repl_data)
    nym = dt.get("dest", None)
    vk = dt.get("verkey", None)
    return nym, vk
