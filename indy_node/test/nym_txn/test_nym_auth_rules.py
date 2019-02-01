import sys
import pytest
import json

from enum import Enum, unique

from indy.did import create_and_store_my_did

from plenum.common.constants import (
    TRUSTEE, STEWARD, NYM, TXN_TYPE, TARGET_NYM, VERKEY, ROLE,
    CURRENT_PROTOCOL_VERSION)
from plenum.common.exceptions import RequestRejectedException, UnauthorizedClientRequest
from plenum.test.helper import sdk_gen_request, sdk_sign_request_objects, sdk_sign_and_submit_op, sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_common.types import Request
from indy_common.roles import Roles
from indy_node.test.helper import createHalfKeyIdentifierAndAbbrevVerkey

#   TODO
#   - more specific string patterns for auth exc check
#   - mixed cases: both verkey and role are presented in NYM txn
#     ??? possibly not necessary for now since role and verkey related constrains
#     are composed like logical AND validation fails if any of them fails
#   - ANYONE_CAN_WRITE=True case


# params for add:
# - signer:
#   - role: Roles
# - dest:
#   - verkey in NYM: omitted, None, val
#   - role: Roles, omitted


# params for edit:
# - signer:
#   - role: Roles
#   - is_creator / is_other / is_self
# - dest:
#   - verkey in ledger: None, val
#   - verkey in NYM: same, new, omitted
#   - role in ledger: Roles
#   - role: Roles, omitted


# FIXTURES

class EnumBase(Enum):
    def __str__(self):
        return self.name


@unique
class ActionIds(EnumBase):
    add = 0
    demote = 1
    rotate = 2


@unique
class Demotions(EnumBase):
    # other DID-without-verkey created by the demoter
    self_created_no_verkey = 1
    # other DID-with-verkey created by the demoter
    self_created_verkey = 2
    # other DID-without-verkey created by other
    other_created_no_verkey = 3
    # other DID-with-verkey created by other
    other_created_verkey = 4


@unique
class Rotations(EnumBase):
    none_val = 1
    val_val = 2
    val_none = 3
    none_none = 4


@unique
class Rotator(EnumBase):
    self = 1
    creator = 2
    other = 3


# FIXME class name
class DIDWallet(object):
    def __init__(self, did=None, role=Roles.IDENTITY_OWNER, verkey=None, creator=None, wallet_handle=None):
        self.did = did
        self.role = role
        self.verkey = verkey
        self.creator = creator
        self.wallet_handle = wallet_handle

    @property
    def wallet_did(self):
        return (self.wallet_handle, self.did)


def auth_check(action_id, signer, dest):

    # is_self = signer.did == dest.did
    is_owner = signer == (dest if dest.verkey is not None else dest.creator)

    if action_id == ActionIds.add:
        if dest.role in (Roles.TRUSTEE, Roles.STEWARD):
            return signer.role == Roles.TRUSTEE
        elif dest.role in (Roles.TRUST_ANCHOR, Roles.NETWORK_MONITOR):
            return signer.role in (Roles.TRUSTEE, Roles.STEWARD)
        elif dest.role == Roles.IDENTITY_OWNER:
            return signer.role in (Roles.TRUSTEE, Roles.STEWARD, Roles.TRUST_ANCHOR)

    elif action_id == ActionIds.demote:
        if dest.role in (Roles.TRUSTEE, Roles.STEWARD):
            return signer.role == Roles.TRUSTEE
        elif dest.role == Roles.TRUST_ANCHOR:
            return (signer.role == Roles.TRUSTEE)
            # FIXME INDY-1968: uncomment when the task is addressed
            # return ((signer.role == Roles.TRUSTEE) or
            #        (signer.role == Roles.TRUST_ANCHOR and
            #            is_self and is_owner))
        elif dest.role == Roles.NETWORK_MONITOR:
            return signer.role in (Roles.TRUSTEE, Roles.STEWARD)
        # FIXME INDY-1969: remove when the task is addressed
        elif dest.role == Roles.IDENTITY_OWNER:
            return is_owner

    elif action_id == ActionIds.rotate:
        return is_owner

    return False


def create_new_did(looper, sdk_pool_handle, creator, role, skipverkey=False):

    op = {
        TXN_TYPE: NYM,
        ROLE: role.value
    }

    new_did_verkey = None

    if skipverkey:
        new_did, _ = createHalfKeyIdentifierAndAbbrevVerkey()
        op.update({TARGET_NYM: new_did})
    else:
        new_did, new_did_verkey = looper.loop.run_until_complete(
            create_and_store_my_did(creator.wallet_handle, "{}"))

    op.update({TARGET_NYM: new_did, VERKEY: new_did_verkey})

    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, creator.wallet_did, op)
    sdk_get_and_check_replies(looper, [req])

    return DIDWallet(did=new_did, role=role, verkey=new_did_verkey,
                     creator=creator, wallet_handle=creator.wallet_handle)


@pytest.fixture(scope="module")
def trustee(sdk_wallet_trustee):
    return DIDWallet(did=sdk_wallet_trustee[1], role=Roles.TRUSTEE, wallet_handle=sdk_wallet_trustee[0])


def did_fixture_wrapper():
    def _fixture(looper, sdk_pool_handle, txnPoolNodeSet, trustee, request):
        marker = request.node.get_marker('skip_did_verkey')
        return create_new_did(looper, sdk_pool_handle, trustee, request.param,
                              skipverkey=(marker is not None))
    return _fixture


