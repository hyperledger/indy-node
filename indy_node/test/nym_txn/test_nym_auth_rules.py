import pytest
import json

from enum import Enum, unique

from indy.did import create_and_store_my_did, key_for_local_did

from plenum.common.constants import (
    TRUSTEE, STEWARD, NYM, TXN_TYPE, TARGET_NYM, VERKEY, ROLE,
    CURRENT_PROTOCOL_VERSION)
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.signer_did import DidSigner
from plenum.common.member.member import Member
from plenum.test.helper import sdk_gen_request, sdk_sign_request_objects

from indy_common.types import Request
from indy_common.roles import Roles

from indy_node.test.helper import createUuidIdentifierAndFullVerkey


#   TODO
#   - more specific string patterns for auth exc check


class DID(object):
    def __init__(self, did=None, role=Roles.IDENTITY_OWNER, verkey=None, creator=None, wallet_handle=None):
        self.did = did
        self.role = role
        self.verkey = verkey
        self.creator = creator
        self.wallet_handle = wallet_handle

    @property
    def wallet_did(self):
        return (self.wallet_handle, self.did)


@unique
class EnumBase(Enum):
    def __str__(self):
        return self.name


ActionIds = Enum('ActionIds', 'add edit', type=EnumBase)

# params for addition:
# - signer:
#   - role: Roles
# - dest:
#   - verkey in NYM: omitted, None, val
#   - role: Roles, omitted
NYMAddDestRoles = Enum(
    'NYMAddDestRoles',
    [(r.name, r.value) for r in Roles] + [('omitted', 'omitted')],
    type=EnumBase)

NYMAddDestVerkeys = Enum('NYMAddDestVerkeys', 'none val omitted', type=EnumBase)

# params for edition:
# - signer:
#   - [self, creator] + [other], where other = any of Roles
# - dest:
#   - role in ledger: Roles
#   - verkey in ledger: None, val
#   - role: Roles, omitted
#   - verkey in NYM: same, new (not None), demote(None), omitted
LedgerDIDVerkeys = Enum('LedgerDIDVerkeys', 'none val', type=EnumBase)
LedgerDIDRoles = Roles

NYMEditSignerTypes = Enum(
    'NYMEditSignerTypes',
    [(r.name, r.value) for r in Roles] + [('self', 'self'), ('creator', 'creator')],
    type=EnumBase
)

NYMEditDestRoles = NYMAddDestRoles
NYMEditDestVerkeys = Enum('NYMEditDestVerkeys', 'same new demote omitted', type=EnumBase)

dids = {}
did_editor_others = {}
did_provisioners = did_editor_others


# FIXTURES


@pytest.fixture(scope="module")
def trustee(looper, sdk_wallet_trustee):
    wh, did = sdk_wallet_trustee
    verkey = looper.loop.run_until_complete(key_for_local_did(wh, did))
    return DID(did=did, role=Roles.TRUSTEE, verkey=verkey, wallet_handle=wh)


@pytest.fixture(scope="module")
def poolTxnData(looper, poolTxnData, trustee):
    global dids
    global did_editor_others

    # TODO non-Trustee creators

    data = poolTxnData

    def _add_did(role, did_name, with_verkey=True):
        nonlocal data

        data['seeds'][did_name] = did_name + '0' * (32 - len(did_name))
        t_sgnr = DidSigner(seed=data['seeds'][did_name].encode())
        verkey = t_sgnr.full_verkey if with_verkey else None
        data['txns'].append(
            Member.nym_txn(nym=t_sgnr.identifier,
                           verkey=verkey,
                           role=role.value,
                           name=did_name,
                           creator=trustee.did)
        )

        if verkey:
            (sdk_did, sdk_verkey) = looper.loop.run_until_complete(
                create_and_store_my_did(
                    trustee.wallet_handle,
                    json.dumps({'seed': data['seeds'][did_name]}))
            )

        return DID(
            did=t_sgnr.identifier, role=role, verkey=verkey,
            creator=trustee, wallet_handle=trustee.wallet_handle
        )

    params = [(dr, dv) for dr in LedgerDIDRoles for dv in LedgerDIDVerkeys]
    for (dr, dv) in params:
        dids[(dr, dv)] = _add_did(
            dr, "{}-{}".format(dr.name, dv.name),
            with_verkey=(dv == LedgerDIDVerkeys.val)
        )

    for dr in Roles:
        did_editor_others[dr] = _add_did(dr, "{}-other".format(dr.name))

    return data


@pytest.fixture(scope="module", params=list(Roles))
def provisioner_role(request):
    return request.param


@pytest.fixture(scope="module")
def provisioner(poolTxnData, provisioner_role):
    return did_provisioners[provisioner_role]


@pytest.fixture(scope="module", params=list(NYMAddDestRoles))
def nym_add_dest_role(request):
    return request.param


@pytest.fixture(scope="module", params=list(NYMAddDestVerkeys))
def nym_add_dest_verkey(request):
    return request.param


@pytest.fixture(scope="function")
def add_op(nym_add_dest_role, nym_add_dest_verkey):
    did, verkey = createUuidIdentifierAndFullVerkey()

    op = {
        TXN_TYPE: NYM,
        TARGET_NYM: did,
        ROLE: nym_add_dest_role.value,
        VERKEY: verkey
    }

    if nym_add_dest_role == NYMAddDestRoles.omitted:
        del op[ROLE]

    if nym_add_dest_verkey == NYMAddDestVerkeys.omitted:
        del op[VERKEY]

    return op


