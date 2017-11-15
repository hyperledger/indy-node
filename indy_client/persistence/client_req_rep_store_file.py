#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import json
import os

from plenum.common.util import updateFieldsWithSeqNo
from plenum.persistence.client_req_rep_store_file import ClientReqRepStoreFile \
    as PClientReqRepStoreFile

from indy_common.txn_util import getTxnOrderedFields


class ClientReqRepStoreFile(PClientReqRepStoreFile):
    def __init__(self, name, baseDir):
        super().__init__(name, baseDir)
        self.lastTxnsFileName = "last_txn_for_id"

    @property
    def txnFieldOrdering(self):
        fields = getTxnOrderedFields()
        return updateFieldsWithSeqNo(fields)

    def setLastTxnForIdentifier(self, identifier, value: str):
        filePath = os.path.join(self.dataLocation, self.lastTxnsFileName)
        if not os.path.exists(filePath):
            open(filePath, 'w').close()
        with open(filePath, "r+") as f:
            data = f.read().strip()
            data = json.loads(data) if data else {}
            data[identifier] = value
            f.seek(0)
            f.write(json.dumps(data))

    def getLastTxnForIdentifier(self, identifier):
        try:
            data = {}
            with open(os.path.join(self.dataLocation, self.lastTxnsFileName),
                      "r") as f:
                data = f.read().strip()
                data = json.loads(data) if data else {}
            return data.get(identifier)
        except FileNotFoundError:
            return None
