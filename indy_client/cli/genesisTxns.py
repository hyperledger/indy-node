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

from plenum.common.constants import STEWARD, TXN_ID
from plenum.common.types import f

from indy_common.constants import TXN_TYPE, TARGET_NYM, ROLE, NYM, TRUST_ANCHOR

STEWARD_SEED = b'steward seed used for signer....'
TRUST_ANCHOR_SEED = b'sponsors are people too.........'

GENESIS_TRANSACTIONS = [
    {
        TXN_TYPE: NYM,
        TARGET_NYM: 'bx3ePPiBdRywm16OOmZdtlzF5FGmX06Fj2sAYbMdF18=',
        TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
        ROLE: STEWARD
    },
    {
        TXN_TYPE: NYM,
        f.IDENTIFIER.nm: 'bx3ePPiBdRywm16OOmZdtlzF5FGmX06Fj2sAYbMdF18=',
        TARGET_NYM: 'MnT3cFlVvVu7QO+QzPp5seU14pkOT7go1PsqDWZSrbo=',
        ROLE: TRUST_ANCHOR,
        TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4c'
    },
    # {
    #     TXN_TYPE: NYM,
    #     f.IDENTIFIER.nm: 'OP2h59vBVQerRi6FjoOoMhSTv4CAemeEg4LPtDHaEWw=',
    #     TARGET_NYM: 'ARyM91PzDKveCuqkV9B6TJ5f9YxI8Aw/cz5eDAduNUs=',
    #     ROLE: TRUST_ANCHOR,
    #     TXN_ID: '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4d'
    # }
]