@pytest.fixture(scope="module", params=list(LedgerDIDRoles))
def edited_ledger_role(request):
    return request.param


@pytest.fixture(scope="module", params=list(LedgerDIDVerkeys))
def edited_ledger_verkey(request):
    return request.param


@pytest.fixture(scope="function")
def edited(edited_ledger_role, edited_ledger_verkey):
    return dids[(edited_ledger_role, edited_ledger_verkey)]


@pytest.fixture(scope="module", params=list(NYMEditDestRoles))
def edited_nym_role(request):
    return request.param


@pytest.fixture(scope="module", params=list(NYMEditDestVerkeys))
def edited_nym_verkey(request):
    return request.param


@pytest.fixture(scope="module", params=list(NYMEditSignerTypes))
def editor_type(request):
    return request.param


@pytest.fixture(scope="function")
def editor(editor_type, edited):
    if editor_type == NYMEditSignerTypes.self:
        return edited
    elif editor_type == NYMEditSignerTypes.creator:
        return edited.creator
    else:
        return did_editor_others[Roles(editor_type.value)]


@pytest.fixture(scope="function")
def edit_op(edited, edited_nym_role, edited_nym_verkey):
    op = {
        TXN_TYPE: NYM,
        TARGET_NYM: edited.did,
    }

    if edited_nym_role != NYMEditDestRoles.omitted:
        op[ROLE] = edited_nym_role.value

    if edited_nym_verkey == NYMEditDestVerkeys.same:
        op[VERKEY] = edited.verkey
    elif edited_nym_verkey == NYMEditDestVerkeys.new:
        _, op[VERKEY] = createUuidIdentifierAndFullVerkey()
    elif edited_nym_verkey == NYMEditDestVerkeys.demote:
        if edited.verkey is None:
            return None  # pass that case since it is covered by `same` case as well
        else:
            op[VERKEY] = None

    return op


# TEST HELPERS

def auth_check(action_id, signer, op, did_ledger=None):
    op_role = Roles(op[ROLE]) if ROLE in op else None

    def check_promotion():
        # omitted role means IDENTITY_OWNER
        if op_role in (None, Roles.IDENTITY_OWNER):
            return signer.role in (Roles.TRUSTEE, Roles.STEWARD, Roles.ENDORSER)
        elif op_role in (Roles.TRUSTEE, Roles.STEWARD):
            return signer.role == Roles.TRUSTEE
        elif op_role in (Roles.ENDORSER, Roles.NETWORK_MONITOR):
            return signer.role in (Roles.TRUSTEE, Roles.STEWARD)

    def check_demotion():
        if did_ledger.role in (Roles.TRUSTEE, Roles.STEWARD):
            return signer.role == Roles.TRUSTEE
        elif did_ledger.role == Roles.ENDORSER:
            return (signer.role == Roles.TRUSTEE)
            # FIXME INDY-1968: uncomment when the task is addressed
            # return ((signer.role == Roles.TRUSTEE) or
            #        (signer.role == Roles.ENDORSER and
            #            is_self and is_owner))
        elif did_ledger.role == Roles.NETWORK_MONITOR:
            return signer.role in (Roles.TRUSTEE, Roles.STEWARD)

    if action_id == ActionIds.add:
        return check_promotion()

    elif action_id == ActionIds.edit:
        # is_self = signer.did == did_ledger.did
        is_owner = signer == (did_ledger if did_ledger.verkey is not None else
        did_ledger.creator)

        if (VERKEY in op) and (not is_owner):
            return False

        if ROLE in op:
            if op_role == did_ledger.role:
                # FIXME INDY-1969: related to the task
                return is_owner  # TODO what is a case here, is it correctly designed

            elif op_role == Roles.IDENTITY_OWNER:  # demotion of existent DID
                return check_demotion()

            elif did_ledger.role == Roles.IDENTITY_OWNER:  # promotion of existent DID
                return check_promotion()

            else:  # role updating: demotion + promotion
                return (check_demotion() and check_promotion())
        else:
            return True

    return False


def sign_and_validate(looper, node, action_id, signer, op, did_ledger=None):
    req_obj = sdk_gen_request(op, protocol_version=CURRENT_PROTOCOL_VERSION,
                              identifier=signer.did)
    s_req = sdk_sign_request_objects(looper, signer.wallet_did, [req_obj])[0]

    request = Request(**json.loads(s_req))

    if auth_check(action_id, signer, op, did_ledger):
        node.write_manager.dynamic_validation(request, 0)
    else:
        with pytest.raises(UnauthorizedClientRequest):
            node.write_manager.dynamic_validation(request, 0)


# TESTS
# Note. some fixtures are referred explicitly just to make test nodeid names predictable

def test_nym_add(
        provisioner_role, nym_add_dest_role, nym_add_dest_verkey,
        looper, txnPoolNodeSet,
        provisioner, add_op):
    sign_and_validate(looper, txnPoolNodeSet[0], ActionIds.add, provisioner, add_op)


def test_nym_edit(
        edited_ledger_role, edited_ledger_verkey, editor_type,
        edited_nym_role, edited_nym_verkey,
        looper, txnPoolNodeSet,
        editor, edited, edit_op):
    if edit_op is None:  # might be None, means a duplicate test case
        return

    if editor.verkey is None:  # skip that as well since it doesn't make sense
        return

    sign_and_validate(looper, txnPoolNodeSet[0], ActionIds.edit, editor, edit_op, did_ledger=edited)
