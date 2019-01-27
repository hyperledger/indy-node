import pytest

from enum import Enum, unique

from indy.did import create_and_store_my_did

from plenum.common.constants import TRUSTEE, STEWARD, NYM
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_sign_and_submit_op, sdk_get_and_check_replies
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_common.constants import CLIENT, TRUST_ANCHOR, NETWORK_MONITOR
from indy_common.roles import Roles
from indy_node.test.helper import createHalfKeyIdentifierAndAbbrevVerkey


# FIXME terms
#   - add/create/provision
#   - remove/demote/revoke/blacklist/suspend/flush
#   - owner/holder
#   - signer/initiator ???
#
#
#   TODO
#   - more specific string patterns for auth exc check
#   - DRY: send requests and check replies
#
#
#   - ptomoter after demotion


# FIXTURES


@unique
class ActionIds(Enum):
    add = 0
    demote = 1


@unique
class Demotions(Enum):
    # other DID-without-verkey created by the demoter
    self_created_no_verkey = 1
    # other DID-with-verkey created by the demoter
    self_created_verkey = 2
    # other DID-without-verkey created by other
    other_created_no_verkey = 3
    # other DID-with-verkey created by other
    other_created_verkey = 4


# FIXME class name
class DIDWallet(object):
    def __init__(self, did=None, role=Roles.CLIENT, verkey=None, creator=None, wallet_handle=None):
        self.did = did
        self.role = role
        self.verkey = verkey
        self.creator = creator
        self.wallet_handle = wallet_handle

    @property
    def wallet_did(self):
        return (self.wallet_handle, self.did)


def auth_check(action_id, signer, dest):

    is_self = signer.did == dest.did
    # is_creator = signer.did == dest.creator.did
    dest_with_verkey = dest.verkey is not None

    if action_id == ActionIds.add:
        if signer.role == Roles.TRUSTEE:
            return True
        elif (signer.role == Roles.STEWARD and
                dest.role in (Roles.CLIENT, Roles.TRUST_ANCHOR, Roles.NETWORK_MONITOR)):
            return True
        elif signer.role == Roles.TRUST_ANCHOR and dest.role == Roles.CLIENT:
            return True

    elif action_id == ActionIds.demote:
        if signer.role == Roles.TRUSTEE:
            return True
        elif (signer.role == Roles.TRUST_ANCHOR and dest.role == Roles.TRUST_ANCHOR and
              is_self and dest_with_verkey):
            return True

    return False


@pytest.fixture(scope="module")
def client(sdk_wallet_client):
    return DIDWallet(did=sdk_wallet_client[1], role=Roles.CLIENT, wallet_handle=sdk_wallet_client[0])


@pytest.fixture(scope="module")
def trustee(sdk_wallet_trustee):
    return DIDWallet(did=sdk_wallet_trustee[1], role=Roles.TRUSTEE, wallet_handle=sdk_wallet_trustee[0])


@pytest.fixture(scope="module")
def steward(sdk_wallet_steward):
    return DIDWallet(did=sdk_wallet_steward[1], role=Roles.STEWARD, wallet_handle=sdk_wallet_steward[0])


def idfn_enum(item):
    return item.name


def _create_new_nym(looper, sdk_pool_handle, creator, role, *args, **kwargs):
    new_did, new_did_verkey = looper.loop.run_until_complete(
        create_and_store_my_did(creator.wallet_handle, "{}"))

    op = {'type': NYM,
          'dest': new_did,
          'role': role.value,
          'verkey': new_did_verkey}
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, (creator.wallet_handle, creator.did), op)
    sdk_get_and_check_replies(looper, [req])

    return DIDWallet(did=new_did, role=role, verkey=new_did_verkey, creator=creator, wallet_handle=creator.wallet_handle)


@pytest.fixture(scope="module",
                params=[Roles.CLIENT, Roles.TRUSTEE, Roles.STEWARD],
                ids=idfn_enum)
def provisioner(request, client, trustee, steward):
    # TODO
    #   - wallets for TRUST_ANCHOR and NETWORK_MONITOR
    return {
        Roles.CLIENT: client,
        Roles.TRUSTEE: trustee,
        Roles.STEWARD: steward,
    }[request.param]


# scope is 'function' since demoter demotes
# themselves at the end of the each demotion test
@pytest.fixture(scope="function",
                params=list(Roles),
                ids=idfn_enum)
def demoter(looper, sdk_pool_handle, txnPoolNodeSet, trustee, request):
    return _create_new_nym(looper, sdk_pool_handle, trustee, request.param)


@pytest.fixture(scope="module", params=list(Roles), ids=idfn_enum)
def role(request):
    return request.param


@pytest.fixture(scope="function")
def nym_op():
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    return {
        'type': NYM,
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
    }


@pytest.fixture(scope="function",
                params=list(Demotions),
                ids=idfn_enum)
# TODO parametrize by verkey in op
def demoted(looper, sdk_pool_handle, txnPoolNodeSet, trustee, demoter, role, request):
    if request.param == Demotions.self_created_no_verkey:
        if auth_check(ActionIds.add, demoter, DIDWallet(role=role)):
            return _create_new_nym(looper, sdk_pool_handle, demoter, role, skipverkey=True)
    elif request.param == Demotions.self_created_verkey:
        if auth_check(ActionIds.add, demoter, DIDWallet(role=role)):
            return _create_new_nym(looper, sdk_pool_handle, demoter, role)
    elif request.param == Demotions.other_created_no_verkey:
        return _create_new_nym(looper, sdk_pool_handle, trustee, role, skipverkey=True)
    elif request.param == Demotions.other_created_verkey:
        return _create_new_nym(looper, sdk_pool_handle, trustee, role)


# TEST HELPERS

def sign_submit_check(looper, sdk_pool_handle, signer, dest, action_id, op):
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, signer.wallet_did, op)

    if auth_check(action_id, signer, dest):
        sdk_get_and_check_replies(looper, [req])
    else:
        with pytest.raises(RequestRejectedException) as excinfo:
            sdk_get_and_check_replies(looper, [req])
        excinfo.match('UnauthorizedClientRequest')


def demote(looper, sdk_pool_handle, txnPoolNodeSet,
           demoter, demoted):

    op = {
        'type': NYM,
        'dest': demoted.did,
        'role': None
    }

    sign_submit_check(looper, sdk_pool_handle, demoter,
                      demoted, ActionIds.demote, op)

# TESTS


def test_add_nym(looper, sdk_pool_handle, txnPoolNodeSet, nym_op, provisioner, role):
    nym_op['role'] = role.value
    sign_submit_check(looper, sdk_pool_handle, provisioner, DIDWallet(role=role), ActionIds.add, nym_op)


def test_add_nym_omitted_role(looper, sdk_pool_handle, txnPoolNodeSet, nym_op, provisioner):
    sign_submit_check(looper, sdk_pool_handle, provisioner, DIDWallet(role=role), ActionIds.add, nym_op)


# TODO parametrize by verkey in op
def test_demote_self_nym(
        looper, sdk_pool_handle, txnPoolNodeSet,
        demoter):
    demote(looper, sdk_pool_handle, txnPoolNodeSet, demoter, demoter)


# TODO parametrize by verkey in op
def test_demote_nym(
        looper, sdk_pool_handle, txnPoolNodeSet,
        demoter, demoted):
    if demoted:
        demote(looper, sdk_pool_handle, txnPoolNodeSet, demoter, demoted)
