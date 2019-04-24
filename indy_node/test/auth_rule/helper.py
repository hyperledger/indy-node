import json

from indy.did import create_and_store_my_did

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.constants import AUTH_RULE, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, OLD_VALUE, NYM, \
    TRUST_ANCHOR
from plenum.common.constants import TRUSTEE, TXN_TYPE

from indy_common.authorize.auth_constraints import CONSTRAINT_ID, ROLE, SIG_COUNT, NEED_TO_BE_OWNER, METADATA, \
    ConstraintsEnum, AUTH_CONSTRAINTS
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_and_submit_req_obj, sdk_get_and_check_replies, sdk_gen_request, \
    sdk_multi_sign_request_objects, sdk_json_to_request_object, sdk_send_signed_requests
from plenum.test.pool_transactions.helper import prepare_nym_request


def generate_constraint_entity(constraint_id=ConstraintsEnum.ROLE_CONSTRAINT_ID,
                               role=TRUSTEE,
                               sig_count=1,
                               need_to_be_owner=False,
                               metadata={}):
    return {CONSTRAINT_ID: constraint_id,
            ROLE: role,
            SIG_COUNT: sig_count,
            NEED_TO_BE_OWNER: need_to_be_owner,
            METADATA: metadata}


def generate_constraint_list(constraint_id=ConstraintsEnum.AND_CONSTRAINT_ID,
                             auth_constraints=None):
    auth_constraints = generate_constraint_entity() \
        if auth_constraints is None \
        else auth_constraints
    return {CONSTRAINT_ID: constraint_id,
            AUTH_CONSTRAINTS: auth_constraints}


def generate_auth_rule_operation(auth_action=ADD_PREFIX, auth_type=NYM,
                                 field=ROLE, new_value=TRUST_ANCHOR,
                                 old_value=None, constraint=None):
    constraint = generate_constraint_entity() \
        if constraint is None \
        else constraint
    op = {TXN_TYPE: AUTH_RULE,
          CONSTRAINT: constraint,
          AUTH_ACTION: auth_action,
          AUTH_TYPE: auth_type,
          FIELD: field,
          NEW_VALUE: new_value
          }
    if old_value or auth_action == EDIT_PREFIX:
        op[OLD_VALUE] = old_value
    return op


def create_verkey_did(looper, wh):
    seed = randomString(32)
    return looper.loop.run_until_complete(
        create_and_store_my_did(wh, json.dumps({'seed': seed})))


def sdk_send_and_check_auth_rule_request(looper, sdk_wallet_trustee, sdk_pool_handle,
                                         auth_action=ADD_PREFIX, auth_type=NYM,
                                         field=ROLE, new_value=TRUST_ANCHOR,
                                         old_value=None, constraint=None, no_wait=False):
    op = generate_auth_rule_operation(auth_action, auth_type,
                                      field, new_value,
                                      old_value, constraint)

    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req = sdk_sign_and_submit_req_obj(looper,
                                      sdk_pool_handle,
                                      sdk_wallet_trustee,
                                      req_obj)
    if no_wait:
        return req
    resp = sdk_get_and_check_replies(looper, [req])
    return resp


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
    # waiting for replies
    sdk_get_and_check_replies(looper, [request_couple])