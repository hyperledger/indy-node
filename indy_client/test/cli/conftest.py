import json
import os
import re
import tempfile
from typing import List

import pytest
from plenum.common.signer_did import DidSigner
from indy_client.test.agent.acme import ACME_ID, ACME_SEED
from indy_client.test.agent.acme import ACME_VERKEY
from indy_client.test.agent.faber import FABER_ID, FABER_VERKEY, FABER_SEED
from indy_client.test.agent.thrift import THRIFT_ID, THRIFT_VERKEY, THRIFT_SEED
from indy_common.config_helper import NodeConfigHelper
from ledger.genesis_txn.genesis_txn_file_util import create_genesis_txn_init_ledger

from stp_core.crypto.util import randomSeed
from stp_core.network.port_dispenser import genHa

import plenum
from plenum.common import util
from plenum.common.constants import ALIAS, NODE_IP, NODE_PORT, CLIENT_IP, \
    CLIENT_PORT, SERVICES, VALIDATOR, BLS_KEY, TXN_TYPE, NODE, NYM
from plenum.common.constants import CLIENT_STACK_SUFFIX
from plenum.common.exceptions import BlowUp
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import randomString
from plenum.test import waits
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone

from plenum.test.conftest import txnPoolNodeSet, patchPluginManager, tdirWithNodeKeepInited
from stp_core.loop.eventually import eventually
from stp_core.common.log import getlogger
from plenum.test.conftest import tdirWithPoolTxns, tdirWithDomainTxns
from indy_client.cli.helper import USAGE_TEXT, NEXT_COMMANDS_TO_TRY_TEXT
from indy_client.test.helper import createNym, buildStewardClient
from indy_common.constants import ENDPOINT, TRUST_ANCHOR
from indy_common.roles import Roles
from indy_common.test.conftest import poolTxnTrusteeNames
from indy_common.test.conftest import domainTxnOrderedFields
from indy_node.test.helper import TestNode
from plenum.common.keygen_utils import initNodeKeysForBothStacks

# plenum.common.util.loggingConfigured = False

from stp_core.loop.looper import Looper
from plenum.test.cli.helper import newKeyPair, doByCtx

from indy_client.test.cli.helper import ensureNodesCreated, get_connection_request, \
    getPoolTxnData, newCLI, getCliBuilder, P, prompt_is, addAgent, doSendNodeCmd, addNym
from indy_client.test.agent.conftest import faberIsRunning as runningFaber, \
    acmeIsRunning as runningAcme, thriftIsRunning as runningThrift, emptyLooper,\
    faberWallet, acmeWallet, thriftWallet, agentIpAddress, \
    faberAgentPort, acmeAgentPort, thriftAgentPort, faberAgent, acmeAgent, \
    thriftAgent, faberBootstrap, acmeBootstrap
from indy_client.test.cli.helper import connect_and_check_output
from indy_common.config_helper import ConfigHelper
from stp_core.crypto.util import randomSeed


@pytest.fixture("module")
def ledger_base_dir(tconf):
    return tconf.CLI_NETWORK_DIR


@pytest.yield_fixture(scope="session")
def cliTempLogger():
    file_name = "indy_cli_test.log"
    file_path = os.path.join(tempfile.tempdir, file_name)
    with open(file_path, 'w'):
        pass
    return file_path


@pytest.yield_fixture(scope="module")
def looper():
    with Looper(debug=False) as l:
        yield l


@pytest.fixture("module")
def cli(looper, client_tdir):
    return newCLI(looper, client_tdir)


@pytest.fixture(scope="module")
def newKeyPairCreated(cli):
    return newKeyPair(cli)


@pytest.fixture(scope="module")
def CliBuilder(tdir, tdirWithPoolTxns, tdirWithDomainTxnsUpdated,
               txnPoolNodesLooper, tconf, cliTempLogger):
    return getCliBuilder(
        tdir,
        tconf,
        tdirWithPoolTxns,
        tdirWithDomainTxnsUpdated,
        logFileName=cliTempLogger,
        def_looper=txnPoolNodesLooper)


def getDefaultUserMap(name):
    return {
        'wallet-name': name,
    }


@pytest.fixture(scope="module")
def aliceMap():
    return getDefaultUserMap("Alice")


@pytest.fixture(scope="module")
def earlMap():
    return getDefaultUserMap("Earl")


@pytest.fixture(scope="module")
def bobMap():
    return getDefaultUserMap("Bob")


@pytest.fixture(scope="module")
def susanMap():
    return getDefaultUserMap("Susan")


@pytest.fixture(scope="module") # noqa
def faberMap(agentIpAddress, faberAgentPort):
    ha = "{}:{}".format(agentIpAddress, faberAgentPort)
    return {'inviter': 'Faber College',
            'invite': "sample/faber-request.indy",
            'invite-not-exists': "sample/faber-request.indy.not.exists",
            'inviter-not-exists': "non-existing-inviter",
            'seed': FABER_SEED.decode(),
            "remote": FABER_ID,
            "remote-verkey": FABER_VERKEY,
            "nonce": "b1134a647eb818069c089e7694f63e6d",
            ENDPOINT: ha,
            "invalidEndpointAttr": json.dumps({ENDPOINT: {'ha': ' 127.0.0.1:11'}}),
            "endpointAttr": json.dumps({ENDPOINT: {'ha': ha}}),
            "claims": "Transcript",
            "claim-to-show": "Transcript",
            "proof-req-to-match": "Transcript",
            'wallet-name': 'Faber'}


