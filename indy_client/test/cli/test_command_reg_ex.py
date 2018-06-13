import pytest
from plenum.cli.helper import getClientGrams
from plenum.common.constants import NAME, VERSION, TYPE, KEYS
from plenum.test.cli.helper import assertCliTokens
from plenum.test.cli.test_command_reg_ex import getMatchedVariables
from prompt_toolkit.contrib.regular_languages.compiler import compile

from indy_client.cli.helper import getNewClientGrams
from indy_common.constants import REF, CLAIM_DEF_SCHEMA_REF
from indy_common.roles import Roles


@pytest.fixture("module")
def grammar():
    grams = getClientGrams() + getNewClientGrams()
    return compile("".join(grams))


def testSendNymWithRole(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    role = Roles.TRUST_ANCHOR.name
    matchedVars = getMatchedVariables(
        grammar, "send NYM dest={} role={}".format(dest, role))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest, "role": role})


def testSendNymWithoutRole(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    matchedVars = getMatchedVariables(grammar, 'send NYM dest={}'.format(dest))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest})


def testSendNymVerkey(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    role = Roles.TRUST_ANCHOR.name
    verkey = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="

    # Test with verkey
    matchedVars = getMatchedVariables(
        grammar, "send NYM dest={} role={} verkey={}".format(
            dest, role, verkey))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest,
        "role": role, "new_ver_key": verkey
    })

    # Test without verkey
    matchedVars = getMatchedVariables(
        grammar,
        "send NYM dest={} role={}".format(dest, role))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest, "role": role
    })

    # Verkey being empty string is supported
    matchedVars = getMatchedVariables(
        grammar,
        "send NYM dest={} role={} verkey={}".format(dest, role, ''))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest, "role": role, "new_ver_key": ''
    })


def testGetNym(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    matchedVars = getMatchedVariables(
        grammar, "send GET_NYM dest={}".format(dest))
    assertCliTokens(matchedVars, {
        "send_get_nym": "send GET_NYM", "dest_id": dest})


def testSendSchema(grammar):
    name = "Degree"
    version = "1.0"
    keys = "undergrad,last_name,first_name,birth_date,postgrad,expiry_date"
    matchedVars = getMatchedVariables(grammar,
                                      'send SCHEMA name={} version={} keys={}'
                                      .format(name, version, keys))
    assertCliTokens(matchedVars,
                    {"send_schema": "send SCHEMA",
                     NAME: name,
                     VERSION: version,
                     KEYS: keys})


def test_send_get_schema(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    name = "Degree"
    version = "1.0"
    matchedVars = getMatchedVariables(
        grammar, 'send GET_SCHEMA dest={} name={} version={}' .format(
            dest, name, version))
    assertCliTokens(matchedVars, {
        "send_get_schema": "send GET_SCHEMA", NAME: name, VERSION: version})


def testSendAttribRegEx(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    raw = '{"legal org": "BRIGHAM YOUNG UNIVERSITY, PROVO, UT", ' \
          '"email": "mail@byu.edu"}'
    matchedVars = getMatchedVariables(
        grammar, 'send ATTRIB dest={} raw={}'.format(
            dest, raw))
    assertCliTokens(matchedVars, {
        "send_attrib": "send ATTRIB", "dest_id": dest, "raw": raw})


def test_send_get_attrib_regex(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    raw = 'legal'
    matchedVars = getMatchedVariables(
        grammar, 'send GET_ATTR dest={} raw={}'.format(
            dest, raw))
    assertCliTokens(matchedVars, {
        "send_get_attr": "send GET_ATTR", "dest_id": dest, "raw": raw})


def testAddAttrRegEx(grammar):
    getMatchedVariables(
        grammar,
        "add attribute first_name=Tyler,last_name=Ruff,birth_date=12/17/1991,undergrad=True,postgrad=True,expiry_date=12/31/2101 for Tyler")


def testAddAttrProverRegEx(grammar):
    getMatchedVariables(
        grammar,
        "attribute known to BYU first_name=Tyler, last_name=Ruff, birth_date=12/17/1991, undergrad=True, postgrad=True, expiry_date=12/31/2101")


def testSendClaimDefRegEx(grammar):
    matchedVars = getMatchedVariables(
        grammar, "send CLAIM_DEF ref=15 signature_type=CL")
    from indy_common.constants import CLAIM_DEF_SIGNATURE_TYPE
    assertCliTokens(matchedVars, {
        "send_claim_def": "send CLAIM_DEF", CLAIM_DEF_SCHEMA_REF: "15", CLAIM_DEF_SIGNATURE_TYPE: "CL"})


def test_send_get_claim_def_regex(grammar):
    matchedVars = getMatchedVariables(
        grammar, "send GET_CLAIM_DEF ref=15 signature_type=CL")
    from indy_common.constants import CLAIM_DEF_SIGNATURE_TYPE
    assertCliTokens(matchedVars, {
        "send_get_claim_def": "send GET_CLAIM_DEF", CLAIM_DEF_SCHEMA_REF: "15", CLAIM_DEF_SIGNATURE_TYPE: "CL"})


def testShowFileCommandRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "show sample/faber-request.indy")
    assertCliTokens(matchedVars, {
        "show_file": "show", "file_path": "sample/faber-request.indy"})

    matchedVars = getMatchedVariables(grammar,
                                      "show sample/faber-request.indy ")
    assertCliTokens(matchedVars, {
        "show_file": "show", "file_path": "sample/faber-request.indy"})


def testLoadFileCommandRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "load sample/faber-request.indy")
    assertCliTokens(matchedVars, {
        "load_file": "load", "file_path": "sample/faber-request.indy"})

    matchedVars = getMatchedVariables(grammar,
                                      "load sample/faber-request.indy ")
    assertCliTokens(matchedVars, {
        "load_file": "load", "file_path": "sample/faber-request.indy"})


def testShowLinkRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "show connection faber")
    assertCliTokens(matchedVars, {"show_connection": "show connection",
                                  "connection_name": "faber"})

    matchedVars = getMatchedVariables(grammar, "show connection faber college")
    assertCliTokens(matchedVars, {"show_connection": "show connection",
                                  "connection_name": "faber college"})

    matchedVars = getMatchedVariables(
        grammar, "show connection faber college ")
    assertCliTokens(matchedVars, {"show_connection": "show connection",
                                  "connection_name": "faber college "})


def testConnectRegEx(grammar):
    getMatchedVariables(grammar, "connect dummy")
    getMatchedVariables(grammar, "connect test")
    getMatchedVariables(grammar, "connect live")


def testSyncLinkRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "sync faber")
    assertCliTokens(
        matchedVars, {"sync_connection": "sync", "connection_name": "faber"})

    matchedVars = getMatchedVariables(grammar, 'sync "faber"')
    assertCliTokens(
        matchedVars, {"sync_connection": "sync", "connection_name": '"faber"'})

    matchedVars = getMatchedVariables(grammar, 'sync "faber" ')
    assertCliTokens(matchedVars,
                    {"sync_connection": "sync",
                     "connection_name": '"faber" '})


def testPingTargetRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "ping faber")
    assertCliTokens(matchedVars, {"ping": "ping", "target_name": "faber"})


def testAcceptInvitationLinkRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "accept request from faber")
    assertCliTokens(matchedVars,
                    {"accept_connection_request": "accept request from",
                     "connection_name": "faber"})

    matchedVars = getMatchedVariables(grammar, 'accept request from "faber"')
    assertCliTokens(matchedVars,
                    {"accept_connection_request": "accept request from",
                     "connection_name": '"faber"'})

    matchedVars = getMatchedVariables(grammar, 'accept request from "faber" ')
    assertCliTokens(matchedVars,
                    {"accept_connection_request": "accept request from",
                     "connection_name": '"faber" '})


def testShowClaimRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "show claim Transcript")
    assertCliTokens(matchedVars, {"show_claim": "show claim",
                                  "claim_name": "Transcript"})

    matchedVars = getMatchedVariables(grammar, 'show claim "Transcript"')
    assertCliTokens(matchedVars, {"show_claim": "show claim",
                                  "claim_name": '"Transcript"'})


def testRequestClaimRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "request claim Transcript")
    assertCliTokens(matchedVars, {"request_claim": "request claim",
                                  "claim_name": "Transcript"})

    matchedVars = getMatchedVariables(grammar, 'request claim "Transcript"')
    assertCliTokens(matchedVars, {"request_claim": "request claim",
                                  "claim_name": '"Transcript"'})


def testProofReqRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "show proof request Transcript")
    assertCliTokens(matchedVars, {"show_proof_request": "show proof request",
                                  "proof_request_name": "Transcript"})

    matchedVars = getMatchedVariables(grammar,
                                      "show proof request Transcript ")
    assertCliTokens(matchedVars, {"show_proof_request": "show proof request",
                                  "proof_request_name": "Transcript "})


def testSendProofReqRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "send proof-request Over-21 to JaneDoe")
    assertCliTokens(matchedVars, {"send_proof_request": "send proof-request",
                                  "proof_request_name": "Over-21",
                                  "target": " JaneDoe"})


def testSetAttribute(grammar):
    matchedVars = getMatchedVariables(
        grammar, "set first_name to Alice")
    assertCliTokens(matchedVars, {
        "set_attr": "set", "attr_name": "first_name", "attr_value": "Alice"})


def testSendProof(grammar):
    getMatchedVariables(grammar, 'send proof Job-Application to Acme')


def testSendPoolUpgrade(grammar):
    # Testing for start
    getMatchedVariables(
        grammar, "send POOL_UPGRADE name=upgrade-13 "
        "version=0.0.6 sha256=f284bdc3c1c9e24a494e285cb387c69510f28de51c15bb93179d9c7f28705398 action=start "
        "schedule={'AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3': "
        "'2017-01-25T12:49:05.258870+00:00', "
        "'4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2': "
        "'2017-01-25T12:33:53.258870+00:00', "
        "'JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ': "
        "'2017-01-25T12:44:01.258870+00:00', "
        "'DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2': "
        "'2017-01-25T12:38:57.258870+00:00'} "
        "timeout=10 "
        "force=True "
        "reinstall=True")

    # Testing for cancel
    getMatchedVariables(
        grammar, 'send POOL_UPGRADE name=upgrade-13 version=0.0.6 '
        'sha256=aad1242 action=cancel '
        'justification="not gonna give you"')


def testDisconnect(grammar):
    matchedVars = getMatchedVariables(
        grammar, "disconnect")
    assertCliTokens(matchedVars, {"disconn": "disconnect"})


def testNewIdentifier(grammar):
    matchedVars = getMatchedVariables(
        grammar, "new DID")
    assertCliTokens(matchedVars, {"new_id": "new DID",
                                  "id": None,
                                  "seed": None, "alias": None})

    matchedVars = getMatchedVariables(
        grammar, "new DID as myalis")
    assertCliTokens(matchedVars,
                    {"new_id": "new DID", "id": None,
                     "seed": None, "alias": "myalis"})

    matchedVars = getMatchedVariables(
        grammar, "new DID 4QxzWk3ajdnEA37NdNU5Kt")
    assertCliTokens(matchedVars, {"new_id": "new DID",
                                  "id": "4QxzWk3ajdnEA37NdNU5Kt",
                                  "seed": None, "alias": None})

    matchedVars = getMatchedVariables(
        grammar, "new DID 4QxzWk3ajdnEA37NdNU5Kt "
                 "with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assertCliTokens(matchedVars, {"new_id": "new DID",
                                  "id": "4QxzWk3ajdnEA37NdNU5Kt",
                                  "seed": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                  "alias": None})


def testAddGenTxnRegEx(grammar):
    matchedVars = getMatchedVariables(
        grammar,
        "add genesis transaction NYM dest=2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML")
    assertCliTokens(matchedVars,
                    {"add_genesis": "add genesis transaction NYM",
                     "dest": "dest=",
                     "dest_id": "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML",
                     "role": None,
                     "ver_key": None})

    matchedVars = getMatchedVariables(
        grammar,
        "add genesis transaction NYM dest=2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML role={role}".format(
            role=Roles.STEWARD.name))
    assertCliTokens(matchedVars,
                    {"add_genesis": "add genesis transaction NYM",
                     "dest": "dest=",
                     "dest_id": "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML",
                     "role": Roles.STEWARD.name,
                     "ver_key": None})

    matchedVars = getMatchedVariables(
        grammar, 'add genesis transaction NODE for 2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML '
        'by FvDi9xQZd1CZitbK15BNKFbA7izCdXZjvxf91u3rQVzW with data '
        '{"node_ip": "localhost", "node_port": "9701", "client_ip": "localhost", "client_port": "9702", "alias": "AliceNode"}')
    assertCliTokens(
        matchedVars,
        {
            "add_gen_txn": "add genesis transaction",
            "type": "NODE",
            "dest": "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML",
            "identifier": "FvDi9xQZd1CZitbK15BNKFbA7izCdXZjvxf91u3rQVzW",
            "role": None,
            "data": '{"node_ip": "localhost", "node_port": "9701", "client_ip": "localhost", "client_port": "9702", "alias": "AliceNode"}'})


def testReqAvailClaims(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "request available claims from Faber")

    assertCliTokens(matchedVars, {
        "request_avail_claims": "request available claims from",
        "connection_name": "Faber"
    })
