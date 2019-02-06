import json
import pytest

from indy.did import create_and_store_my_did, replace_keys_start, replace_keys_apply
from indy.ledger import build_get_nym_request
from indy_common.constants import TRUST_ANCHOR_STRING
from indy_node.test.helper import sdk_add_attribute_and_check
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.test.helper import sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request, \
    prepare_nym_request, sdk_add_new_nym

TRUST_ANCHOR_SEED = 'TRUST0NO0ONE00000000000000000001'


def set_verkey(looper, sdk_pool_handle, sdk_wallet_sender, dest, verkey):
    wh, _ = sdk_wallet_sender
    nym_request, new_did = looper.loop.run_until_complete(
        prepare_nym_request(sdk_wallet_sender, None,
                            None, TRUST_ANCHOR_STRING, dest, verkey, False if verkey else True))
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_sender,
                                                        sdk_pool_handle, nym_request)
    sdk_get_and_check_replies(looper, [request_couple])
    return wh, new_did


@pytest.fixture("module")
def trust_anchor_did_verkey(looper, sdk_wallet_client):
    wh, _ = sdk_wallet_client
    named_did, verkey = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': TRUST_ANCHOR_SEED})))
    return named_did, verkey


def test_pool_nodes_started(nodeSet):
    pass

@pytest.fixture(scope='function', params=['trustee', 'steward'])
def sdk_wallet(request, sdk_wallet_steward, sdk_wallet_trustee):
    if request.param == 'steward':
        yield sdk_wallet_steward
    elif request.param == 'trustee':
        yield sdk_wallet_trustee


def test_send_same_nyms_only_first_gets_written(
        looper, sdk_pool_handle, sdk_wallet):
    wh, _ = sdk_wallet
    seed = randomString(32)
    did, verkey = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': seed})))

    # request 1
    _, did1 = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet, dest=did, verkey=verkey)

    seed = randomString(32)
    _, verkey = looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': seed})))
    # request 2
    with pytest.raises(RequestRejectedException) as e:
        _, did2 = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet, dest=did, verkey=verkey)
    e.match('can not touch verkey field since only the owner can modify it')


def get_nym(looper, sdk_pool_handle, sdk_wallet_steward, t_did):
    _, s_did = sdk_wallet_steward
    get_nym_req = looper.loop.run_until_complete(build_get_nym_request(s_did, t_did))
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_steward,
                                             sdk_pool_handle, get_nym_req)
    return sdk_get_and_check_replies(looper, [req])


def test_get_nym_without_adding_it(looper, sdk_pool_handle, sdk_wallet_steward,
                                   trust_anchor_did_verkey):
    t_did, _ = trust_anchor_did_verkey
    rep = get_nym(looper, sdk_pool_handle, sdk_wallet_steward, t_did)
    assert not rep[0][1]['result']['data']


@pytest.fixture(scope="module")
def nym_added(looper, sdk_pool_handle, sdk_wallet_steward, trust_anchor_did_verkey):
    dest, _ = trust_anchor_did_verkey
    set_verkey(looper, sdk_pool_handle, sdk_wallet_steward, dest, None)


def test_add_nym(nym_added):
    pass


def test_get_nym_without_verkey(looper, sdk_pool_handle, sdk_wallet_steward, nym_added,
                                trust_anchor_did_verkey):
    t_did, _ = trust_anchor_did_verkey
    rep = get_nym(looper, sdk_pool_handle, sdk_wallet_steward, t_did)
    assert rep[0][1]['result']['data']
    assert not json.loads(rep[0][1]['result']['data'])['verkey']


@pytest.fixture(scope="module")
def verkey_added_to_nym(looper, sdk_pool_handle, sdk_wallet_steward, nym_added, trust_anchor_did_verkey):
    wh, _ = sdk_wallet_steward
    did, _ = trust_anchor_did_verkey
    verkey = looper.loop.run_until_complete(replace_keys_start(wh, did, json.dumps({'': ''})))
    set_verkey(looper, sdk_pool_handle, sdk_wallet_steward, did, verkey)
    looper.loop.run_until_complete(replace_keys_apply(wh, did))


def test_add_verkey_to_existing_nym(verkey_added_to_nym):
    pass


def test_get_did_with_verkey(looper, sdk_pool_handle, sdk_wallet_steward, verkey_added_to_nym,
                             trust_anchor_did_verkey):
    t_did, _ = trust_anchor_did_verkey
    rep = get_nym(looper, sdk_pool_handle, sdk_wallet_steward, t_did)
    assert rep[0][1]['result']['data']
    assert json.loads(rep[0][1]['result']['data'])['verkey']


def test_send_attrib_for_did(looper, sdk_pool_handle, sdk_wallet_steward,
                             verkey_added_to_nym, trust_anchor_did_verkey):
    raw = '{"name": "Alice"}'
    dest, _ = trust_anchor_did_verkey
    wh, _ = sdk_wallet_steward
    sdk_add_attribute_and_check(looper, sdk_pool_handle, (wh, dest), raw, dest)


@pytest.fixture(scope="module")
def verkey_removed_from_existing_did(looper, sdk_pool_handle, sdk_wallet_steward,
                                     verkey_added_to_nym, trust_anchor_did_verkey):
    did, _ = trust_anchor_did_verkey
    wh, _ = sdk_wallet_steward
    set_verkey(looper, sdk_pool_handle, (wh, did), did, None)


def test_remove_verkey_from_did(verkey_removed_from_existing_did):
    pass


@pytest.mark.skip(
    reason="SOV-568. Obsolete assumption, if an identity has set "
           "its verkey to blank, no-one including "
           "itself can change it")
def testNewverkey_added_to_nym(be, do, philCli, abbrevIdr,
                               verkeyRemovedFromExistingDID):
    pass