@pytest.fixture(scope="module") # noqa
def acmeMap(agentIpAddress, acmeAgentPort):
    ha = "{}:{}".format(agentIpAddress, acmeAgentPort)
    return {'inviter': 'Acme Corp',
            ENDPOINT: ha,
            "endpointAttr": json.dumps({ENDPOINT: {'ha': ha}}),
            "invalidEndpointAttr": json.dumps({ENDPOINT: {'ha': '127.0.0.1: 11'}}),
            'invite': 'sample/acme-job-application.indy',
            'invite-no-pr': 'sample/acme-job-application-no-pr.indy',
            'invite-not-exists': 'sample/acme-job-application.indy.not.exists',
            'inviter-not-exists': 'non-existing-inviter',
            'seed': ACME_SEED.decode(),
            "remote": ACME_ID,
            "remote-verkey": ACME_VERKEY,
            'nonce': '57fbf9dc8c8e6acde33de98c6d747b28c',
            'proof-requests': 'Job-Application',
            'proof-request-to-show': 'Job-Application',
            'claim-ver-req-to-show': '0.2',
            'proof-req-to-match': 'Job-Application',
            'claims': '<claim-name>',
            'rcvd-claim-transcript-provider': 'Faber College',
            'rcvd-claim-transcript-name': 'Transcript',
            'rcvd-claim-transcript-version': '1.2',
            'send-proof-target': 'Alice',
            'pr-name': 'Job-Application',
            'pr-schema-version': '0.2',
            'wallet-name': 'Acme'}


@pytest.fixture(scope="module") # noqa
def thriftMap(agentIpAddress, thriftAgentPort):
    ha = "{}:{}".format(agentIpAddress, thriftAgentPort)
    return {'inviter': 'Thrift Bank',
            'invite': "sample/thrift-loan-application.indy",
            'invite-not-exists': "sample/thrift-loan-application.indy.not.exists",
            'inviter-not-exists': "non-existing-inviter",
            'seed': THRIFT_SEED.decode(),
            "remote": THRIFT_ID,
            "remote-verkey": THRIFT_VERKEY,
            "nonce": "77fbf9dc8c8e6acde33de98c6d747b28c",
            ENDPOINT: ha,
            "endpointAttr": json.dumps({ENDPOINT: {'ha': ha}}),
            "invalidEndpointAttr": json.dumps({ENDPOINT: {'ha': '127.0.0.1:4A78'}}),
            "proof-requests": "Loan-Application-Basic, Loan-Application-KYC",
            "rcvd-claim-job-certificate-name": "Job-Certificate",
            "rcvd-claim-job-certificate-version": "0.2",
            "rcvd-claim-job-certificate-provider": "Acme Corp",
            "claim-ver-req-to-show": "0.1",
            'wallet-name': 'Thrift'}


@pytest.fixture(scope="module")
def loadInviteOut(nextCommandsToTryUsageLine):
    return ["1 connection request found for {inviter}.",
            "Creating connection for {inviter}.",
            ''] + \
        nextCommandsToTryUsageLine + \
        ['    show connection "{inviter}"',
            '    accept request from "{inviter}"',
            '',
            '']


@pytest.fixture(scope="module")
def fileNotExists():
    return ["Given file does not exist"]


@pytest.fixture(scope="module")
def canNotSyncMsg():
    return ["Cannot sync because not connected"]


@pytest.fixture(scope="module")
def syncWhenNotConnected(canNotSyncMsg, connectUsage):
    return canNotSyncMsg + connectUsage


@pytest.fixture(scope="module")
def canNotAcceptMsg():
    return ["Cannot accept because not connected"]


@pytest.fixture(scope="module")
def acceptWhenNotConnected(canNotAcceptMsg, connectUsage):
    return canNotAcceptMsg + connectUsage


@pytest.fixture(scope="module")
def acceptUnSyncedWithoutEndpointWhenConnected(
        common_accept_request_msgs, syncedInviteAcceptedOutWithoutClaims):
    return common_accept_request_msgs + \
        syncedInviteAcceptedOutWithoutClaims


@pytest.fixture(scope="module")
def common_accept_requests_msgs():
    return ["Request not yet verified",
            "Connection not yet synchronized.",
            ]


@pytest.fixture(scope="module")
def acceptUnSyncedWhenNotConnected(common_accept_requests_msgs,
                                   canNotSyncMsg, connectUsage):
    return common_accept_requests_msgs + \
        ["Request acceptance aborted."] + \
        canNotSyncMsg + connectUsage


@pytest.fixture(scope="module")
def usageLine():
    return [USAGE_TEXT]


@pytest.fixture(scope="module")
def nextCommandsToTryUsageLine():
    return [NEXT_COMMANDS_TO_TRY_TEXT]


@pytest.fixture(scope="module")
def connectUsage(usageLine):
    return usageLine + ["    connect"]


@pytest.fixture(scope="module")
def notConnectedStatus(connectUsage):
    return ['Not connected to Indy network. Please connect first.', ''] +\
        connectUsage +\
        ['', '']


@pytest.fixture(scope="module")
def newKeyringOut():
    return ["New wallet {wallet-name} created",
            'Active wallet set to "{wallet-name}"'
            ]


@pytest.fixture(scope="module")
def connectionAlreadyExists():
    return ["Connection already exists"]


@pytest.fixture(scope="module")
def jobApplicationProofRequestMap():
    return {
        'proof-request-version': '0.2',
        'proof-request-attr-first_name': 'first_name',
        'proof-request-attr-last_name': 'last_name',
        'proof-request-attr-phone_number': 'phone_number',
        'proof-request-attr-degree': 'degree',
        'proof-request-attr-status': 'status',
        'proof-request-attr-ssn': 'ssn'
    }


@pytest.fixture(scope="module")
def unsyncedInviteAcceptedWhenNotConnected(availableClaims):
    return [
        "Response from {inviter}",
        "Trust established.",
        "DID created in Indy."
    ] + availableClaims + [
        "Cannot check if DID is written to Indy."
    ]


@pytest.fixture(scope="module")
def syncedInviteAcceptedOutWithoutClaims():
    return [
        "Signature accepted.",
        "Trust established.",
        "DID created in Indy.",
        "Synchronizing...",
        "Confirmed DID written to Indy."
    ]


@pytest.fixture(scope="module")
def availableClaims():
    return ["Available Claim(s): {claims}"]


@pytest.fixture(scope="module")
def syncedInviteAcceptedWithClaimsOut(
        syncedInviteAcceptedOutWithoutClaims, availableClaims):
    return syncedInviteAcceptedOutWithoutClaims + availableClaims


