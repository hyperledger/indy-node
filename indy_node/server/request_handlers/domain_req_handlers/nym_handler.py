from binascii import hexlify

from common.serializers.serialization import domain_state_serializer
from indy_common.state import domain
from indy_common.roles import Roles
from indy_common.constants import NYM
from indy_common.auth import Authoriser
from ledger.util import F

from plenum.common.constants import ROLE, TARGET_NYM, TRUSTEE, VERKEY, DOMAIN_LEDGER_ID, TXN_TIME

from plenum.common.exceptions import InvalidClientRequest, UnknownIdentifier, UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_seq_no, get_txn_time, get_request_data, get_from
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import nym_to_state_key, get_nym_details


class NymHandler(WriteRequestHandler):
    state_serializer = domain_state_serializer

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, NYM, DOMAIN_LEDGER_ID)

    def static_validation(self, request: Request):
        self._validate_request_type(request)
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
        self._validate_request_type(request)
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
        self._validate_txn_type(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        binary_digest = domain.make_state_path_for_nym(nym)
        return hexlify(binary_digest).decode()

    def _update_state_with_single_txn(self, txn, is_committed=True):
        self._validate_txn_type(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        existing_data = get_nym_details(self.state, nym,
                                        is_committed=is_committed)
        txn_data = get_payload_data(txn)
        new_data = {}
        if not existing_data:
            new_data[f.IDENTIFIER.nm] = get_from(txn)
            new_data[ROLE] = None
            new_data[VERKEY] = None

        if ROLE in txn_data:
            new_data[ROLE] = txn_data[ROLE]
        if VERKEY in txn_data:
            new_data[VERKEY] = txn_data[VERKEY]
        new_data[F.seqNo.name] = get_seq_no(txn)
        new_data[TXN_TIME] = get_txn_time(txn)
        existing_data.update(new_data)
        val = self.state_serializer.serialize(existing_data)
        key = nym_to_state_key(nym)
        self.state.set(key, val)
        txn_time = get_txn_time(txn)
        self.database_manager.idr_cache.set(nym,
                                            seqNo=get_seq_no(txn),
                                            txnTime=txn_time,
                                            ta=existing_data.get(f.IDENTIFIER.nm),
                                            role=existing_data.get(ROLE),
                                            verkey=existing_data.get(VERKEY),
                                            isCommitted=is_committed)
        return existing_data

    def _validate_new_nym(self, identifier, req_id, operation, origin_role):
        role = operation.get(ROLE)
        r, msg = Authoriser.authorised(NYM,
                                       origin_role,
                                       field=ROLE,
                                       oldVal=None,
                                       newVal=role)
        if not r:
            raise UnauthorizedClientRequest(
                identifier,
                req_id,
                "{} cannot add {}".format(
                    Roles.nameFromValue(origin_role),
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
