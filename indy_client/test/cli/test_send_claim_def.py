from indy_client.test.cli.constants import SCHEMA_ADDED, CLAIM_DEF_ADDED
from indy_client.test.cli.helper import getSeqNoFromCliOutput


def test_send_claim_def_succeeds(
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


def test_send_claim_def_fails_if_ref_is_seqno_of_non_schema_txn(
        be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.1'
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


def test_send_claim_def_fails_if_ref_is_not_existing_seqno(
        be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.2'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED, within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect='Schema with seqNo {ref} not found',
       mapper={'ref': schemaTxnSeqNo + 1},
       within=5)


def test_can_not_send_claim_def_for_same_schema_and_signature_type(
        be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.3'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect='can have one and only one CLAIM_DEF',
       mapper={'ref': schemaTxnSeqNo},
       within=5)

def test_can_send_same_claim_def_by_different_issuers(
        be, do, poolNodesStarted, trusteeCli, newStewardCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.4'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)

    be(newStewardCli)
    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)