@pytest.fixture(scope="module")
def unsycedAcceptedInviteWithoutClaimOut(syncedInviteAcceptedOutWithoutClaims):
    return [
        "Request not yet verified",
        "Attempting to sync...",
        "Synchronizing...",
    ] + syncedInviteAcceptedOutWithoutClaims + \
        ["Confirmed DID written to Indy."]


@pytest.fixture(scope="module")
def unsyced_already_accepted_request_accepted_out():
    return [
        "Request not yet verified",
        "Attempting to sync...",
        "Synchronizing..."
    ]


@pytest.fixture(scope="module")
def showTranscriptProofOut():
    return [
        "Claim ({rcvd-claim-transcript-name} "
        "v{rcvd-claim-transcript-version} "
        "from {rcvd-claim-transcript-provider})",
        "  student_name: {attr-student_name}",
        "* ssn: {attr-ssn}",
        "* degree: {attr-degree}",
        "  year: {attr-year}",
        "* status: {attr-status}",
    ]


@pytest.fixture(scope="module")
def showJobCertificateClaimInProofOut():
    return [
        "The Proof is constructed from the following claims:",
        "Claim ({rcvd-claim-job-certificate-name} "
        "v{rcvd-claim-job-certificate-version} "
        "from {rcvd-claim-job-certificate-provider})",
        "* first_name: {attr-first_name}",
        "* last_name: {attr-last_name}",
        "  employee_status: {attr-employee_status}",
        "  experience: {attr-experience}",
        "  salary_bracket: {attr-salary_bracket}"
    ]


@pytest.fixture(scope="module")
def proofConstructedMsg():
    return ["The Proof is constructed from the following claims:"]


@pytest.fixture(scope="module")
def showJobAppProofRequestOut(proofConstructedMsg, showTranscriptProofOut):
    return [
        'Found proof request "{proof-req-to-match}" in connection "{inviter}"',
        "Status: Requested",
        "Name: {proof-request-to-show}",
        "Version: {proof-request-version}",
        "Attributes:",
        "{proof-request-attr-first_name}: {set-attr-first_name}",
        "{proof-request-attr-last_name}: {set-attr-last_name}",
        "{proof-request-attr-phone_number}: {set-attr-phone_number}",
        "{proof-request-attr-degree} (V): {attr-degree}",
        "{proof-request-attr-status} (V): {attr-status}",
        "{proof-request-attr-ssn} (V): {attr-ssn}"
    ] + proofConstructedMsg + showTranscriptProofOut


@pytest.fixture(scope="module")
def showNameProofRequestOut(showJobCertificateClaimInProofOut):
    return [
        'Found proof request "{proof-req-to-match}" in connection "{inviter}"',
        "Name: {proof-req-to-match}",
        "Version: {proof-request-version}",
        "Status: Requested",
        "Attributes:",
        "{proof-request-attr-first_name} (V): {set-attr-first_name}",
        "{proof-request-attr-last_name} (V): {set-attr-last_name}",
    ] + showJobCertificateClaimInProofOut + [
        "Try Next:",
        "set <attr-name> to <attr-value>",
        'send proof "{proof-req-to-match}" to "{inviter}"'
    ]


@pytest.fixture(scope="module")
def showBankingProofOut():
    return [
        "Claim ({rcvd-claim-banking-name} "
        "v{rcvd-claim-banking-version} "
        "from {rcvd-claim-banking-provider})",
        "title: {attr-title}",
        "first_name: {attr-first_name}",
        "last_name: {attr-last_name}",
        "address_1: {attr-address_1}",
        "address_2: {attr-address_2}",
        "address_3: {attr-address_3}",
        "postcode_zip: {attr-postcode_zip}",
        "date_of_birth: {attr-date_of_birth}",
        "account_type: {attr-account_type}",
        "year_opened: {attr-year_opened}",
        "account_status: {attr-account_status}"
    ]


@pytest.fixture(scope="module")
def proofRequestNotExists():
    return ["No matching Proof Requests found in current wallet"]


@pytest.fixture(scope="module")
def connectionNotExists():
    return ["No matching connection requests found in current wallet"]


@pytest.fixture(scope="module")
def faberInviteLoaded(aliceCLI, be, do, faberMap, loadInviteOut):
    be(aliceCLI)
    do("load {invite}", expect=loadInviteOut, mapper=faberMap)


@pytest.fixture(scope="module")
def acmeInviteLoaded(aliceCLI, be, do, acmeMap, loadInviteOut):
    be(aliceCLI)
    do("load {invite}", expect=loadInviteOut, mapper=acmeMap)


@pytest.fixture(scope="module")
def attrAddedOut():
    return ["Attribute added for nym {remote}"]


@pytest.fixture(scope="module")
def nymAddedOut():
    return ["Nym {remote} added"]


@pytest.fixture(scope="module")
def unSyncedEndpointOut():
    return ["Remote endpoint: <unknown, waiting for sync>"]


@pytest.fixture(scope="module")
def showConnectionOutWithoutEndpoint(showConnectionOut, unSyncedEndpointOut):
    return showConnectionOut + unSyncedEndpointOut


@pytest.fixture(scope="module")
def endpointReceived():
    return ["Endpoint received:"]


@pytest.fixture(scope="module")
def endpointNotAvailable():
    return ["Endpoint not available"]


@pytest.fixture(scope="module")
def syncConnectionOutEndsWith():
    return ["Connection {inviter} synced"]


@pytest.fixture(scope="module")
def syncConnectionOutStartsWith():
    return ["Synchronizing..."]


@pytest.fixture(scope="module")
def syncConnectionOutWithEndpoint(syncConnectionOutStartsWith,
                                  syncConnectionOutEndsWith):
    return syncConnectionOutStartsWith + syncConnectionOutEndsWith


@pytest.fixture(scope="module")
def syncConnectionOutWithoutEndpoint(syncConnectionOutStartsWith):
    return syncConnectionOutStartsWith


