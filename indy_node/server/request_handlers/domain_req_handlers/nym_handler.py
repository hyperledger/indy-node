from binascii import hexlify
from typing import Optional

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import NYM
from indy_common.auth import Authoriser
from ledger.util import F

from plenum.common.constants import ROLE, TARGET_NYM, VERKEY, TXN_TIME
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_seq_no, get_txn_time, get_request_data, get_from
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.nym_handler import NymHandler as PNymHandler
from plenum.server.request_handlers.utils import nym_to_state_key, get_nym_details


class NymHandler(PNymHandler):
    state_serializer = domain_state_serializer

    def __init__(self, config, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(config, database_manager)
        self.write_req_validator = write_req_validator

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

    def additional_dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)
        operation = request.operation

        nym_data = self.database_manager.idr_cache.getNym(operation[TARGET_NYM], isCommitted=False)
        if not nym_data:
            # If nym does not exist
            self._validate_new_nym(request, operation)
        else:
            self._validate_existing_nym(request, operation, nym_data)

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        binary_digest = self.make_state_path_for_nym(nym)
        return hexlify(binary_digest).decode()

    def update_state(self, txn, prev_result, request, is_committed=False):
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
        return existing_data

    def _validate_new_nym(self, request, operation):
        identifier, req_id, _ = get_request_data(request)
        role = operation.get(ROLE)

        nym_data = self.database_manager.idr_cache.getNym(request.identifier, isCommitted=False)
        if not nym_data:
            # Non-ledger nym case. These two checks duplicated and mainly executed in client_authn,
            # but it has point to repeat them here, for clear understanding of validation non-ledger request cases.
            if request.identifier != request.operation.get(TARGET_NYM):
                raise InvalidClientRequest(identifier, req_id, "DID which is not stored on ledger can "
                                                               "send nym txn only if appropriate auth_rules set "
                                                               "and sender did equal to destination nym")
            if not request.operation.get(VERKEY):
                raise InvalidClientRequest(identifier, req_id, "Non-ledger nym txn must contain verkey for new did")

        self.write_req_validator.validate(request,
                                          [AuthActionAdd(txn_type=NYM,
                                                         field=ROLE,
                                                         value=role)])

    def _validate_existing_nym(self, request, operation, nym_data):
        origin = request.identifier
        owner = self.database_manager.idr_cache.getOwnerFor(operation[TARGET_NYM], isCommitted=False)
        is_owner = origin == owner

        updateKeys = [ROLE, VERKEY]
        updateKeysInOperationOrOwner = is_owner
        for key in updateKeys:
            if key in operation:
                updateKeysInOperationOrOwner = True
                newVal = operation[key]
                oldVal = nym_data.get(key)
                self.write_req_validator.validate(request,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=key,
                                                                  old_value=oldVal,
                                                                  new_value=newVal,
                                                                  is_owner=is_owner)])
        if not updateKeysInOperationOrOwner:
            raise InvalidClientRequest(request.identifier, request.reqId)

    def _decode_state_value(self, encoded):
        if encoded:
            return domain_state_serializer.deserialize(encoded)
        return None, None, None