# adds did_per_module and did_per_function fixtures
for scope in ('module', 'function'):
    setattr(
        sys.modules[__name__],
        "did_per_{}".format(scope),
        pytest.fixture(scope=scope, params=list(Roles))(did_fixture_wrapper()))


@pytest.fixture(scope="module")
def provisioner(did_per_module):
    return did_per_module


@pytest.fixture(scope="module", params=list(Roles) + [None],
                ids=lambda r: str(r) if r else 'omitted_role')
def provisioned_role(request):
    return request.param


@pytest.fixture(scope="function")
def provisioned(provisioned_role):
    did, verkey = createHalfKeyIdentifierAndAbbrevVerkey()
    return (
        DIDWallet(
            did=did,
            role=provisioned_role if provisioned_role else Roles.IDENTITY_OWNER,
            verkey=verkey),
        provisioned_role is None)


# scope is 'function' since demoter demotes
# themselves at the end of the each demotion test
@pytest.fixture(scope="function")
def demoter(did_per_function):
    return did_per_function


@pytest.fixture(scope="function",
                params=[(x, y) for x in Demotions for y in Roles] + [None],
                ids=lambda p: "{}-{}".format(p[0], p[1]) if p else 'self')
def demotion(request):
    return request.param


@pytest.fixture(scope="function")
def demoted(looper, sdk_pool_handle, txnPoolNodeSet, trustee, demoter, demotion):
    if demotion is None:  # self demotion
        return demoter
    else:
        demotion_type, role = demotion
        if demotion_type == Demotions.self_created_no_verkey:
            if auth_check(ActionIds.add, demoter, DIDWallet(role=role)):
                return create_new_did(looper, sdk_pool_handle, demoter, role, skipverkey=True)
        elif demotion_type == Demotions.self_created_verkey:
            if auth_check(ActionIds.add, demoter, DIDWallet(role=role)):
                return create_new_did(looper, sdk_pool_handle, demoter, role)
        elif demotion_type == Demotions.other_created_no_verkey:
            return create_new_did(looper, sdk_pool_handle, trustee, role, skipverkey=True)
        elif demotion_type == Demotions.other_created_verkey:
            return create_new_did(looper, sdk_pool_handle, trustee, role)


# Note. dedicated trustee is used to test rotations by other
# (not creator and not self). Other other-rotators (e.g. TRUST_ANCHOR)
# are ignored as less powerful.
@pytest.fixture(scope="module")
def trustee_not_creator(looper, sdk_pool_handle, txnPoolNodeSet, trustee):
    return create_new_did(looper, sdk_pool_handle, trustee, Roles.TRUSTEE)


@pytest.fixture(scope="function", params=list(Rotations))
def rotation_verkey(request):
    if request.param in (Rotations.none_none, Rotations.none_val):
        request.node.add_marker('skip_did_verkey')

    verkey = None
    if request.param in (Rotations.val_val, Rotations.none_val):
        _, verkey_ = createHalfKeyIdentifierAndAbbrevVerkey()

    return verkey


@pytest.fixture(scope="function", params=list(Rotator))
def rotator(did_per_function, trustee_not_creator, request):
    if request.param == Rotator.self:
        return did_per_function
    elif request.param == Rotator.creator:
        return did_per_function.creator
    elif request.param == Rotator.other:
        return trustee_not_creator


@pytest.fixture(scope="function")
def rotated(did_per_function):
    return did_per_function


# TEST HELPERS

def sign_submit_check(looper, node, signer, dest, action_id, op):
    req_obj = sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                              identifier=signer.did)
    s_req = sdk_sign_request_objects(looper, signer.wallet_did, [req_obj])[0]

    request = Request(**json.loads(s_req))

    if auth_check(action_id, signer, dest):
        node.get_req_handler(txn_type=NYM).validate(request)
    else:
        with pytest.raises(UnauthorizedClientRequest):
            node.get_req_handler(txn_type=NYM).validate(request)


def add(looper, node, provisioner, provisioned, omit_role=False):
    op = {
        TXN_TYPE: NYM,
        TARGET_NYM: provisioned.did,
        VERKEY: provisioned.verkey,
    }

    if not omit_role:
        op[ROLE] = provisioned.role.value

    sign_submit_check(looper, node, provisioner, provisioned, ActionIds.add, op)


def demote(looper, node, demoter, demoted):
    op = {
        TXN_TYPE: NYM,
        TARGET_NYM: demoted.did,
        ROLE: None
    }

    sign_submit_check(looper, node, demoter, demoted, ActionIds.demote, op)


def rotate(looper, node, rotator, rotated, new_verkey):
    op = {
        TXN_TYPE: NYM,
        TARGET_NYM: rotated.did,
        VERKEY: new_verkey
    }

    sign_submit_check(looper, node, rotator, rotated, ActionIds.rotate, op)


# TESTS

def test_nym_add(looper, txnPoolNodeSet, provisioner, provisioned):
    provisioned, omit_role = provisioned
    add(looper, txnPoolNodeSet[0], provisioner, provisioned, omit_role=omit_role)


# Demotion is considered as NYM with only 'role' field specified and it's None.
# If NYM includes 'verkey' field as well it mixes role demotion/promotion and
# verkey rotation and should be checked separately.
def test_nym_demote(looper, txnPoolNodeSet, demoter, demoted):
    # might be None for cases 'self_created_no_verkey' and 'self_created_verkey' or self demotion
    if demoted:
        demote(looper, txnPoolNodeSet[0], demoter, demoted)


def test_nym_rotate(looper, txnPoolNodeSet, rotator, rotated, rotation_verkey):
    rotate(looper, txnPoolNodeSet[0], rotator, rotated, rotation_verkey)