@pytest.fixture(scope="module")
def showSyncedConnectionWithEndpointOut(
        acceptedConnectionHeading, showConnectionOut):
    return acceptedConnectionHeading + showConnectionOut + \
        ["Last synced: "]


@pytest.fixture(scope="module")
def showSyncedConnectionWithoutEndpointOut(showConnectionOut):
    return showConnectionOut


@pytest.fixture(scope="module")
def connectionNotYetSynced():
    return ["    Last synced: <this connection has not yet been synchronized>"]


@pytest.fixture(scope="module")
def acceptedConnectionHeading():
    return ["Connection"]


@pytest.fixture(scope="module")
def unAcceptedConnectionHeading():
    return ["Connection (not yet accepted)"]


@pytest.fixture(scope="module")
def showUnSyncedConnectionOut(unAcceptedConnectionHeading, showConnectionOut):
    return unAcceptedConnectionHeading + showConnectionOut


@pytest.fixture(scope="module")
def showClaimNotFoundOut():
    return ["No matching Claims found in any connections in current wallet"]


@pytest.fixture(scope="module")
def transcriptClaimAttrValueMap():
    return {
        "attr-student_name": "Alice Garcia",
        "attr-ssn": "123-45-6789",
        "attr-degree": "Bachelor of Science, Marketing",
        "attr-year": "2015",
        "attr-status": "graduated"
    }


@pytest.fixture(scope="module")
def transcriptClaimValueMap(transcriptClaimAttrValueMap):
    basic = {
        'inviter': 'Faber College',
        'name': 'Transcript',
        "version": "1.2",
        'status': "available (not yet issued)"
    }
    basic.update(transcriptClaimAttrValueMap)
    return basic


@pytest.fixture(scope="module")
def bankingRelationshipClaimAttrValueMap():
    return {
        "attr-title": "Mrs.",
        "attr-first_name": "Alicia",
        "attr-last_name": "Garcia",
        "attr-address_1": "H-301",
        "attr-address_2": "Street 1",
        "attr-address_3": "UK",
        "attr-postcode_zip": "G61 3NR",
        "attr-date_of_birth": "December 28, 1990",
        "attr-account_type": "savings",
        "attr-year_opened": "2000",
        "attr-account_status": "active"
    }


@pytest.fixture(scope="module")
def transcriptClaimMap():
    return {
        'inviter': 'Faber College',
        'name': 'Transcript',
        'status': "available (not yet issued)",
        "version": "1.2",
        "attr-student_name": "string",
        "attr-ssn": "string",
        "attr-degree": "string",
        "attr-year": "string",
        "attr-status": "string"
    }


@pytest.fixture(scope="module")
def jobCertClaimAttrValueMap():
    return {
        "attr-first_name": "Alice",
        "attr-last_name": "Garcia",
        "attr-employee_status": "Permanent",
        "attr-experience": "3 years",
        "attr-salary_bracket": "between $50,000 to $100,000"
    }


@pytest.fixture(scope="module")
def jobCertificateClaimValueMap(jobCertClaimAttrValueMap):
    basic = {
        'inviter': 'Acme Corp',
        'name': 'Job-Certificate',
        'status': "available (not yet issued)",
        "version": "0.2"
    }
    basic.update(jobCertClaimAttrValueMap)
    return basic


@pytest.fixture(scope="module")
def jobCertificateClaimMap():
    return {
        'inviter': 'Acme Corp',
        'name': 'Job-Certificate',
        'status': "available (not yet issued)",
        "version": "0.2",
        "attr-first_name": "string",
        "attr-last_name": "string",
        "attr-employee_status": "string",
        "attr-experience": "string",
        "attr-salary_bracket": "string"
    }


@pytest.fixture(scope="module")
def reqClaimOut():
    return ["Found claim {name} in connection {inviter}",
            "Requesting claim {name} from {inviter}..."]


# TODO Change name
@pytest.fixture(scope="module")
def reqClaimOut1():
    return ["Found claim {name} in connection {inviter}",
            "Requesting claim {name} from {inviter}...",
            "Signature accepted.",
            'Received claim "{name}".']


@pytest.fixture(scope="module")
def rcvdTranscriptClaimOut():
    return ["Found claim {name} in connection {inviter}",
            "Name: {name}",
            "Status: ",
            "Version: {version}",
            "Attributes:",
            "student_name: {attr-student_name}",
            "ssn: {attr-ssn}",
            "degree: {attr-degree}",
            "year: {attr-year}",
            "status: {attr-status}"
            ]


@pytest.fixture(scope="module")
def rcvdBankingRelationshipClaimOut():
    return ["Found claim {name} in connection {inviter}",
            "Name: {name}",
            "Status: ",
            "Version: {version}",
            "Attributes:",
            "title: {attr-title}",
            "first_name: {attr-first_name}",
            "last_name: {attr-last_name}",
            "address_1: {attr-address_1}",
            "address_2: {attr-address_2}",
            "address_3: {attr-address_3}",
            "postcode_zip: {attr-postcode_zip}",
            "date_of_birth: {attr-date_of_birth}",
            "year_opened: {attr-year_opened}",
            "account_status: {attr-account_status}"
            ]


@pytest.fixture(scope="module")
def rcvdJobCertClaimOut():
    return ["Found claim {name} in connection {inviter}",
            "Name: {name}",
            "Status: ",
            "Version: {version}",
            "Attributes:",
            "first_name: {attr-first_name}",
            "last_name: {attr-last_name}",
            "employee_status: {attr-employee_status}",
            "experience: {attr-experience}",
            "salary_bracket: {attr-salary_bracket}"
            ]


@pytest.fixture(scope="module")
def showTranscriptClaimOut(nextCommandsToTryUsageLine):
    return ["Found claim {name} in connection {inviter}",
            "Name: {name}",
            "Status: {status}",
            "Version: {version}",
            "Attributes:",
            "student_name",
            "ssn",
            "degree",
            "year",
            "status"
            ] + nextCommandsToTryUsageLine + \
        ['request claim "{name}"']


