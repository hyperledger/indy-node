from binascii import hexlify

from indy_common.state import domain

from indy_common.roles import Roles

from indy_common.constants import NYM

from indy_common.auth import Authoriser
from plenum.common.constants import ROLE, TARGET_NYM, TRUSTEE, VERKEY, TXN_TIME

from plenum.common.exceptions import InvalidClientRequest, UnknownIdentifier, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_from, get_seq_no, get_txn_time, get_request_data
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.nym_handler import NymHandler as PNymHandler


class NymHandler(PNymHandler):

    def __init__(self, config, database_manager: DatabaseManager):
        super().__init__(config, database_manager)

    def static_validation(self, request: Request):
        self._validate_type(request)
        identifier, req_id, operation = get_request_data(request)
        role = operation.get(ROLE)
        nym = operation.get(TARGET_NYM)
        if isinstance(nym, str):
            nym = nym.strip()
        if not nym:
            raise InvalidClientRequest(identifier, req_id,
                                       "{} needs to be present".
                                       format(TARGET_NYM))
        if not Authoriser.isValidRole(role):
            raise InvalidClientRequest(identifier, req_id,
                                       "{} not a valid role".
                                       format(role))

    def dynamic_validation(self, request: Request):
        self._validate_type(request)
        identifier, req_id, operation = get_request_data(request)
        try:
            origin_role = self.database_manager.idr_cache.getRole(
                identifier, isCommitted=False) or None
        except BaseException:
            raise UnknownIdentifier(
                identifier,
                req_id)

        nym_data = self.database_manager.idr_cache.getNym(operation[TARGET_NYM], isCommitted=False)
        if not nym_data:
            # If nym does not exist
            self._validate_new_nym(identifier, req_id, operation, origin_role)
        else:
            self._validate_existing_nym(identifier, req_id, operation, origin_role, nym_data)

    def gen_txn_path(self, txn):
        nym = get_payload_data(txn).get(TARGET_NYM)
        binary_digest = domain.make_state_path_for_nym(nym)
        return hexlify(binary_digest).decode()

    def _update_state_with_single_txn(self, txn, isCommitted=False):
        txn_data = get_payload_data(txn)
        nym = txn_data.get(TARGET_NYM)
        data = {
            f.IDENTIFIER.nm: get_from(txn),
            f.SEQ_NO.nm: get_seq_no(txn),
            TXN_TIME: get_txn_time(txn)
        }
        if ROLE in txn_data:
            data[ROLE] = txn_data.get(ROLE)
        if VERKEY in txn_data:
            data[VERKEY] = txn_data.get(VERKEY)
        self.update_nym(nym, txn, isCommitted=isCommitted)

    def update_nym(self, nym, txn, isCommitted=True):
        updatedData = super().update_nym(nym, txn, isCommitted=isCommitted)
        txn_time = get_txn_time(txn)
        self.database_manager.idr_cache.set(nym,
                                            seqNo=get_seq_no(txn),
                                            txnTime=txn_time,
                                            ta=updatedData.get(f.IDENTIFIER.nm),
                                            role=updatedData.get(ROLE),
                                            verkey=updatedData.get(VERKEY),
                                            isCommitted=isCommitted)

    def _validate_new_nym(self, identifier, req_id, operation, originRole):
        role = operation.get(ROLE)
        r, msg = Authoriser.authorised(NYM,
                                       originRole,
                                       field=ROLE,
                                       oldVal=None,
                                       newVal=role)
        if not r:
            raise UnauthorizedClientRequest(
                identifier,
                req_id,
                "{} cannot add {}".format(
                    Roles.nameFromValue(originRole),
                    Roles.nameFromValue(role))
            )

    def _validate_existing_nym(self, identifier, req_id, op, origin_role, nym_data):
        unauthorized = False
        reason = None
        owner = self.database_manager.idr_cache.getOwnerFor(op[TARGET_NYM], isCommitted=False)
        is_owner = identifier == owner

        if not origin_role == TRUSTEE and not is_owner:
            reason = '{} is neither Trustee nor owner of {}' \
                .format(identifier, op[TARGET_NYM])
            unauthorized = True

        if not unauthorized:
            update_keys = [ROLE, VERKEY]
            for key in update_keys:
                if key in op:
                    new_val = op[key]
                    old_val = nym_data.get(key)
                    if old_val != new_val:
                        r, msg = Authoriser.authorised(NYM, origin_role, field=key,
                                                       oldVal=old_val, newVal=new_val,
                                                       isActorOwnerOfSubject=is_owner)
                        if not r:
                            unauthorized = True
                            reason = "{} cannot update {}". \
                                format(Roles.nameFromValue(origin_role), key)
                            break
        if unauthorized:
            raise UnauthorizedClientRequest(
                identifier, req_id, reason)
