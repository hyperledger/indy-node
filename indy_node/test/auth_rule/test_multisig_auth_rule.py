import json

import pytest

from indy_common.authorize.auth_actions import ADD_PREFIX
from indy_common.authorize.auth_constraints import ROLE, AuthConstraint, AuthConstraintAnd, AuthConstraintOr
from indy_common.constants import NYM
from indy_node.test.auth_rule.helper import create_verkey_did, sdk_send_and_check_auth_rule_request
from indy_node.test.nym_txn.test_nym_additional import get_nym
from plenum.common.constants import STEWARD, STEWARD_STRING, TRUSTEE, TRUSTEE_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.test.conftest import sdk_wallet_client
from plenum.test.helper import sdk_get_and_check_replies, sdk_send_signed_requests, sdk_sign_request_objects, \
    sdk_json_to_request_object, sdk_multi_sign_request_objects
from plenum.test.pool_transactions.helper import prepare_nym_request, \
    sdk_sign_and_send_prepared_request, sdk_add_new_nym

auth_constraint = AuthConstraintOr(auth_constraints=[AuthConstraintAnd(auth_constraints=[AuthConstraint(role=STEWARD,
                                                                                                        sig_count=2),
                                                                                         AuthConstraint(role=TRUSTEE,
                                                                                                        sig_count=1)]),
                                                     AuthConstraint(role=TRUSTEE,
                                                                    sig_count=2)
                                                     ])


@pytest.fixture(scope='module', params=[(2, 0), (3, 0), (1, 2), (1, 3), (2, 1)])
def wallets_for_success(request, sdk_wallet_steward_list, sdk_wallet_trustee_list):
    return (
        sdk_wallet_trustee_list[:request.param[0]] +
        sdk_wallet_steward_list[:request.param[1]]
    )


@pytest.fixture(scope='module', params=[(0, 3), (1, 0), (1, 1)])
def wallets_for_fail(request, sdk_wallet_steward_list, sdk_wallet_trustee_list):
    return (
        sdk_wallet_trustee_list[:request.param[0]] +
        sdk_wallet_steward_list[:request.param[1]]
    )


@pytest.fixture(scope='module')
def sdk_wallet_steward_list(looper,
                            sdk_wallet_trustee,
                            sdk_pool_handle):
    sdk_wallet_steward_list = []
    for i in range(3):
        wallet = sdk_add_new_nym(looper,
                                 sdk_pool_handle,
                                 sdk_wallet_trustee,
                                 alias='steward{}'.format(i),
                                 role=STEWARD_STRING)
        sdk_wallet_steward_list.append(wallet)
    return sdk_wallet_steward_list


@pytest.fixture(scope='module')
def sdk_wallet_trustee_list(looper,
                            sdk_wallet_trustee,
                            sdk_pool_handle):
    sdk_wallet_trustee_list = []
    for i in range(3):
        wallet = sdk_add_new_nym(looper,
                                 sdk_pool_handle,
                                 sdk_wallet_trustee,
                                 alias='trustee{}'.format(i),
                                 role=TRUSTEE_STRING)
        sdk_wallet_trustee_list.append(wallet)
    return sdk_wallet_trustee_list


@pytest.fixture(scope='module')
def prepare_auth_map(looper,
                     sdk_wallet_trustee,
                     sdk_pool_handle):
    wh, _ = sdk_wallet_trustee
    did1, verkey1 = create_verkey_did(looper, wh)
    """Adding new steward for old auth rules"""
    add_new_nym(looper,
                sdk_pool_handle,
                [sdk_wallet_trustee],
                'newSteward1',
                STEWARD_STRING,
                dest=did1, verkey=verkey1)
    sdk_send_and_check_auth_rule_request(looper, sdk_pool_handle, sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=NYM, field=ROLE, new_value=STEWARD, old_value=None,
                                         constraint=auth_constraint.as_dict)


def add_new_nym(looper, sdk_pool_handle, creators_wallets,
                alias=None, role=None, seed=None,
                dest=None, verkey=None, skipverkey=False, no_wait=False):
    seed = seed or randomString(32)
    alias = alias or randomString(5)
    wh, _ = creators_wallets[0]

    # filling nym request and getting steward did
    # if role == None, we are adding client
    nym_request, new_did = looper.loop.run_until_complete(
        prepare_nym_request(creators_wallets[0], seed,
                            alias, role, dest, verkey, skipverkey))

    # sending request using 'sdk_' functions
    signed_reqs = sdk_multi_sign_request_objects(looper, creators_wallets,
                                                 [sdk_json_to_request_object(
                                                     json.loads(nym_request))])
    request_couple = sdk_send_signed_requests(sdk_pool_handle, signed_reqs)[0]
    if no_wait:
        return request_couple
    # waitng for replies
    sdk_get_and_check_replies(looper, [request_couple])


def test_multi_sig_auth_rule(looper,
                             wallets_for_success,
                             sdk_pool_handle,
                             prepare_auth_map):
    wh, _ = wallets_for_success[0]
    did, verkey = create_verkey_did(looper, wh)
    add_new_nym(looper,
                sdk_pool_handle,
                wallets_for_success,
                'newSteward1',
                STEWARD_STRING,
                dest=did)
    get_nym(looper, sdk_pool_handle, wallets_for_success[0], did)


def test_reject_request_with_multi_sig_auth_rule(looper,
                                                 wallets_for_fail,
                                                 sdk_pool_handle,
                                                 prepare_auth_map):
    with pytest.raises(RequestRejectedException, match="Rule for this action is: {}".format(auth_constraint)):
        """Adding new steward for changed auth rules"""
        add_new_nym(looper,
                    sdk_pool_handle,
                    wallets_for_fail,
                    'newSteward2',
                    STEWARD_STRING)


def test_validate_by_auth_rule_without_signatures(looper,  # noqa: F811
                                                  sdk_wallet_client,
                                                  sdk_pool_handle,
                                                  prepare_auth_map):
    with pytest.raises(RequestRejectedException, match="Rule for this action is: {}".format(auth_constraint)):
        """Adding new steward for changed auth rules"""
        add_new_nym(looper,
                    sdk_pool_handle,
                    [sdk_wallet_client],
                    'newSteward2',
                    STEWARD_STRING)