@pytest.fixture(scope="module")
def showJobCertClaimOut(nextCommandsToTryUsageLine):
    return ["Found claim {name} in connection {inviter}",
            "Name: {name}",
            "Status: {status}",
            "Version: {version}",
            "Attributes:",
            "first_name",
            "last_name",
            "employee_status",
            "experience",
            "salary_bracket"
            ] + nextCommandsToTryUsageLine + \
        ['request claim "{name}"']


@pytest.fixture(scope="module")
def showBankingRelationshipClaimOut(nextCommandsToTryUsageLine):
    return ["Found claim {name} in connection {inviter}",
            "Name: {name}",
            "Status: {status}",
            "Version: {version}",
            "Attributes:",
            "title",
            "first_name",
            "last_name",
            "address_1",
            "address_2",
            "address_3",
            "postcode_zip",
            "date_of_birth",
            "account_type",
            "year_opened",
            "account_status"
            ] + nextCommandsToTryUsageLine + \
        ['request claim "{name}"']


@pytest.fixture(scope="module")
def showConnectionWithProofRequestsOut():
    return ["Proof Request(s): {proof-requests}"]


@pytest.fixture(scope="module")
def showConnectionWithAvailableClaimsOut():
    return ["Available Claim(s): {claims}"]


@pytest.fixture(scope="module")
def showAcceptedConnectionWithClaimReqsOut(
        showAcceptedConnectionOut,
        showConnectionWithProofRequestsOut,
        showConnectionWithAvailableClaimsOut,
        showConnectionSuggestion):
    return showAcceptedConnectionOut + showConnectionWithProofRequestsOut + \
        showConnectionWithAvailableClaimsOut + \
        showConnectionSuggestion


@pytest.fixture(scope="module")
def showAcceptedConnectionWithoutAvailableClaimsOut(
        showAcceptedConnectionOut,
        showConnectionWithProofRequestsOut):
    return showAcceptedConnectionOut + showConnectionWithProofRequestsOut


@pytest.fixture(scope="module")
def showAcceptedConnectionWithAvailableClaimsOut(
        showAcceptedConnectionOut,
        showConnectionWithProofRequestsOut,
        showConnectionWithAvailableClaimsOut):
    return showAcceptedConnectionOut + showConnectionWithProofRequestsOut + \
        showConnectionWithAvailableClaimsOut


@pytest.fixture(scope="module")
def showConnectionSuggestion(nextCommandsToTryUsageLine):
    return nextCommandsToTryUsageLine + \
        ['show claim "{claims}"',
         'request claim "{claims}"']


@pytest.fixture(scope="module")
def showAcceptedConnectionOut():
    return [
        "Connection",
        "Name: {inviter}",
        "DID: {DID}",
        "Verification key: {verkey}",
        "Remote: {remote}",
        "Remote Verification key: {remote-verkey}",
        "Trust anchor: {inviter} (confirmed)",
        "Request nonce: {nonce}",
        "Request status: Accepted"]


@pytest.fixture(scope="module")
def showConnectionOut(nextCommandsToTryUsageLine, connectionNotYetSynced):
    return [
        "    Name: {inviter}",
        "    DID: not yet assigned",
        "    Trust anchor: {inviter} (not yet written to Indy)",
        "    Verification key: <empty>",
        "    Signing key: <hidden>",
        "    Remote: {remote}",
        "    Remote endpoint: {endpoint}",
        "    Request nonce: {nonce}",
        "    Request status: not verified, remote verkey unknown",
        "    Last synced: {last_synced}"] + \
        [""] + \
        nextCommandsToTryUsageLine + \
        ['    sync "{inviter}"',
            '    accept request from "{inviter}"',
            '',
            '']


@pytest.fixture(scope="module")
def showAcceptedSyncedConnectionOut(nextCommandsToTryUsageLine):
    return [
        "Connection",
        "Name: {inviter}",
        "Trust anchor: {inviter} (confirmed)",
        "Verification key: ~",
        "Signing key: <hidden>",
        "Remote: {remote}",
        "Remote Verification key: <same as Remote>",
        "Request nonce: {nonce}",
        "Request status: Accepted",
        "Proof Request(s): {proof-requests}",
        "Available Claim(s): {claims}"] + \
        nextCommandsToTryUsageLine + \
        ['show claim "{claim-to-show}"',
            'send proof "{proof-requests}"']


@pytest.yield_fixture(scope="module")
def poolCLI_baby(CliBuilder):
    yield from CliBuilder("pool")


@pytest.yield_fixture(scope="module")
def aliceCLI(CliBuilder):
    yield from CliBuilder("alice")


@pytest.yield_fixture(scope="module")
def devinCLI(CliBuilder):
    yield from CliBuilder("devin")


@pytest.yield_fixture(scope="module")
def bobCLI(CliBuilder):
    yield from CliBuilder("bob")


@pytest.yield_fixture(scope="module")
def earlCLI(CliBuilder):
    yield from CliBuilder("earl")


@pytest.yield_fixture(scope="module")
def susanCLI(CliBuilder):
    yield from CliBuilder("susan")


@pytest.yield_fixture(scope="module")
def philCLI(CliBuilder):
    yield from CliBuilder("phil")


@pytest.yield_fixture(scope="module")
def faberCLI(CliBuilder):
    yield from CliBuilder("faber")


@pytest.yield_fixture(scope="module")
def acmeCLI(CliBuilder):
    yield from CliBuilder("acme")


@pytest.yield_fixture(scope="module")
def thriftCLI(CliBuilder):
    yield from CliBuilder("thrift")


@pytest.fixture(scope="module")
def poolCLI(tdir, tconf, poolCLI_baby, poolTxnData, poolTxnNodeNames, txnPoolNodeSet):
    seeds = poolTxnData["seeds"]
    for nName in poolTxnNodeNames:
        seed = seeds[nName]
        use_bls = nName in poolTxnData['nodesWithBls']
        config_helper = NodeConfigHelper(nName, tconf, chroot=tdir)
        initNodeKeysForBothStacks(nName, config_helper.keys_dir,
                                  seed, override=True, use_bls=use_bls)
    for node in txnPoolNodeSet:
        poolCLI_baby.nodes[node.name] = node
    return poolCLI_baby


