from plenum.common.constants import TARGET_NYM, TXN_TYPE, NYM, ROLE, VERKEY, \
    CURRENT_PROTOCOL_VERSION
from plenum.common.signer_did import DidIdentity
from stp_core.types import Identifier
from indy_common.auth import Authoriser

from indy_common.generates_request import GeneratesRequest
from indy_common.constants import GET_NYM, NULL
from indy_common.types import Request


class Identity(GeneratesRequest):
    def __init__(self,
                 identifier: Identifier,
                 endorser: Identifier = None,
                 verkey=None,
                 role=None,
                 last_synced=None,
                 seq_no=None):
        """

        :param identifier:
        :param endorser:
        :param verkey:
        :param role: If role is explicitly passed as `null` then in the request
         to ledger, `role` key would be sent as None which would stop the
         Identity's ability to do any privileged actions. If role is not passed,
          `role` key will not be included in the request to the ledger
        :param last_synced:
        :param seq_no:
        """

        self.identity = DidIdentity(identifier, verkey=verkey)
        self.endorser = endorser

        # if role and role not in (ENDORSER, STEWARD):
        if not Authoriser.isValidRole(self.correctRole(role)):
            raise AttributeError("Invalid role {}".format(role))
        self._role = role

        # timestamp for when the ledger was last checked for key replacement or
        # revocation
        self.last_synced = last_synced

        # sequence number of the latest key management transaction for this
        # identifier
        self.seqNo = seq_no

    @property
    def identifier(self):
        return self.identity.identifier

    @property
    def verkey(self):
        return self.identity.verkey

    @verkey.setter
    def verkey(self, new_val):
        identifier = self.identifier
        self.identity = DidIdentity(identifier, verkey=new_val)

    @staticmethod
    def correctRole(role):
        return None if role == NULL else role

    @property
    def role(self):
        return self.correctRole(self._role)

    @role.setter
    def role(self, role):
        if not Authoriser.isValidRole(self.correctRole(role)):
            raise AttributeError("Invalid role {}".format(role))
        self._role = role

    def _op(self):
        op = {
            TXN_TYPE: NYM,
            TARGET_NYM: self.identity.identifier
        }
        if self.identity.verkey is not None:
            op[VERKEY] = None if self.identity.verkey == '' else self.identity.verkey
        if self._role:
            op[ROLE] = self.role
        return op

    def ledgerRequest(self):
        if not self.seqNo:
            assert self.identity.identifier is not None
            return Request(identifier=self.endorser,
                           operation=self._op(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)

    def _opForGet(self):
        return {
            TARGET_NYM: self.identity.identifier,
            TXN_TYPE: GET_NYM,
        }

    def getRequest(self, requestAuthor: Identifier):
        if not self.seqNo:
            return Request(identifier=requestAuthor,
                           operation=self._opForGet(),
                           protocolVersion=CURRENT_PROTOCOL_VERSION)
