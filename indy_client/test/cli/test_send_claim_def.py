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

from indy_client.test.cli.constants import SCHEMA_ADDED, CLAIM_DEF_ADDED
from indy_client.test.cli.helper import getSeqNoFromCliOutput


def testSendClaimDefSucceedsIfRefIsSeqNoOfSchemaTxn(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.0'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)


def testSendClaimDefFailsIfRefIsSeqNoOfNonSchemaTxn(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.0'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)

    firstClaimDefSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect='Schema with seqNo {ref} not found',
       mapper={'ref': firstClaimDefSeqNo},
       within=5)


def testSendClaimDefFailsIfRefIsNotExistingSeqNo(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.0'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED, within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect='Schema with seqNo {ref} not found',
       mapper={'ref': schemaTxnSeqNo + 1},
       within=5)