@pytest.fixture(scope="module")
def poolNodesCreated(poolCLI, poolTxnNodeNames):
    #ensureNodesCreated(poolCLI, poolTxnNodeNames)
    return poolCLI


class TestMultiNode:
    def __init__(self, name, poolTxnNodeNames, tdir, tconf,
                 poolTxnData, tdirWithPoolTxns, tdirWithDomainTxns, poolCli):
        self.name = name
        self.poolTxnNodeNames = poolTxnNodeNames
        self.tdir = tdir
        self.tconf = tconf
        self.poolTxnData = poolTxnData
        self.tdirWithPoolTxns = tdirWithPoolTxns
        self.tdirWithDomainTxns = tdirWithDomainTxns
        self.poolCli = poolCli


def custom_tdir_with_pool_txns(pool_txn_data, tdir_for_pool_txns, pool_transactions_file_name):
    ledger = create_genesis_txn_init_ledger(tdir_for_pool_txns, pool_transactions_file_name)

    for item in pool_txn_data["txns"]:
        if item.get(TXN_TYPE) == NODE:
            ledger.add(item)
    ledger.stop()
    return tdir_for_pool_txns


def custom_tdir_with_domain_txns(pool_txn_data, tdir_for_domain_txns,
                                 domain_txn_ordered_fields, domain_transactions_file_name):
    ledger = create_genesis_txn_init_ledger(tdir_for_domain_txns, domain_transactions_file_name)

    for item in pool_txn_data["txns"]:
        if item.get(TXN_TYPE) == NYM:
            ledger.add(item)
    ledger.stop()
    return tdir_for_domain_txns


@pytest.yield_fixture(scope="module")
def multiPoolNodesCreated(request, tconf, looper, tdir,
                          cliTempLogger, namesOfPools=("pool1", "pool2")):

    multiNodes = []
    for poolName in namesOfPools:
        newPoolTxnNodeNames = [poolName + n for n
                               in ("Alpha", "Beta", "Gamma", "Delta")]
        config_helper = ConfigHelper(tconf, chroot=tdir)
        ledger_dir = os.path.join(config_helper.ledger_base_dir, poolName)
        newPoolTxnData = getPoolTxnData(poolName, newPoolTxnNodeNames)
        newTdirWithPoolTxns = custom_tdir_with_pool_txns(newPoolTxnData, ledger_dir,
                                                         tconf.poolTransactionsFile)
        newTdirWithDomainTxns = custom_tdir_with_domain_txns(
            newPoolTxnData, ledger_dir, domainTxnOrderedFields(), tconf.domainTransactionsFile)
        testPoolNode = TestMultiNode(
            poolName, newPoolTxnNodeNames, tdir, tconf,
            newPoolTxnData, newTdirWithPoolTxns, newTdirWithDomainTxns, None)

        poolCLIBabyGen = CliBuilder(tdir, newTdirWithPoolTxns,
                                    newTdirWithDomainTxns, looper, tconf,
                                    cliTempLogger)
        poolCLIBaby = next(poolCLIBabyGen(poolName))

        # Ugly hack to build several networks
        network_bak = tconf.NETWORK_NAME
        tconf.NETWORK_NAME = poolName
        tdirWithNodeKeepInited(tdir, tconf, NodeConfigHelper, newPoolTxnData, newPoolTxnNodeNames)

        nodes = []
        for nm in newPoolTxnNodeNames:
            config_helper = NodeConfigHelper(nm, tconf, chroot=tdir)
            node = TestNode(nm,
                            config_helper=config_helper,
                            config=tconf,
                            pluginPaths=None)
            looper.add(node)
            nodes.append(node)
        looper.run(checkNodesConnected(nodes))
        ensureElectionsDone(looper=looper, nodes=nodes)

        poolCli = poolCLI(tdir, tconf, poolCLIBaby, newPoolTxnData,
                          newPoolTxnNodeNames, nodes)
        testPoolNode.poolCli = poolCli
        multiNodes.append(testPoolNode)
        tconf.NETWORK_NAME = network_bak

    return multiNodes


@pytest.fixture("module")
def ctx():
    """
    Provides a simple container for test context. Assists with 'be' and 'do'.
    """
    return {}


@pytest.fixture("module")
def be(ctx):
    """
    Fixture that is a 'be' function that closes over the test context.
    'be' allows to change the current cli in the context.
    """
    def _(cli):
        ctx['current_cli'] = cli
    return _


@pytest.fixture("module")
def do(ctx):
    """
    Fixture that is a 'do' function that closes over the test context
    'do' allows to call the do method of the current cli from the context.
    """
    return doByCtx(ctx)


@pytest.fixture(scope="module")
def dump(ctx):

    def _dump():
        logger = getlogger()

        cli = ctx['current_cli']
        nocli = {"cli": False}
        wrts = ''.join(cli.cli.output.writes)
        logger.info('=========================================', extra=nocli)
        logger.info('|             OUTPUT DUMP               |', extra=nocli)
        logger.info('-----------------------------------------', extra=nocli)
        for w in wrts.splitlines():
            logger.info('> ' + w, extra=nocli)
        logger.info('=========================================', extra=nocli)
    return _dump


@pytest.fixture(scope="module")
def bookmark(ctx):
    BM = '~bookmarks~'
    if BM not in ctx:
        ctx[BM] = {}
    return ctx[BM]


@pytest.fixture(scope="module")
def current_cli(ctx):
    def _():
        return ctx['current_cli']
    return _


@pytest.fixture(scope="module")
def get_bookmark(bookmark, current_cli):
    def _():
        return bookmark.get(current_cli(), 0)
    return _


@pytest.fixture(scope="module")
def set_bookmark(bookmark, current_cli):
    def _(val):
        bookmark[current_cli()] = val
    return _


@pytest.fixture(scope="module")
def inc_bookmark(get_bookmark, set_bookmark):
    def _(inc):
        val = get_bookmark()
        set_bookmark(val + inc)
    return _


@pytest.fixture(scope="module")
def expect(current_cli, get_bookmark, inc_bookmark):

    def _expect(expected, mapper=None, line_no=None,
                within=None, ignore_extra_lines=None):
        cur_cli = current_cli()

        def _():
            expected_ = expected if not mapper \
                else [s.format(**mapper) for s in expected]
            assert isinstance(expected_, List)
            bm = get_bookmark()
            actual = ''.join(cur_cli.cli.output.writes).splitlines()[bm:]
            assert isinstance(actual, List)
            explanation = ''
            expected_index = 0
            for i in range(min(len(expected_), len(actual))):
                e = expected_[expected_index]
                assert isinstance(e, str)
                a = actual[i]
                assert isinstance(a, str)
                is_p = isinstance(e, P)
                if (not is_p and a != e) or (is_p and not e.match(a)):
                    if ignore_extra_lines:
                        continue
                    explanation += "line {} doesn't match\n"\
                                   "  expected: {}\n"\
                                   "    actual: {}\n".format(i, e, a)
                expected_index += 1

            if len(expected_) > len(actual):
                for e in expected_:
                    try:
                        p = re.compile(e) if isinstance(e, P) else None
                    except Exception as err:
                        explanation += "ERROR COMPILING REGEX for {}: {}\n".\
                            format(e, err)
                    for a in actual:
                        if (p and p.fullmatch(a)) or a == e:
                            break
                    else:
                        explanation += "missing: {}\n".format(e)

            if len(expected_) < len(actual) and ignore_extra_lines is None:
                for a in actual:
                    for e in expected_:
                        p = re.compile(e) if isinstance(e, P) else None
                        if (p and p.fullmatch(a)) or a == e:
                            break
                    else:
                        explanation += "extra: {}\n".format(a)

            if explanation:
                explanation += "\nexpected:\n"
                for x in expected_:
                    explanation += "  > {}\n".format(x)
                explanation += "\nactual:\n"
                for x in actual:
                    explanation += "  > {}\n".format(x)
                if line_no:
                    explanation += "section ends line number: {}\n".format(
                        line_no)
                pytest.fail(''.join(explanation))
            else:
                inc_bookmark(len(actual))
        if within:
            cur_cli.looper.run(eventually(_, timeout=within))
        else:
            _()

    return _expect


@pytest.fixture(scope="module")
def steward(poolNodesCreated, looper, tdir, stewardWallet):
    return buildStewardClient(looper, tdir, stewardWallet)


@pytest.fixture(scope="module")
def faberAdded(poolNodesCreated,
               looper,
               aliceCLI,
               faberInviteLoaded,
               aliceConnected,
               steward, stewardWallet):
    li = get_connection_request("Faber", aliceCLI.activeWallet)
    createNym(looper, li.remoteIdentifier, steward, stewardWallet,
              role=TRUST_ANCHOR)


@pytest.fixture(scope="module") # noqa
def faberIsRunningWithoutNymAdded(emptyLooper, tdirWithPoolTxns, faberWallet,
                                  faberAgent):
    faber, faberWallet = runningFaber(emptyLooper, tdirWithPoolTxns,
                                      faberWallet, faberAgent, None)
    return faber, faberWallet


@pytest.fixture(scope="module") # noqa
def faberIsRunning(emptyLooper, tdirWithPoolTxns, faberWallet,
                   faberAddedByPhil, faberAgent, faberBootstrap):
    faber, faberWallet = runningFaber(
        emptyLooper, tdirWithPoolTxns, faberWallet, faberAgent, faberAddedByPhil, faberBootstrap)
    return faber, faberWallet


@pytest.fixture(scope="module") # noqa
def acmeIsRunning(emptyLooper, tdirWithPoolTxns, acmeWallet,
                  acmeAddedByPhil, acmeAgent, acmeBootstrap):
    acme, acmeWallet = runningAcme(
        emptyLooper, tdirWithPoolTxns, acmeWallet, acmeAgent, acmeAddedByPhil, acmeBootstrap)

    return acme, acmeWallet


@pytest.fixture(scope="module") # noqa
def thriftIsRunning(emptyLooper, tdirWithPoolTxns, thriftWallet,
                    thriftAddedByPhil, thriftAgent):
    thrift, thriftWallet = runningThrift(emptyLooper, tdirWithPoolTxns,
                                         thriftWallet, thriftAgent,
                                         thriftAddedByPhil)

    return thrift, thriftWallet


@pytest.fixture(scope='module')
def savedKeyringRestored():
    return ['Saved wallet {wallet-name} restored']


# TODO: Need to refactor following three fixture to reuse code
@pytest.yield_fixture(scope="module")
def cliForMultiNodePools(request, multiPoolNodesCreated, tdir,
                         tdirWithPoolTxns, tdirWithDomainTxnsUpdated, tconf,
                         cliTempLogger):
    yield from getCliBuilder(tdir, tconf,
                             tdirWithPoolTxns, tdirWithDomainTxnsUpdated,
                             cliTempLogger, multiPoolNodesCreated)("susan")


@pytest.yield_fixture(scope="module")
def aliceMultiNodePools(request, multiPoolNodesCreated, tdir,
                        tdirWithPoolTxns, tdirWithDomainTxnsUpdated, tconf,
                        cliTempLogger):
    yield from getCliBuilder(tdir, tconf,
                             tdirWithPoolTxns, tdirWithDomainTxnsUpdated,
                             cliTempLogger, multiPoolNodesCreated)("alice")


@pytest.yield_fixture(scope="module")
def earlMultiNodePools(request, multiPoolNodesCreated, tdir,
                       tdirWithPoolTxns, tdirWithDomainTxnsUpdated, tconf,
                       cliTempLogger):
    yield from getCliBuilder(tdir, tconf,
                             tdirWithPoolTxns, tdirWithDomainTxnsUpdated,
                             cliTempLogger, multiPoolNodesCreated)("earl")


@pytest.yield_fixture(scope="module")   # noqa
def trusteeCLI(CliBuilder, poolTxnTrusteeNames):
    yield from CliBuilder(poolTxnTrusteeNames[0])


@pytest.fixture(scope="module")
def trusteeMap(trusteeWallet):
    return {
        'trusteeSeed': bytes(trusteeWallet._signerById(
            trusteeWallet.defaultId).sk).decode(),
        'trusteeIdr': trusteeWallet.defaultId,
    }


@pytest.fixture(scope="module")
def trusteeCli(be, do, trusteeMap, poolNodesStarted, nymAddedOut, trusteeCLI):
    be(trusteeCLI)
    do('new key with seed {trusteeSeed}', expect=[
        'DID for key is {trusteeIdr}',
        'Current DID set to {trusteeIdr}'],
       mapper=trusteeMap)

    if not trusteeCLI._isConnectedToAnyEnv():
        connect_and_check_output(do, trusteeCLI.txn_dir)

    return trusteeCLI


@pytest.fixture(scope="module")
def poolNodesStarted(be, do, poolCLI):
    be(poolCLI)
    return poolCLI


@pytest.fixture(scope="module")
def philCli(be, do, philCLI, trusteeCli, poolTxnData):

    be(philCLI)

    do('prompt Phil', expect=prompt_is('Phil'))

    do('new wallet Phil', expect=['New wallet Phil created',
                                  'Active wallet set to "Phil"'])

    phil_seed = randomSeed()
    phil_signer = DidSigner(seed=phil_seed)

    mapper = {
        'seed': phil_seed.decode(),
        'idr': phil_signer.identifier}
    do('new key with seed {seed}', expect=['Key created in wallet Phil',
                                           'DID for key is {idr}',
                                           'Current DID set to {idr}'],
       mapper=mapper)

    addNym(be, do, trusteeCli,
           phil_signer.identifier,
           verkey=phil_signer.verkey,
           role=Roles.TRUSTEE.name)

    return philCLI


@pytest.fixture(scope="module")
def faberAddedByPhil(be, do, poolNodesStarted, philCli,
                     nymAddedOut, faberMap):
    return addAgent(be, do, philCli, faberMap)


@pytest.fixture(scope="module")
def acmeAddedByPhil(be, do, poolNodesStarted, philCli,
                    nymAddedOut, acmeMap):
    return addAgent(be, do, philCli, acmeMap)


@pytest.fixture(scope="module")
def thriftAddedByPhil(be, do, poolNodesStarted, philCli,
                      nymAddedOut, thriftMap):
    return addAgent(be, do, philCli, thriftMap)


@pytest.fixture(scope='module')
def newStewardVals():
    newStewardSeed = randomSeed()
    signer = DidSigner(seed=newStewardSeed)
    return {
        'newStewardSeed': newStewardSeed.decode(),
        'newStewardIdr': signer.identifier,
        'newStewardVerkey': signer.verkey
    }


@pytest.fixture(scope='module')
def newNodeVals():
    newNodeSeed = randomSeed()
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()

    newNodeData = {
        NODE_IP: nodeIp,
        NODE_PORT: nodePort,
        CLIENT_IP: clientIp,
        CLIENT_PORT: clientPort,
        ALIAS: randomString(6),
        SERVICES: [VALIDATOR],
        BLS_KEY: '0' * 32
    }

    return {
        'newNodeSeed': newNodeSeed.decode(),
        'newNodeIdr': SimpleSigner(seed=newNodeSeed).identifier,
        'newNodeData': newNodeData
    }

@pytest.fixture(scope='module')
def nodeValsEmptyData(newNodeVals):
    node_vals = {}
    node_vals['newNodeData'] = {}
    node_vals['newNodeIdr'] = newNodeVals['newNodeIdr']
    return node_vals

@pytest.yield_fixture(scope="module")
def cliWithNewStewardName(CliBuilder):
    yield from CliBuilder("newSteward")


@pytest.fixture(scope='module')
def newStewardCli(be, do, poolNodesStarted, trusteeCli,
                  cliWithNewStewardName, newStewardVals):
    be(trusteeCli)
    if not trusteeCli._isConnectedToAnyEnv():
        connect_and_check_output(do, trusteeCli.txn_dir)

    do('send NYM dest={{newStewardIdr}} role={role} verkey={{newStewardVerkey}}'
       .format(role=Roles.STEWARD.name),
       within=3,
       expect='Nym {newStewardIdr} added',
       mapper=newStewardVals)

    be(cliWithNewStewardName)

    do('new key with seed {newStewardSeed}', expect=[
        'DID for key is {newStewardIdr}',
        'Current DID set to {newStewardIdr}'],
       mapper=newStewardVals)

    if not cliWithNewStewardName._isConnectedToAnyEnv():
        connect_and_check_output(do, cliWithNewStewardName.txn_dir)

    return cliWithNewStewardName


@pytest.fixture(scope="module")
def newNodeAdded(be, do, poolNodesStarted, philCli, newStewardCli,
                 newNodeVals):
    be(philCli)

    if not philCli._isConnectedToAnyEnv():
        connect_and_check_output(do, philCli.txn_dir)

    be(newStewardCli)
    doSendNodeCmd(do, newNodeVals)
    newNodeData = newNodeVals["newNodeData"]

    def checkClientConnected(client):
        name = newNodeData[ALIAS] + CLIENT_STACK_SUFFIX
        assert name in client.nodeReg

    def checkNodeConnected(nodes):
        for node in nodes:
            name = newNodeData[ALIAS]
            assert name in node.nodeReg

    timeout = waits.expectedClientToPoolConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )

    newStewardCli.looper.run(eventually(checkClientConnected,
                                        newStewardCli.activeClient,
                                        timeout=timeout))

    philCli.looper.run(eventually(checkClientConnected,
                                  philCli.activeClient,
                                  timeout=timeout))

    poolNodesStarted.looper.run(
        eventually(
            checkNodeConnected,
            list(
                poolNodesStarted.nodes.values()),
            timeout=timeout))
    return newNodeVals


@pytest.fixture(scope='module')
def nodeIds(poolNodesStarted):
    return next(iter(poolNodesStarted.nodes.values())).poolManager.nodeIds
