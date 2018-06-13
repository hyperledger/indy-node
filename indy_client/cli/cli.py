import ast
import asyncio
import datetime
import importlib
import json
import os
import traceback
from collections import OrderedDict
from functools import partial
from hashlib import sha256
from operator import itemgetter
from typing import Dict, Any, Tuple, Callable, NamedTuple

import base58
from libnacl import randombytes
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.layout.lexers import SimpleLexer
from pygments.token import Token

from anoncreds.protocol.exceptions import SchemaNotFoundError
from anoncreds.protocol.globals import KEYS, ATTR_NAMES
from anoncreds.protocol.types import Schema, ID, ProofRequest
from indy_client.agent.constants import EVENT_NOTIFY_MSG, EVENT_POST_ACCEPT_INVITE, \
    EVENT_NOT_CONNECTED_TO_ANY_ENV
from indy_client.agent.msg_constants import ERR_NO_PROOF_REQUEST_SCHEMA_FOUND
from indy_client.agent.walleted_agent import WalletedAgent
from indy_client.cli.command import acceptConnectionCmd, connectToCmd, \
    disconnectCmd, loadFileCmd, newDIDCmd, pingTargetCmd, reqClaimCmd, \
    sendAttribCmd, sendProofCmd, sendGetNymCmd, sendClaimDefCmd, sendNodeCmd, \
    sendGetAttrCmd, sendGetSchemaCmd, sendGetClaimDefCmd, \
    sendNymCmd, sendPoolUpgCmd, sendSchemaCmd, setAttrCmd, showClaimCmd, \
    listClaimsCmd, showFileCmd, showConnectionCmd, syncConnectionCmd, addGenesisTxnCmd, \
    sendProofRequestCmd, showProofRequestCmd, reqAvailClaimsCmd, listConnectionsCmd, sendPoolConfigCmd, changeKeyCmd
from indy_client.cli.helper import getNewClientGrams, \
    USAGE_TEXT, NEXT_COMMANDS_TO_TRY_TEXT
from indy_client.client.client import Client
from indy_client.client.wallet.attribute import Attribute, LedgerStore
from indy_client.client.wallet.connection import Connection
from indy_client.client.wallet.node import Node
from indy_client.client.wallet.pool_config import PoolConfig
from indy_client.client.wallet.upgrade import Upgrade
from indy_client.client.wallet.wallet import Wallet
from indy_client.utils.migration import combined_migration
from indy_client.utils.migration.combined_migration import \
    is_cli_base_dir_untouched, legacy_base_dir_exists
from indy_common.auth import Authoriser
from indy_common.config_util import getConfig
from indy_common.constants import TARGET_NYM, ROLE, TXN_TYPE, NYM, REF, \
    ACTION, SHA256, TIMEOUT, SCHEDULE, START, JUSTIFICATION, NULL, WRITES, \
    REINSTALL, SCHEMA_ATTR_NAMES
from indy_common.exceptions import InvalidConnectionException, ConnectionAlreadyExists, \
    ConnectionNotFound, NotConnectedToNetwork
from indy_common.identity import Identity
from indy_common.roles import Roles
from indy_common.txn_util import getTxnOrderedFields
from indy_common.util import ensureReqCompleted, getIndex, \
    invalidate_config_caches
from indy_node.__metadata__ import __version__
from ledger.genesis_txn.genesis_txn_file_util import genesis_txn_file
from plenum.cli.cli import Cli as PlenumCli
from plenum.cli.constants import PROMPT_ENV_SEPARATOR, NO_ENV
from plenum.cli.helper import getClientGrams
from plenum.cli.phrase_word_completer import PhraseWordCompleter
from plenum.common.constants import NAME, VERSION, VERKEY, DATA, TXN_ID, FORCE, RAW
from plenum.common.exceptions import OperationError
from plenum.common.member.member import Member
from plenum.common.signer_did import DidSigner
from plenum.common.txn_util import createGenesisTxnFile, get_payload_data
from plenum.common.util import randomString, getWalletFilePath
from stp_core.crypto.signer import Signer
from stp_core.crypto.util import cleanSeed
from stp_core.network.port_dispenser import genHa

try:
    nodeMod = importlib.import_module('indy_node.server.node')
    nodeClass = nodeMod.Node
except ImportError:
    nodeClass = None

"""
Objective
The plenum cli bootstraps client keys by just adding them to the nodes.
Indy needs the client nyms to be added as transactions first.
I'm thinking maybe the cli needs to support something like this:
new node all
<each node reports genesis transactions>
new client steward with DID <nym> (nym matches the genesis transactions)
client steward add bob (cli creates a signer and an ADDNYM for that signer's
cryptonym, and then an alias for bobto that cryptonym.)
new client bob (cli uses the signer previously stored for this client)
"""

Context = NamedTuple("Context", [("link", Connection),
                                 ("proofRequest", Any),
                                 ("selfAttestedAttrs", Any)])


class IndyCli(PlenumCli):
    name = 'indy'
    properName = 'Indy'
    fullName = 'Indy Identity platform'
    githubUrl = 'https://github.com/hyperledger/indy-node'

    NodeClass = nodeClass
    ClientClass = Client
    _genesisTransactions = []

    override_file_path = None

    def __init__(self, *args, **kwargs):
        IndyCli._migrate_legacy_app_data_if_just_upgraded_and_user_agrees()

        self.aliases = {}  # type: Dict[str, Signer]
        self.trustAnchors = set()
        self.users = set()
        self._agent = None

        # This specifies which environment the cli is connected to test or live
        self.activeEnv = None

        super().__init__(*args, **kwargs)

        # Load available environments
        self.envs = self.get_available_networks()

        # TODO bad code smell
        self.curContext = Context(None, None, {})  # type: Context

    @staticmethod
    def _migrate_legacy_app_data_if_just_upgraded_and_user_agrees():
        if is_cli_base_dir_untouched() and legacy_base_dir_exists():
            print('Application data from previous Indy version has been found')
            answer = prompt('Do you want to migrate it? [Y/n] ')

            if not answer or answer.upper().startswith('Y'):
                try:
                    combined_migration.migrate()
                    # Invalidate config caches to pick up overridden config
                    # parameters from migrated application data
                    invalidate_config_caches()
                    print('Application data has been migrated')

                except Exception as e:
                    print('Error occurred when trying to migrate'
                          ' application data: {}'.format(e))
                    traceback.print_exc()
                    print('Application data has not been migrated')

            else:
                print('Application data was not migrated')

    @staticmethod
    def getCliVersion():
        return __version__

    @property
    def pool_ledger_dir(self):
        if not self.activeEnv:
            return self.ledger_base_dir
        return os.path.join(self.ledger_base_dir, self.activeEnv)

    @property
    def lexers(self):
        lexerNames = [
            'send_nym',
            'send_get_nym',
            'send_attrib',
            'send_get_attr',
            'send_schema',
            'send_get_schema',
            'send_claim_def',
            'send_get_claim_def',
            'send_node',
            'send_pool_upg',
            'add_genesis',
            'show_file',
            'conn',
            'disconn',
            'load_file',
            'show_connection',
            'sync_connection',
            'ping_target'
            'show_claim',
            'list_claims',
            'list_connections',
            # 'show_claim_req',
            'show_proof_request',
            'request_claim',
            'accept_connection_request',
            'set_attr',
            'send_proof_request'
            'send_proof',
            'new_id',
            'request_avail_claims',
            'change_ckey'
        ]
        lexers = {n: SimpleLexer(Token.Keyword) for n in lexerNames}
        # Add more lexers to base class lexers
        return {**super().lexers, **lexers}

    @property
    def completers(self):
        completers = {}
        completers["nym"] = WordCompleter([])
        completers["role"] = WordCompleter(
            [Roles.TRUST_ANCHOR.name, Roles.STEWARD.name])
        completers["send_nym"] = PhraseWordCompleter(sendNymCmd.id)
        completers["send_get_nym"] = PhraseWordCompleter(sendGetNymCmd.id)
        completers["send_attrib"] = PhraseWordCompleter(sendAttribCmd.id)
        completers["send_get_attr"] = PhraseWordCompleter(sendGetAttrCmd.id)
        completers["send_schema"] = PhraseWordCompleter(sendSchemaCmd.id)
        completers["send_get_schema"] = PhraseWordCompleter(
            sendGetSchemaCmd.id)
        completers["send_claim_def"] = PhraseWordCompleter(sendClaimDefCmd.id)
        completers["send_get_claim_def"] = PhraseWordCompleter(
            sendGetClaimDefCmd.id)
        completers["send_node"] = PhraseWordCompleter(sendNodeCmd.id)
        completers["send_pool_upg"] = PhraseWordCompleter(sendPoolUpgCmd.id)
        completers["send_pool_config"] = PhraseWordCompleter(
            sendPoolConfigCmd.id)
        completers["add_genesis"] = PhraseWordCompleter(
            addGenesisTxnCmd.id)
        completers["show_file"] = WordCompleter([showFileCmd.id])
        completers["load_file"] = WordCompleter([loadFileCmd.id])
        completers["show_connection"] = PhraseWordCompleter(
            showConnectionCmd.id)
        completers["conn"] = WordCompleter([connectToCmd.id])
        completers["disconn"] = WordCompleter([disconnectCmd.id])
        completers["env_name"] = WordCompleter(self.get_available_networks())
        completers["sync_connection"] = WordCompleter([syncConnectionCmd.id])
        completers["ping_target"] = WordCompleter([pingTargetCmd.id])
        completers["show_claim"] = PhraseWordCompleter(showClaimCmd.id)
        completers["request_claim"] = PhraseWordCompleter(reqClaimCmd.id)
        completers["accept_connection_request"] = PhraseWordCompleter(
            acceptConnectionCmd.id)
        completers["set_attr"] = WordCompleter([setAttrCmd.id])
        completers["new_id"] = PhraseWordCompleter(newDIDCmd.id)
        completers["list_claims"] = PhraseWordCompleter(listClaimsCmd.id)
        completers["list_connections"] = PhraseWordCompleter(
            listConnectionsCmd.id)
        completers["show_proof_request"] = PhraseWordCompleter(
            showProofRequestCmd.id)
        completers["send_proof_request"] = PhraseWordCompleter(
            sendProofRequestCmd.id)
        completers["send_proof"] = PhraseWordCompleter(sendProofCmd.id)
        completers["request_avail_claims"] = PhraseWordCompleter(
            reqAvailClaimsCmd.id)
        completers["change_ckey"] = PhraseWordCompleter(changeKeyCmd.id)

        return {**super().completers, **completers}

    def initializeGrammar(self):
        self.clientGrams = getClientGrams() + getNewClientGrams()
        super().initializeGrammar()

    @property
    def actions(self):
        actions = super().actions
        # Add more actions to base class for indy CLI
        if self._sendNymAction not in actions:
            actions.extend([self._sendNymAction,
                            self._sendGetNymAction,
                            self._sendAttribAction,
                            self._sendGetAttrAction,
                            self._sendNodeAction,
                            self._sendPoolUpgAction,
                            self._sendPoolConfigAction,
                            self._sendSchemaAction,
                            self._sendGetSchemaAction,
                            self._sendClaimDefAction,
                            self._sendGetClaimDefAction,
                            self._addGenTxnAction,
                            self._showFile,
                            self._loadFile,
                            self._showConnection,
                            self._connectTo,
                            self._disconnect,
                            self._syncConnection,
                            self._pingTarget,
                            self._showClaim,
                            self._listClaims,
                            self._listConnections,
                            self._reqClaim,
                            self._showProofRequest,
                            self._accept_request_connection,
                            self._setAttr,
                            self._sendProofRequest,
                            self._sendProof,
                            self._newDID,
                            self._reqAvailClaims,
                            self._change_current_key_req
                            ])
        return actions

    @PlenumCli.activeWallet.setter
    def activeWallet(self, wallet):
        PlenumCli.activeWallet.fset(self, wallet)
        if self._agent:
            self._agent.wallet = self._activeWallet

    @staticmethod
    def _getSetAttrUsage():
        return ['{} <attr-name> to <attr-value>'.format(setAttrCmd.id)]

    @staticmethod
    def _getSendProofUsage(proofRequest: ProofRequest=None,
                           inviter: Connection=None):
        return ['{} "{}" to "{}"'.format(
            sendProofCmd.id,
            proofRequest.name or "<proof-request-name>",
            inviter.name or "<inviter-name>")]

    @staticmethod
    def _getShowFileUsage(filePath=None):
        return ['{} {}'.format(showFileCmd.id, filePath or "<file-path>")]

    @staticmethod
    def _getLoadFileUsage(filePath=None):
        return ['{} {}'.format(
            loadFileCmd.id,
            filePath or "<file-path>")]

    @staticmethod
    def _getShowProofRequestUsage(proofRequest: ProofRequest=None):
        return ['{} "{}"'.format(
            showProofRequestCmd.id,
            (proofRequest and proofRequest.name) or '<proof-request-name>')]

    @staticmethod
    def _getShowClaimUsage(claimName=None):
        return ['{} "{}"'.format(
            showClaimCmd.id,
            claimName or "<claim-name>")]

    @staticmethod
    def _getReqClaimUsage(claimName=None):
        return ['{} "{}"'.format(
            reqClaimCmd.id,
            claimName or "<claim-name>")]

    @staticmethod
    def _getShowConnectionUsage(connectionName=None):
        return ['{} "{}"'.format(
            showConnectionCmd.id,
            connectionName or "<connection-name>")]

    @staticmethod
    def _getSyncConnectionUsage(connectionName=None):
        return ['{} "{}"'.format(
            syncConnectionCmd.id,
            connectionName or "<connection-name>")]

    @staticmethod
    def _getAcceptConnectionUsage(connectionName=None):
        return ['{} "{}"'.format(
            acceptConnectionCmd.id,
            connectionName or "<connection-name>")]

    @staticmethod
    def _getPromptUsage():
        return ["prompt <principal name>"]

    @property
    def allEnvNames(self):
        return "|".join(sorted(self.envs, reverse=True))

    def _getConnectUsage(self):
        return ["{} <{}>".format(
            connectToCmd.id,
            self.allEnvNames)]

    def _printMsg(self, notifier, msg):
        self.print(msg)

    def _printSuggestionPostAcceptConnection(self, notifier,
                                             connection: Connection):
        suggestions = []
        if len(connection.availableClaims) > 0:
            claimName = "|".join([n.name for n in connection.availableClaims])
            claimName = claimName or "<claim-name>"
            suggestions += self._getShowClaimUsage(claimName)
            suggestions += self._getReqClaimUsage(claimName)
        if len(connection.proofRequests) > 0:
            for pr in connection.proofRequests:
                suggestions += self._getShowProofRequestUsage(pr)
                suggestions += self._getSendProofUsage(pr, connection)
        if suggestions:
            self.printSuggestion(suggestions)
        else:
            self.print("")

    def sendToAgent(self, msg: Any, connection: Connection):
        if not self.agent:
            return

        endpoint = connection.remoteEndPoint
        self.agent.sendMessage(msg, ha=endpoint)

    @property
    def walletClass(self):
        return Wallet

    @property
    def genesisTransactions(self):
        return self._genesisTransactions

    def reset(self):
        self._genesisTransactions = []

    def newNode(self, nodeName: str):
        createGenesisTxnFile(self.genesisTransactions, self.basedirpath,
                             self.config.domainTransactionsFile,
                             getTxnOrderedFields(), reset=False)
        nodesAdded = super().newNode(nodeName)
        return nodesAdded

    def _printCannotSyncSinceNotConnectedEnvMessage(self):

        self.print("Cannot sync because not connected. Please connect first.")
        self._printConnectUsage()

    def _printNotConnectedEnvMessage(self,
                                     prefix="Not connected to Indy network"):

        self.print("{}. Please connect first.".format(prefix))
        self._printConnectUsage()

    def _printConnectUsage(self):
        self.printUsage(self._getConnectUsage())

    def newClient(self, clientName,
                  config=None):
        if not self.activeEnv:
            self._printNotConnectedEnvMessage()
            # TODO: Return a dummy object that catches all attributes and
            # method calls and does nothing. Alo the dummy object should
            # initialise to null
            return DummyClient()

        client = super().newClient(clientName, config=config)
        if self.activeWallet:
            client.registerObserver(self.activeWallet.handleIncomingReply)
            self.activeWallet.pendSyncRequests()
            prepared = self.activeWallet.preparePending()
            client.submitReqs(*prepared)

        # If agent was created before the user connected to a test environment
        if self._agent:
            self._agent.client = client
        return client

    def registerAgentListeners(self, agent):
        agent.registerEventListener(EVENT_NOTIFY_MSG, self._printMsg)
        agent.registerEventListener(EVENT_POST_ACCEPT_INVITE,
                                    self._printSuggestionPostAcceptConnection)
        agent.registerEventListener(EVENT_NOT_CONNECTED_TO_ANY_ENV,
                                    self._handleNotConnectedToAnyEnv)

    def deregisterAgentListeners(self, agent):
        agent.deregisterEventListener(EVENT_NOTIFY_MSG, self._printMsg)
        agent.deregisterEventListener(
            EVENT_POST_ACCEPT_INVITE,
            self._printSuggestionPostAcceptConnection)
        agent.deregisterEventListener(EVENT_NOT_CONNECTED_TO_ANY_ENV,
                                      self._handleNotConnectedToAnyEnv)

    @property
    def agent(self) -> WalletedAgent:
        if self._agent is None:
            _, port = genHa()
            agent = WalletedAgent(
                name=randomString(6),
                basedirpath=self.basedirpath,
                client=self.activeClient if self.activeEnv else None,
                wallet=self.activeWallet,
                loop=self.looper.loop,
                port=port)
            self.agent = agent
        return self._agent

    @agent.setter
    def agent(self, agent):
        if self._agent is not None:
            self.deregisterAgentListeners(self._agent)
            self.looper.removeProdable(self._agent)

        self._agent = agent

        if agent is not None:
            self.registerAgentListeners(self._agent)
            self.looper.add(self._agent)
            self._activeWallet = self._agent.wallet
            self.wallets[self._agent.wallet.name] = self._agent.wallet

    def _handleNotConnectedToAnyEnv(self, notifier, msg):
        self.print("\n{}\n".format(msg))
        self._printNotConnectedEnvMessage()

    @staticmethod
    def bootstrapClientKeys(idr, verkey, nodes):
        pass

    def _clientCommand(self, matchedVars):
        if matchedVars.get('client') == 'client':
            r = super()._clientCommand(matchedVars)
            if r:
                return True

            client_name = matchedVars.get('client_name')
            if client_name not in self.clients:
                self.print("{} cannot add a new user".
                           format(client_name), Token.BoldOrange)
                return True
            client_action = matchedVars.get('cli_action')
            if client_action == 'add':
                otherClientName = matchedVars.get('other_client_name')
                role = self._getRole(matchedVars)
                signer = DidSigner()
                nym = signer.verstr
                return self._addNym(nym, Identity.correctRole(role),
                                    newVerKey=None,
                                    otherClientName=otherClientName)

    def _getRole(self, matchedVars):
        """
        :param matchedVars:
        :return: NULL or the role's integer value
        """
        role = matchedVars.get(ROLE)
        if role is not None and role.strip() == '':
            role = NULL
        else:
            valid = Authoriser.isValidRoleName(role)
            if valid:
                role = Authoriser.getRoleFromName(role)
            else:
                self.print("Invalid role. Valid roles are: {}".
                           format(", ".join(map(lambda r: r.name, Roles))),
                           Token.Error)
                return False
        return role

    def _getNym(self, nym):
        identity = Identity(identifier=nym)
        req = self.activeWallet.requestIdentity(
            identity, sender=self.activeWallet.defaultId)
        self.activeClient.submitReqs(req)
        self.print("Getting nym {}".format(nym))

        def getNymReply(reply, err, *args):
            try:
                if err:
                    self.print("Error: {}".format(err), Token.BoldOrange)
                    return

                if reply and reply[DATA]:
                    data = json.loads(reply[DATA])
                    if data:
                        idr = base58.b58decode(nym)
                        if data.get(VERKEY) is None:
                            if len(idr) == 32:
                                self.print(
                                    "Current verkey is same as DID {}"
                                    .format(nym), Token.BoldBlue)
                            else:
                                self.print(
                                    "No verkey ever assigned to the DID {}".
                                    format(nym), Token.BoldBlue)
                            return
                        if data.get(VERKEY) == '':
                            self.print("No active verkey found for the DID {}".
                                       format(nym), Token.BoldBlue)
                        else:
                            if data[ROLE] is not None and data[ROLE] != '':
                                self.print("Current verkey for NYM {} is {} with role {}"
                                           .format(nym, data[VERKEY],
                                                   Roles.nameFromValue(data[ROLE])),
                                           Token.BoldBlue)
                            else:
                                self.print("Current verkey for NYM {} is {}"
                                           .format(nym, data[VERKEY]), Token.BoldBlue)
                else:
                    self.print("NYM {} not found".format(nym), Token.BoldBlue)
            except BaseException as e:
                self.print("Error during fetching verkey: {}".format(e),
                           Token.BoldOrange)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, getNymReply)

    def _addNym(self, nym, role, newVerKey=None,
                otherClientName=None, custom_clb=None):
        idy = Identity(nym, verkey=newVerKey, role=role)
        try:
            self.activeWallet.addTrustAnchoredIdentity(idy)
        except Exception as e:
            if e.args[0] == 'DID already added':
                pass
            else:
                raise e
        reqs = self.activeWallet.preparePending()
        req = self.activeClient.submitReqs(*reqs)[0][0]
        printStr = "Adding nym {}".format(nym)

        if otherClientName:
            printStr = printStr + " for " + otherClientName
        self.print(printStr)

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Error: {}".format(error), Token.BoldBlue)
            else:
                self.print("Nym {} added".format(get_payload_data(reply)[TARGET_NYM]),
                           Token.BoldBlue)

        self.looper.loop.call_later(.2,
                                    self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient,
                                    custom_clb or out)
        return True

    def _addAttribToNym(self, nym, raw, enc, hsh):
        attrib = self.activeWallet.build_attrib(nym, raw, enc, hsh)
        # TODO: What is the purpose of this?
        # if nym != self.activeWallet.defaultId:
        #     attrib.dest = nym

        self.activeWallet.addAttribute(attrib)
        reqs = self.activeWallet.preparePending()
        req, errs = self.activeClient.submitReqs(*reqs)
        if errs:
            for err in errs:
                self.print("Request error: {}".format(err), Token.BoldOrange)

        if not req:
            return

        req = req[0]

        self.print("Adding attributes {} for {}".format(attrib.value, nym))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Error: {}".format(error), Token.BoldOrange)
            else:
                self.print("Attribute added for nym {}".
                           format(get_payload_data(reply)[TARGET_NYM]), Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, out)

    def _getAttr(self, nym, raw, enc, hsh):
        assert int(bool(raw)) + int(bool(enc)) + int(bool(hsh)) == 1
        if raw:
            led_store = LedgerStore.RAW
            data = raw
        elif enc:
            led_store = LedgerStore.ENC
            data = enc
        elif hsh:
            led_store = LedgerStore.HASH
            data = hsh
        else:
            raise RuntimeError('One of raw, enc, or hash are required.')

        attrib = Attribute(data, dest=nym, ledgerStore=led_store)
        req = self.activeWallet.requestAttribute(
            attrib, sender=self.activeWallet.defaultId)
        self.activeClient.submitReqs(req)
        self.print("Getting attr {}".format(nym))

        def getAttrReply(reply, err, *args):
            if reply and reply[DATA]:
                data_to_print = None
                if RAW in reply:
                    data = json.loads(reply[DATA])
                    if data:
                        data_to_print = json.dumps(data)
                else:
                    data_to_print = reply[DATA]
                if data_to_print:
                    self.print("Found attribute {}".format(data_to_print))
            else:
                self.print("Attr not found")

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, getAttrReply)

    def _getSchema(self, nym, name, version):
        req = self.activeWallet.requestSchema(
            nym, name, version, sender=self.activeWallet.defaultId)
        self.activeClient.submitReqs(req)
        self.print("Getting schema {}".format(nym))

        def getSchema(reply, err, *args):
            try:
                if reply and reply[DATA] and SCHEMA_ATTR_NAMES in reply[DATA]:
                    self.print(
                        "Found schema {}"
                        .format(reply[DATA]))
                else:
                    self.print("Schema not found")
            except BaseException:
                self.print('"data" must be in proper format', Token.Error)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, getSchema)

    def _getClaimDef(self, seqNo, signature):
        req = self.activeWallet.requestClaimDef(
            seqNo, signature, sender=self.activeWallet.defaultId)
        self.activeClient.submitReqs(req)
        self.print("Getting claim def {}".format(seqNo))

        def getClaimDef(reply, err, *args):
            try:
                if reply and reply[DATA]:
                    self.print(
                        "Found claim def {}"
                        .format(reply[DATA]))
                else:
                    self.print("Claim def not found")
            except BaseException:
                self.print('"data" must be in proper format', Token.Error)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, getClaimDef)

    def _sendNodeTxn(self, nym, data):
        node = Node(nym, data, self.activeDID)
        self.activeWallet.addNode(node)
        reqs = self.activeWallet.preparePending()
        req = self.activeClient.submitReqs(*reqs)[0][0]
        self.print("Sending node request for node DID {} by {} "
                   "(request id: {})".format(nym, self.activeDID,
                                             req.reqId))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Node request failed with error: {}".format(
                    error), Token.BoldOrange)
            else:
                self.print(
                    "Node request completed {}".format(
                        get_payload_data(reply)[TARGET_NYM]),
                    Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, out)

    def _sendPoolUpgTxn(
            self,
            name,
            version,
            action,
            sha256,
            schedule=None,
            justification=None,
            timeout=None,
            force=False,
            reinstall=False):
        upgrade = Upgrade(
            name,
            version,
            action,
            sha256,
            schedule=schedule,
            trustee=self.activeDID,
            timeout=timeout,
            justification=justification,
            force=force,
            reinstall=reinstall)
        self.activeWallet.doPoolUpgrade(upgrade)
        reqs = self.activeWallet.preparePending()
        req = self.activeClient.submitReqs(*reqs)[0][0]
        self.print("Sending pool upgrade {} for version {}".
                   format(name, version))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print(
                    "Pool upgrade failed: {}".format(error),
                    Token.BoldOrange)
            else:
                self.print("Pool Upgrade Transaction Scheduled",
                           Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, out)

    def _sendPoolConfigTxn(self, writes, force=False):
        poolConfig = PoolConfig(trustee=self.activeDID,
                                writes=writes, force=force)
        self.activeWallet.doPoolConfig(poolConfig)
        reqs = self.activeWallet.preparePending()
        req = self.activeClient.submitReqs(*reqs)[0][0]
        self.print(
            "Sending pool config writes={} force={}".format(
                writes, force))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Pool config failed: {}".format(
                    error), Token.BoldOrange)
            else:
                self.print("Pool config successful", Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.activeClient, out)

    @staticmethod
    def parseAttributeString(attrs):
        attrInput = {}
        for attr in attrs.split(','):
            name, value = attr.split('=')
            name, value = name.strip(), value.strip()
            attrInput[name] = value
        return attrInput

    def _sendNymAction(self, matchedVars):
        if matchedVars.get('send_nym') == sendNymCmd.id:
            if not self.canMakeIndyRequest:
                return True
            nym = matchedVars.get('dest_id')
            role = self._getRole(matchedVars)
            newVerKey = matchedVars.get('new_ver_key')
            if matchedVars.get('verkey') and newVerKey is None:
                newVerKey = ''
            elif newVerKey is not None:
                newVerKey = newVerKey.strip()
            self._addNym(nym, role, newVerKey=newVerKey)
            return True

    def _sendGetNymAction(self, matchedVars):
        if matchedVars.get('send_get_nym') == sendGetNymCmd.id:
            if not self.hasAnyKey:
                return True
            if not self.canMakeIndyRequest:
                return True
            destId = matchedVars.get('dest_id')
            self._getNym(destId)
            return True

    def _sendAttribAction(self, matchedVars):
        if matchedVars.get('send_attrib') == sendAttribCmd.id:
            if not self.canMakeIndyRequest:
                return True
            nym = matchedVars.get('dest_id')
            raw = matchedVars.get('raw', None)
            enc = matchedVars.get('enc', None)
            hsh = matchedVars.get('hash', None)
            self._addAttribToNym(nym, raw, enc, hsh)
            return True

    def _sendGetAttrAction(self, matchedVars):
        if matchedVars.get('send_get_attr') == sendGetAttrCmd.id:
            if not self.hasAnyKey:
                return True
            if not self.canMakeIndyRequest:
                return True
            nym = matchedVars.get('dest_id')
            raw = matchedVars.get('raw', None)
            enc = matchedVars.get('enc', None)
            hsh = matchedVars.get('hash', None)
            self._getAttr(nym, raw, enc, hsh)
            return True

    def _sendGetSchemaAction(self, matchedVars):
        if matchedVars.get('send_get_schema') == sendGetSchemaCmd.id:
            if not self.canMakeIndyRequest:
                return True
            self.logger.debug("Processing GET_SCHEMA request")
            nym = matchedVars.get('dest_id')
            name = matchedVars.get('name')
            version = matchedVars.get('version')
            self._getSchema(nym, name, version)
            return True

    def _sendGetClaimDefAction(self, matchedVars):
        if matchedVars.get('send_get_claim_def') == sendGetClaimDefCmd.id:
            if not self.canMakeIndyRequest:
                return True
            self.logger.debug("Processing GET_CLAIM_DEF request")
            seqNo = int(matchedVars.get('ref'))
            signature = matchedVars.get('signature_type')
            self._getClaimDef(seqNo, signature)
            return True

    def _sendNodeAction(self, matchedVars):
        if matchedVars.get('send_node') == sendNodeCmd.id:
            if not self.canMakeIndyRequest:
                return True
            nym = matchedVars.get('dest_id')
            data = matchedVars.get('data').strip()
            try:
                data = ast.literal_eval(data)
                self._sendNodeTxn(nym, data)
            except BaseException:
                self.print('"data" must be in proper format', Token.Error)
            return True

    def _sendPoolUpgAction(self, matchedVars):
        if matchedVars.get('send_pool_upg') == sendPoolUpgCmd.id:
            if not self.canMakeIndyRequest:
                return True
            name = matchedVars.get(NAME).strip()
            version = matchedVars.get(VERSION).strip()
            action = matchedVars.get(ACTION).strip()
            sha256 = matchedVars.get(SHA256).strip()
            timeout = matchedVars.get(TIMEOUT)
            schedule = matchedVars.get(SCHEDULE)
            justification = matchedVars.get(JUSTIFICATION)
            force = matchedVars.get(FORCE, "False")
            reinstall = matchedVars.get(REINSTALL, "False")
            force = force == "True"
            reinstall = reinstall == "True"
            if action == START:
                if not schedule:
                    self.print('{} need to be provided'.format(SCHEDULE),
                               Token.Error)
                    return True
                if not timeout:
                    self.print('{} need to be provided'.format(TIMEOUT),
                               Token.Error)
                    return True
            try:
                if schedule:
                    schedule = ast.literal_eval(schedule.strip())
            except BaseException:
                self.print('"schedule" must be in proper format', Token.Error)
                return True
            if timeout:
                timeout = int(timeout.strip())
            self._sendPoolUpgTxn(name, version, action, sha256,
                                 schedule=schedule, timeout=timeout,
                                 justification=justification, force=force,
                                 reinstall=reinstall)
            return True

    def _sendPoolConfigAction(self, matchedVars):
        if matchedVars.get('send_pool_config') == sendPoolConfigCmd.id:
            if not self.canMakeIndyRequest:
                return True
            writes = matchedVars.get(WRITES, "False")
            writes = writes == "True"
            force = matchedVars.get(FORCE, "False")
            force = force == "True"
            self._sendPoolConfigTxn(writes, force=force)
            return True

    def _sendSchemaAction(self, matchedVars):
        if matchedVars.get('send_schema') == sendSchemaCmd.id:
            self.agent.loop.call_soon(asyncio.ensure_future,
                                      self._sendSchemaActionAsync(matchedVars))
            return True

    async def _sendSchemaActionAsync(self, matchedVars):
        if not self.canMakeIndyRequest:
            return True

        try:
            schema = await self.agent.issuer.genSchema(
                name=matchedVars.get(NAME),
                version=matchedVars.get(VERSION),
                attrNames=[s.strip() for s in matchedVars.get(KEYS).split(",")])
        except OperationError as ex:
            self.print("Can not add SCHEMA {}".format(ex),
                       Token.BoldOrange)
            return False

        self.print("The following schema is published "
                   "to the Indy distributed ledger\n", Token.BoldBlue,
                   newline=False)
        self.print("{}".format(str(schema)))
        self.print("Sequence number is {}".format(schema.seqId),
                   Token.BoldBlue)

        return True

    def _sendClaimDefAction(self, matchedVars):
        if matchedVars.get('send_claim_def') == sendClaimDefCmd.id:
            self.agent.loop.call_soon(
                asyncio.ensure_future,
                self._sendClaimDefActionAsync(matchedVars))
            return True

    async def _sendClaimDefActionAsync(self, matchedVars):
        if not self.canMakeIndyRequest:
            return True
        reference = int(matchedVars.get(REF))
        id = ID(schemaId=reference)
        try:
            pk, pkR = await self.agent.issuer.genKeys(id)
        except SchemaNotFoundError:
            self.print("Schema with seqNo {} not found".format(reference),
                       Token.BoldOrange)
            return False

        self.print("The claim definition was published to the"
                   " Indy distributed ledger:\n", Token.BoldBlue,
                   newline=False)
        self.print("Sequence number is {}".format(pk[0].seqId),
                   Token.BoldBlue)

        return True

    def printUsageMsgs(self, msgs):
        for m in msgs:
            self.print('    {}'.format(m))
        self.print("\n")

    def printSuggestion(self, msgs):
        self.print("\n{}".format(NEXT_COMMANDS_TO_TRY_TEXT))
        self.printUsageMsgs(msgs)

    def printUsage(self, msgs):
        self.print("\n{}".format(USAGE_TEXT))
        self.printUsageMsgs(msgs)

    def _loadFile(self, matchedVars):
        if matchedVars.get('load_file') == loadFileCmd.id:
            if not self.agent:
                self._printNotConnectedEnvMessage()
            else:
                givenFilePath = matchedVars.get('file_path')
                filePath = IndyCli._getFilePath(givenFilePath)
                try:
                    # TODO: Shouldn't just be the wallet be involved in loading
                    # a request.
                    connection = self.agent.load_request_file(filePath)
                    self._printShowAndAcceptConnectionUsage(connection.name)
                except (FileNotFoundError, TypeError):
                    self.print("Given file does not exist")
                    msgs = self._getShowFileUsage() + self._getLoadFileUsage()
                    self.printUsage(msgs)
                except ConnectionAlreadyExists:
                    self.print("Connection already exists")
                except ConnectionNotFound:
                    self.print("No connection request found in the given file")
                except ValueError:
                    self.print("Input is not a valid json"
                               "please check and try again")
                except InvalidConnectionException as e:
                    self.print(e.args[0])
            return True

    @classmethod
    def _getFilePath(cls, givenPath, caller_file=None):
        curDirPath = os.path.dirname(os.path.abspath(caller_file or
                                                     cls.override_file_path or
                                                     __file__))
        sampleExplicitFilePath = curDirPath + "/../../" + givenPath
        sampleImplicitFilePath = curDirPath + "/../../sample/" + givenPath

        if os.path.isfile(givenPath):
            return givenPath
        elif os.path.isfile(sampleExplicitFilePath):
            return sampleExplicitFilePath
        elif os.path.isfile(sampleImplicitFilePath):
            return sampleImplicitFilePath
        else:
            return None

    def _get_request_matching_connections(self, connectionName):
        exactMatched = {}
        likelyMatched = {}
        # if we want to search in all wallets, then,
        # change [self.activeWallet] to self.wallets.values()
        walletsToBeSearched = [self.activeWallet]  # self.wallets.values()
        for w in walletsToBeSearched:
            # TODO: This should be moved to wallet
            requests = w.getMatchingConnections(connectionName)
            for i in requests:
                if i.name == connectionName:
                    if w.name in exactMatched:
                        exactMatched[w.name].append(i)
                    else:
                        exactMatched[w.name] = [i]
                else:
                    if w.name in likelyMatched:
                        likelyMatched[w.name].append(i)
                    else:
                        likelyMatched[w.name] = [i]

        # TODO: instead of a comment, this should be implemented as a test
        # Here is how the return dictionary should look like:
        # {
        #    "exactlyMatched": {
        #           "Default": [connectionWithExactName],
        #           "WalletOne" : [connectionWithExactName],
        #     }, "likelyMatched": {
        #           "Default": [similarMatches1, similarMatches2],
        #           "WalletOne": [similarMatches2, similarMatches3]
        #     }
        # }
        return {
            "exactlyMatched": exactMatched,
            "likelyMatched": likelyMatched
        }

    def _syncConnectionPostEndPointRetrieval(
            self,
            postSync,
            connection: Connection,
            reply,
            err,
            **kwargs):
        if err:
            self.print('    {}'.format(err))
            return True

        postSync(connection)

    def _printUsagePostSync(self, connection):
        self._printShowAndAcceptConnectionUsage(connection.name)

    def _getTargetEndpoint(self, li, postSync):
        if not self.activeWallet.identifiers:
            self.print("No key present in wallet for making request on Indy,"
                       " so adding one")
            self._newSigner(wallet=self.activeWallet)
        if self._isConnectedToAnyEnv():
            self.print("\nSynchronizing...")
            doneCallback = partial(self._syncConnectionPostEndPointRetrieval,
                                   postSync, li)
            try:
                self.agent.sync(li.name, doneCallback)
            except NotConnectedToNetwork:
                self._printCannotSyncSinceNotConnectedEnvMessage()
        else:
            if not self.activeEnv:
                self._printCannotSyncSinceNotConnectedEnvMessage()

    def _getOneConnectionForFurtherProcessing(self, connectionName):
        totalFound, exactlyMatchedConnections, likelyMatchedConnections = \
            self._get_matching_requests_detail(connectionName)

        if totalFound == 0:
            self._printNoConnectionFoundMsg()
            return None

        if totalFound > 1:
            self._printMoreThanOneConnectionFoundMsg(
                connectionName, exactlyMatchedConnections, likelyMatchedConnections)
            return None
        li = self._getOneConnection(
            exactlyMatchedConnections, likelyMatchedConnections)
        if IndyCli.isNotMatching(connectionName, li.name):
            self.print('Expanding {} to "{}"'.format(connectionName, li.name))
        return li

    def _sendAcceptInviteToTargetEndpoint(self, connection: Connection):
        self.agent.accept_request(connection)

    def _acceptConnectionPostSync(self, connection: Connection):
        if connection.isRemoteEndpointAvailable:
            self._sendAcceptInviteToTargetEndpoint(connection)
        else:
            self.print("Remote endpoint ({}) not found, "
                       "can not connect to {}\n".format(
                           connection.remoteEndPoint, connection.name))
            self.logger.debug("{} has remote endpoint {}".
                              format(connection, connection.remoteEndPoint))

    def _accept_connection_request(self, connectionName):
        li = self._getOneConnectionForFurtherProcessing(connectionName)

        if li:
            if li.isAccepted:
                self._printConnectionAlreadyExcepted(li.name)
            else:
                self.print("Request not yet verified.")
                if not li.connection_last_synced:
                    self.print("Connection not yet synchronized.")

                if self._isConnectedToAnyEnv():
                    self.print("Attempting to sync...")
                    self._getTargetEndpoint(li, self._acceptConnectionPostSync)
                else:
                    if li.isRemoteEndpointAvailable:
                        self._sendAcceptInviteToTargetEndpoint(li)
                    else:
                        self.print("Request acceptance aborted.")
                        self._printNotConnectedEnvMessage(
                            "Cannot sync because not connected")

    def _sync_connection_request(self, connectionName):
        li = self._getOneConnectionForFurtherProcessing(connectionName)
        if li:
            self._getTargetEndpoint(li, self._printUsagePostSync)

    @staticmethod
    def isNotMatching(source, target):
        return source.lower() != target.lower()

    @staticmethod
    def removeSpecialChars(name):
        return name.replace('"', '').replace("'", "") if name else None

    def _printSyncConnectionUsage(self, connectionName):
        msgs = self._getSyncConnectionUsage(connectionName)
        self.printSuggestion(msgs)

    def _printSyncAndAcceptUsage(self, connectionName):
        msgs = self._getSyncConnectionUsage(connectionName) + \
            self._getAcceptConnectionUsage(connectionName)
        self.printSuggestion(msgs)

    def _printConnectionAlreadyExcepted(self, connectionName):
        self.print(
            "Connection {} is already accepted\n".format(connectionName))

    def _printShowAndAcceptConnectionUsage(self, connectionName=None):
        msgs = self._getShowConnectionUsage(connectionName) + \
            self._getAcceptConnectionUsage(connectionName)
        self.printSuggestion(msgs)

    def _printShowAndLoadFileUsage(self):
        msgs = self._getShowFileUsage() + self._getLoadFileUsage()
        self.printUsage(msgs)

    def _printShowAndLoadFileSuggestion(self):
        msgs = self._getShowFileUsage() + self._getLoadFileUsage()
        self.printSuggestion(msgs)

    def _printNoConnectionFoundMsg(self):
        self.print("No matching connection requests found in current wallet")
        self._printShowAndLoadFileSuggestion()

    def _isConnectedToAnyEnv(self):
        return self.activeEnv and self.activeClient and \
            self.activeClient.hasSufficientConnections

    def _accept_request_connection(self, matchedVars):
        if matchedVars.get(
                'accept_connection_request') == acceptConnectionCmd.id:
            connectionName = IndyCli.removeSpecialChars(
                matchedVars.get('connection_name'))
            self._accept_connection_request(connectionName)
            return True

    def _pingTarget(self, matchedVars):
        if matchedVars.get('ping') == pingTargetCmd.id:
            connectionName = IndyCli.removeSpecialChars(
                matchedVars.get('target_name'))
            li = self._getOneConnectionForFurtherProcessing(connectionName)
            if li:
                if li.isRemoteEndpointAvailable:
                    self.agent._pingToEndpoint(li.name, li.remoteEndPoint)
                else:
                    self.print("Please sync first to get target endpoint")
                    self._printSyncConnectionUsage(li.name)
            return True

    def _syncConnection(self, matchedVars):
        if matchedVars.get('sync_connection') == syncConnectionCmd.id:
            # TODO: Shouldn't we remove single quotes too?
            connectionName = IndyCli.removeSpecialChars(
                matchedVars.get('connection_name'))
            self._sync_connection_request(connectionName)
            return True

    def _get_matching_requests_detail(self, connectionName):
        connection_requests = self._get_request_matching_connections(
            IndyCli.removeSpecialChars(connectionName))

        exactlyMatchedConnections = connection_requests["exactlyMatched"]
        likelyMatchedConnections = connection_requests["likelyMatched"]

        totalFound = sum([len(v) for v in {**exactlyMatchedConnections,
                                           **likelyMatchedConnections}.values()])
        return totalFound, exactlyMatchedConnections, likelyMatchedConnections

    @staticmethod
    def _getOneConnection(exactlyMatchedConnections,
                          likelyMatchedConnections) -> Connection:
        li = None
        if len(exactlyMatchedConnections) == 1:
            li = list(exactlyMatchedConnections.values())[0][0]
        else:
            li = list(likelyMatchedConnections.values())[0][0]
        return li

    def _printMoreThanOneConnectionFoundMsg(
            self,
            connectionName,
            exactlyMatchedConnections,
            likelyMatchedConnections):
        self.print(
            'More than one connection matches "{}"'.format(connectionName))
        exactlyMatchedConnections.update(likelyMatchedConnections)
        for k, v in exactlyMatchedConnections.items():
            for li in v:
                self.print("{}".format(li.name))
        self.print("\nRe enter the command with more specific "
                   "connection request name")
        self._printShowAndAcceptConnectionUsage()

    def _showConnection(self, matchedVars):
        if matchedVars.get('show_connection') == showConnectionCmd.id:
            connectionName = matchedVars.get(
                'connection_name').replace('"', '')

            totalFound, exactlyMatchedConnections, likelyMatchedConnections = \
                self._get_matching_requests_detail(connectionName)

            if totalFound == 0:
                self._printNoConnectionFoundMsg()
                return True

            if totalFound == 1:
                li = self._getOneConnection(
                    exactlyMatchedConnections, likelyMatchedConnections)

                if IndyCli.isNotMatching(connectionName, li.name):
                    self.print('Expanding {} to "{}"'.format(
                        connectionName, li.name))

                self.print("{}".format(str(li)))
                if li.isAccepted:
                    self._printSuggestionPostAcceptConnection(self, li)
                else:
                    self._printSyncAndAcceptUsage(li.name)
            else:
                self._printMoreThanOneConnectionFoundMsg(
                    connectionName, exactlyMatchedConnections, likelyMatchedConnections)

            return True

    # def _printNoClaimReqFoundMsg(self):
    #     self.print("No matching Claim Requests found in current wallet\n")
    #
    def _printNoProofReqFoundMsg(self):
        self.print("No matching Proof Requests found in current wallet\n")

    def _printNoClaimFoundMsg(self):
        self.print("No matching Claims found in "
                   "any connections in current wallet\n")

    def _printMoreThanOneConnectionFoundForRequest(
            self, requestedName, connectionNames):
        self.print(
            'More than one connection matches "{}"'.format(requestedName))
        for li in connectionNames:
            self.print("{}".format(li))
            # TODO: Any suggestion in more than one connection?

    # TODO: Refactor following three methods
    # as most of the pattern looks similar

    def _printRequestAlreadyMade(self, extra=""):
        msg = "Request already made."
        if extra:
            msg += "Extra info: {}".format(extra)
        self.print(msg)

    def _printMoreThanOneClaimFoundForRequest(
            self, claimName, connectionAndClaimNames):
        self.print('More than one match for "{}"'.format(claimName))
        for li, cl in connectionAndClaimNames:
            self.print("{} in {}".format(li, cl))

    def _findProofRequest(self,
                          claimReqName: str,
                          connectionName: str=None) -> (Connection,
                                                        ProofRequest):
        matchingConnectionWithClaimReq = self.activeWallet. findAllProofRequests(
            claimReqName, connectionName)  # TODO rename claimReqName -> proofRequestName

        if len(matchingConnectionWithClaimReq) == 0:
            self._printNoProofReqFoundMsg()
            return None, None

        if len(matchingConnectionWithClaimReq) > 1:
            connectionNames = [ml.name for ml,
                               cr in matchingConnectionWithClaimReq]
            self._printMoreThanOneConnectionFoundForRequest(
                claimReqName, connectionNames)
            return None, None

        return matchingConnectionWithClaimReq[0]

    def _getOneConnectionAndAvailableClaim(
            self, claimName, printMsgs: bool = True) -> (Connection, Schema):
        matchingConnectionsWithAvailableClaim = self.activeWallet. \
            getMatchingConnectionsWithAvailableClaim(claimName)

        if len(matchingConnectionsWithAvailableClaim) == 0:
            if printMsgs:
                self._printNoClaimFoundMsg()
            return None, None

        if len(matchingConnectionsWithAvailableClaim) > 1:
            connectionNames = [ml.name for ml,
                               _ in matchingConnectionsWithAvailableClaim]
            if printMsgs:
                self._printMoreThanOneConnectionFoundForRequest(
                    claimName, connectionNames)
            return None, None

        return matchingConnectionsWithAvailableClaim[0]

    async def _getOneConnectionAndReceivedClaim(self, claimName, printMsgs: bool = True) -> \
            (Connection, Tuple, Dict):
        matchingConnectionsWithRcvdClaim = await self.agent.getMatchingConnectionsWithReceivedClaimAsync(claimName)

        if len(matchingConnectionsWithRcvdClaim) == 0:
            if printMsgs:
                self._printNoClaimFoundMsg()
            return None, None, None

        if len(matchingConnectionsWithRcvdClaim) > 1:
            connectionNames = [ml.name for ml, _,
                               _ in matchingConnectionsWithRcvdClaim]
            if printMsgs:
                self._printMoreThanOneConnectionFoundForRequest(
                    claimName, connectionNames)
            return None, None, None

        return matchingConnectionsWithRcvdClaim[0]

    def _setAttr(self, matchedVars):
        if matchedVars.get('set_attr') == setAttrCmd.id:
            attrName = matchedVars.get('attr_name')
            attrValue = matchedVars.get('attr_value')
            curConnection, curProofReq, selfAttestedAttrs = self.curContext
            if curProofReq:
                selfAttestedAttrs[attrName] = attrValue
            else:
                self.print("No context, use below command to set the context")
                self.printUsage(self._getShowProofRequestUsage())
            return True

    def _reqClaim(self, matchedVars):
        if matchedVars.get('request_claim') == reqClaimCmd.id:
            claimName = IndyCli.removeSpecialChars(
                matchedVars.get('claim_name'))
            matchingConnection, ac = \
                self._getOneConnectionAndAvailableClaim(
                    claimName, printMsgs=False)
            if matchingConnection:
                name, version, origin = ac
                if IndyCli.isNotMatching(claimName, name):
                    self.print('Expanding {} to "{}"'.format(
                        claimName, name))
                self.print("Found claim {} in connection {}".
                           format(claimName, matchingConnection.name))
                if not self._isConnectedToAnyEnv():
                    self._printNotConnectedEnvMessage()
                    return True

                schemaKey = (name, version, origin)
                self.print("Requesting claim {} from {}...".format(
                    name, matchingConnection.name))

                self.agent.sendReqClaim(matchingConnection, schemaKey)
            else:
                self._printNoClaimFoundMsg()
            return True

    def _change_current_key_req(self, matchedVars):
        if matchedVars.get('change_ckey') == changeKeyCmd.id:
            if not self.canMakeIndyRequest:
                return True
            seed = matchedVars.get('seed')
            self._change_current_key(seed=seed)
            return True

    def _change_current_key(self, seed=None):
        if not self.isValidSeedForNewKey(seed):
            return True

        cur_id = self.activeWallet.requiredIdr()
        cseed = cleanSeed(seed or randombytes(32))

        dm = self.activeWallet.didMethods.get(None)
        signer = dm.newSigner(identifier=cur_id, seed=cseed)

        def change_verkey_cb(reply, error, *args, **kwargs):
            if error:
                self.print("Error: {}".format(error), Token.BoldBlue)
            else:
                self.activeWallet.updateSigner(cur_id, signer)
                self._saveActiveWallet()
                self.print("Key changed for {}".format(
                    get_payload_data(reply)[TARGET_NYM]), Token.BoldBlue)
                self.print("New verification key is {}".format(
                    signer.verkey), Token.BoldBlue)

        self._addNym(nym=cur_id, role=None, newVerKey=signer.verkey,
                     otherClientName=None, custom_clb=change_verkey_cb)

    def _createNewIdentifier(self, DID, seed,
                             alias=None):
        if not self.isValidSeedForNewKey(seed):
            return True

        if not seed:
            seed = randombytes(32)

        cseed = cleanSeed(seed)

        signer = DidSigner(identifier=DID, seed=cseed, alias=alias)

        id, signer = self.activeWallet.addIdentifier(DID,
                                                     seed=cseed, alias=alias)
        self.print("DID created in wallet {}".format(self.activeWallet))
        self.print("New DID is {}".format(signer.identifier))
        self.print("New verification key is {}".format(signer.verkey))
        self._setActiveIdentifier(id)

    def _reqAvailClaims(self, matchedVars):
        if matchedVars.get('request_avail_claims') == reqAvailClaimsCmd.id:
            connectionName = IndyCli.removeSpecialChars(
                matchedVars.get('connection_name'))
            li = self._getOneConnectionForFurtherProcessing(connectionName)
            if li:
                self.agent.sendRequestForAvailClaims(li)
            return True

    def _newDID(self, matchedVars):
        if matchedVars.get('new_id') == newDIDCmd.id:
            DID = matchedVars.get('id')
            alias = matchedVars.get('alias')

            seed = matchedVars.get('seed')
            self._createNewIdentifier(DID, seed, alias)
            return True

    def _sendProof(self, matchedVars):
        if matchedVars.get('send_proof') == sendProofCmd.id:
            proofName = IndyCli.removeSpecialChars(
                matchedVars.get('proof_name').strip())
            connectionName = IndyCli.removeSpecialChars(
                matchedVars.get('connection_name').strip())

            li, proofReq = self._findProofRequest(proofName, connectionName)

            if not li or not proofReq:
                return False

            self.logger.debug("Building proof using {} for {}".
                              format(proofReq, li))

            # if connection or proof request doesn't match with context information,
            # then set the context accordingly
            if li != self.curContext.link or \
                    proofReq != self.curContext.proofRequest:
                self.curContext = Context(li, proofReq, {})

            self.agent.sendProof(li, proofReq)

            return True

    def _sendProofRequest(self, matchedVars):
        if matchedVars.get('send_proof_request') == 'send proof-request':
            proofRequestName = IndyCli.removeSpecialChars(
                matchedVars.get('proof_request_name').strip())
            target = IndyCli.removeSpecialChars(
                matchedVars.get('target').strip())

            li = self._getOneConnectionForFurtherProcessing(target)

            if li:
                result = self.agent.sendProofReq(li, proofRequestName)
                if result != ERR_NO_PROOF_REQUEST_SCHEMA_FOUND:
                    self.print('Sent proof request "{}" to {}'
                               .format(proofRequestName, target))
                else:
                    self.print(ERR_NO_PROOF_REQUEST_SCHEMA_FOUND)
            else:
                self.print('No connection found with name {}'.format(target))

            return True

    async def _showReceivedOrAvailableClaim(self, claimName):
        matchingConnection, rcvdClaim, attributes = \
            await self._getOneConnectionAndReceivedClaim(claimName)
        if matchingConnection:
            self.print("Found claim {} in connection {}".
                       format(claimName, matchingConnection.name))

            # TODO: Figure out how to get time of issuance
            issued = None not in attributes.values()

            if issued:
                self.print("Status: {}".format(datetime.datetime.now()))
            else:
                self.print("Status: available (not yet issued)")

            self.print('Name: {}\nVersion: {}'.format(claimName, rcvdClaim[1]))
            self.print("Attributes:")
            for n, v in attributes.items():
                if v:
                    self.print('    {}: {}'.format(n, v))
                else:
                    self.print('    {}'.format(n))

            if not issued:
                self._printRequestClaimMsg(claimName)
            else:
                self.print("")
            return rcvdClaim
        else:
            self.print("No matching Claims found "
                       "in any connections in current wallet")

    def _printRequestClaimMsg(self, claimName):
        self.printSuggestion(self._getReqClaimUsage(claimName))

    @staticmethod
    def _formatProofRequestAttribute(attributes, verifiableAttributes,
                                     matchingConnectionAndReceivedClaim):
        getClaim = itemgetter(2)

        def containsAttr(key):
            return lambda t: key in getClaim(t)

        formatted = 'Attributes:\n'

        for k, v in attributes.items():
            # determine if we need to show number for claims which
            # were participated in proof generation
            attrClaimIndex = getIndex(containsAttr(
                k), matchingConnectionAndReceivedClaim)
            showClaimNumber = attrClaimIndex > -1 and \
                len(matchingConnectionAndReceivedClaim) > 1

            formatted += ('    ' +
                          ('[{}] '.format(attrClaimIndex + 1)
                           if showClaimNumber else '') +
                          str(k) +
                          (' (V)' if k in verifiableAttributes else '') +
                          ': ' + str(v) + '\n')

        return formatted

    @staticmethod
    def _printClaimsUsedInProofConstruction(
            filteredMatchingClaims, proofRequestAttrs):
        toPrint = '\nThe Proof is constructed from the following claims:\n'
        showClaimNumber = len(filteredMatchingClaims) > 1
        claimNumber = 1
        alreadyFulfilledAttrs = {}

        for li, (name, ver, _), issuedAttrs in filteredMatchingClaims:
            toPrint += '\n    Claim {}({} v{} from {})\n'.format(
                '[{}] '.format(claimNumber) if showClaimNumber else '',
                name, ver, li.name
            )
            for k, v in issuedAttrs.items():
                toPrint += ('        {}'.format(
                    '* ' if k in proofRequestAttrs and
                            k not in alreadyFulfilledAttrs else '  ') +
                            k + ': ' +
                            '{}\n'.format('None' if v is None else v)
                            )
                if k not in alreadyFulfilledAttrs:
                    alreadyFulfilledAttrs[k] = True

            claimNumber += 1

        return toPrint

    async def _fulfillProofRequestByContext(self, c: Context):
        matchingConnectionAndReceivedClaim = await self.agent.getClaimsUsedForAttrs(
            c.proofRequest.attributes)

        # filter all those claims who has some None value
        # since they are not yet requested
        filteredMatchingClaims = []
        for li, cl, issuedAttrs in matchingConnectionAndReceivedClaim:
            if None not in [v for k, v in issuedAttrs.items()]:
                filteredMatchingClaims.append((li, cl, issuedAttrs))

        attributesWithValue = c.proofRequest.attributes
        c.proofRequest.selfAttestedAttrs = {}
        for k, v in c.proofRequest.attributes.items():
            for li, cl, issuedAttrs in filteredMatchingClaims:
                if k in issuedAttrs:
                    attributesWithValue[k] = issuedAttrs[k]
                else:
                    defaultValue = attributesWithValue[k] or v
                    selfAttestedValue = c.selfAttestedAttrs.get(k)
                    if selfAttestedValue:
                        attributesWithValue[k] = selfAttestedValue
                        c.proofRequest.selfAttestedAttrs[k] = selfAttestedValue
                    else:
                        attributesWithValue[k] = defaultValue

        c.proofRequest.attributes = attributesWithValue
        c.proofRequest.fulfilledByClaims = filteredMatchingClaims
        return True

    async def fulfillProofRequest(self, proofReqName):
        proof_req_name = IndyCli.removeSpecialChars(proofReqName)
        matchingConnection, proofRequest = self._findProofRequest(
            proof_req_name)

        if matchingConnection and proofRequest:
            if matchingConnection != self.curContext.link or \
                    proofRequest != self.curContext.proofRequest:
                self.curContext = Context(matchingConnection, proofRequest, {})
            self.print('Found proof request "{}" in connection "{}"'.
                       format(proofRequest.name, matchingConnection.name))

            return await self._fulfillProofRequestByContext(self.curContext)
        else:
            return False

    async def _showProofWithMatchingClaims(self, c: Context):
        self.print(
            c.proofRequest.fixedInfo +
            self._formatProofRequestAttribute(
                c.proofRequest.attributes,
                [
                    v.name for k,
                    v in c.proofRequest.verifiableAttributes.items()],
                c.proofRequest.fulfilledByClaims))

        self.print(self._printClaimsUsedInProofConstruction(
            c.proofRequest.fulfilledByClaims, c.proofRequest.attributes))

        self.printSuggestion(
            self._getSetAttrUsage() +
            self._getSendProofUsage(c.proofRequest, c.link))

    async def _fulfillAndShowConstructedProof(self, proof_request_name):
        fulfilled = await self.fulfillProofRequest(proof_request_name)
        if fulfilled:
            await self._showProofWithMatchingClaims(self.curContext)

    def _showProofRequest(self, matchedVars):
        if matchedVars.get('show_proof_request') == showProofRequestCmd.id:
            proof_request_name = IndyCli.removeSpecialChars(
                matchedVars.get('proof_request_name'))

            self.agent.loop.call_soon(asyncio.ensure_future,
                                      self._fulfillAndShowConstructedProof(
                                          proof_request_name))
            return True

    def _showClaim(self, matchedVars):
        if matchedVars.get('show_claim') == showClaimCmd.id:
            claimName = IndyCli.removeSpecialChars(
                matchedVars.get('claim_name'))
            self.agent.loop.call_soon(
                asyncio.ensure_future,
                self._showReceivedOrAvailableClaim(claimName))

            return True

    def _listClaims(self, matchedVars):
        if matchedVars.get('list_claims') == listClaimsCmd.id:
            connection_name = IndyCli.removeSpecialChars(
                matchedVars.get('connection_name'))

            li = self._getOneConnectionForFurtherProcessing(connection_name)
            if li:
                # TODO sync if needed, send msg to agent
                self._printAvailClaims(li)
            return True

    def _listConnections(self, matchedVars):
        if matchedVars.get('list_connections') == listConnectionsCmd.id:
            connections = self.activeWallet.getConnectionNames()
            if len(connections) == 0:
                self.print("No connections exists")
            else:
                for connection in connections:
                    self.print(connection + "\n")
            return True

    def _printAvailClaims(self, connection):
        self.print(connection.avail_claims_str())

    def _showFile(self, matchedVars):
        if matchedVars.get('show_file') == showFileCmd.id:
            givenFilePath = matchedVars.get('file_path')
            filePath = IndyCli._getFilePath(givenFilePath)
            if not filePath:
                self.print("Given file does not exist")
                self.printUsage(self._getShowFileUsage())
            else:
                with open(filePath, 'r') as fin:
                    self.print(fin.read())
                msgs = self._getLoadFileUsage(givenFilePath)
                self.printSuggestion(msgs)
            return True

    def canConnectToEnv(self, envName: str):
        if envName == self.activeEnv:
            return "Already connected to {}".format(envName)
        if envName not in self.envs:
            return "Unknown environment {}".format(envName)

        new_base_path = os.path.join(self.ledger_base_dir, envName)

        if not os.path.exists(os.path.join(new_base_path,
                              genesis_txn_file(self.config.poolTransactionsFile))):
            return "Do not have information to connect to {}".format(envName)

    def _disconnect(self, matchedVars):
        if matchedVars.get('disconn') == disconnectCmd.id:
            self._disconnectFromCurrentEnv()
            return True

    def _disconnectFromCurrentEnv(self, toConnectToNewEnv=None):
        oldEnv = self.activeEnv
        if not oldEnv and not toConnectToNewEnv:
            self.print("Not connected to any environment.")
            return True

        if not toConnectToNewEnv:
            self.print("Disconnecting from {} ...".format(self.activeEnv))

        self._saveActiveWallet()
        self._wallets = {}
        self._activeWallet = None
        self._activeClient = None
        self.activeEnv = None
        self._setPrompt(self.currPromptText.replace("{}{}".format(
            PROMPT_ENV_SEPARATOR, oldEnv), ""))

        if not toConnectToNewEnv:
            self.print("Disconnected from {}".format(oldEnv), Token.BoldGreen)

        if toConnectToNewEnv is None:
            self.restoreLastActiveWallet()

    def printWarningIfActiveWalletIsIncompatible(self):
        if self._activeWallet:
            if not self.checkIfWalletBelongsToCurrentContext(
                    self._activeWallet):
                self.print(self.getWalletContextMistmatchMsg, Token.BoldOrange)
                self.print("Any changes made to this wallet won't "
                           "be persisted.", Token.BoldOrange)

    def moveActiveWalletToNewContext(self, newEnv):
        if self._activeWallet:
            if not self._activeWallet.env or self._activeWallet.env == NO_ENV:
                currentWalletName = self._activeWallet.name
                self._activeWallet.env = newEnv
                randomSuffix = ''
                sourceWalletFilePath = getWalletFilePath(
                    self.getContextBasedWalletsBaseDir(), self.walletFileName)
                targetContextDir = os.path.join(self.getWalletsBaseDir(),
                                                newEnv)
                if os.path.exists(sourceWalletFilePath):
                    while True:
                        targetWalletName = currentWalletName + randomSuffix
                        toBeTargetWalletFileExists = self.checkIfPersistentWalletExists(
                            targetWalletName, inContextDir=targetContextDir)
                        if not toBeTargetWalletFileExists:
                            self._activeWallet.name = targetWalletName
                            break
                        randomSuffix = "-{}".format(randomString(6))
                    self._saveActiveWalletInDir(contextDir=targetContextDir,
                                                printMsgs=False)
                    os.remove(sourceWalletFilePath)
                targetWalletFilePath = getWalletFilePath(
                    targetContextDir, self.walletFileName)

                self.print("Current active wallet got moved to '{}' "
                           "environment. Here is the detail:".format(newEnv),
                           Token.BoldBlue)
                self.print("    wallet name: {}".format(
                    currentWalletName), Token.BoldBlue)
                self.print("    old location: {}".format(
                    sourceWalletFilePath), Token.BoldBlue)
                self.print("    new location: {}".format(
                    targetWalletFilePath), Token.BoldBlue)
                if randomSuffix != '':
                    self.print("    new wallet name: {}".format(
                        self._activeWallet.name), Token.BoldBlue)
                    self.print("    Note:\n       Target environment "
                               "already had a wallet with name '{}', so we "
                               "renamed current active wallet to '{}'.\n      "
                               " You can always rename any wallet with more "
                               "meaningful name with 'rename wallet' command.".
                               format(currentWalletName,
                                      self._activeWallet.name),
                               Token.BoldBlue)
                self._activeWallet = None

    def _connectTo(self, matchedVars):
        if matchedVars.get('conn') == connectToCmd.id:
            envName = matchedVars.get('env_name')
            envError = self.canConnectToEnv(envName)

            if envError:
                self.print(envError, token=Token.Error)
                self._printConnectUsage()
                return False

            oldEnv = self.activeEnv

            self._saveActiveWallet()

            if not oldEnv:
                self.moveActiveWalletToNewContext(envName)

            isAnyWalletExistsForNewEnv = \
                self.isAnyWalletFileExistsForGivenEnv(envName)

            if oldEnv or isAnyWalletExistsForNewEnv:
                self._disconnectFromCurrentEnv(envName)

            # Prompt has to be changed, so it show the environment too
            self.activeEnv = envName
            self._setPrompt(self.currPromptText.replace("{}{}".format(
                PROMPT_ENV_SEPARATOR, oldEnv), ""))

            if isAnyWalletExistsForNewEnv:
                self.restoreLastActiveWallet()

            self.printWarningIfActiveWalletIsIncompatible()

            self._buildClientIfNotExists(self.config)
            self.print("Connecting to {}...".format(
                envName), Token.BoldGreen)

            self.ensureClientConnected()

            if not self.activeClient or not self.activeClient.nodeReg:
                msg = '\nThe information required to connect this client to the nodes cannot be found. ' \
                      '\nThis is an error. To correct the error, get the file containing genesis transactions ' \
                      '\n(the file name is `{}`) from the github repository and place ' \
                      '\nit in directory `{}`.\n' \
                      '\nThe github url is {}.\n'.format(genesis_txn_file(self.config.poolTransactionsFile),
                                                         self.ledger_base_dir,
                                                         self.githubUrl)
                self.print(msg)
                return False

            return True

    @property
    def getActiveEnv(self):
        prompt, env = PlenumCli.getPromptAndEnv(self.name,
                                                self.currPromptText)
        return env

    def get_available_networks(self):
        return [check_dir for check_dir in os.listdir(self.ledger_base_dir)
                if os.path.isdir(
                    os.path.join(self.ledger_base_dir, check_dir))]

    def getAllSubDirNamesForKeyrings(self):
        lst = self.get_available_networks()
        lst.append(NO_ENV)
        return lst

    def updateEnvNameInWallet(self):
        if not self._activeWallet.getEnvName:
            self._activeWallet.env = self.activeEnv if self.activeEnv \
                else NO_ENV

    def getStatus(self):
        # TODO: This needs to show active wallet and active DID
        if not self.activeEnv:
            self._printNotConnectedEnvMessage()
        else:
            if self.activeClient.hasSufficientConnections:
                msg = "Connected to {} Indy network".format(self.activeEnv)
            else:
                msg = "Attempting connection to {} Indy network". \
                    format(self.activeEnv)
            self.print(msg)

    def _setPrompt(self, promptText):
        if self.activeEnv:
            if not promptText.endswith("{}{}".format(PROMPT_ENV_SEPARATOR,
                                                     self.activeEnv)):
                promptText = "{}{}{}".format(promptText, PROMPT_ENV_SEPARATOR,
                                             self.activeEnv)

        super()._setPrompt(promptText)

    def _addGenTxnAction(self, matchedVars):
        if matchedVars.get('add_genesis'):
            nym = matchedVars.get('dest_id')
            role = Identity.correctRole(self._getRole(matchedVars))
            if role:
                role = role.upper()
            txn = Member.nym_txn(nym=nym,
                                 role=role,
                                 txn_id=sha256(randomString(6).encode()).hexdigest())
            # TODO: need to check if this needs to persist as well
            self.genesisTransactions.append(txn)
            self.print('Genesis transaction added.')
            return True

    @staticmethod
    def bootstrapClientKey(client, node, identifier=None):
        pass

    def ensureClientConnected(self):
        if self._isConnectedToAnyEnv():
            self.print("Connected to {}.".format(
                self.activeEnv), Token.BoldBlue)
        else:
            self.looper.loop.call_later(.2, self.ensureClientConnected)

    def ensureAgentConnected(self, otherAgentHa, clbk: Callable = None,
                             *args):
        if not self.agent:
            return
        if self.agent.endpoint.isConnectedTo(ha=otherAgentHa):
            # TODO: Remove this print
            self.logger.debug("Agent {} connected to {}".
                              format(self.agent, otherAgentHa))
            if clbk:
                clbk(*args)
        else:
            self.looper.loop.call_later(.2, self.ensureAgentConnected,
                                        otherAgentHa, clbk, *args)

    def _ensureReqCompleted(self, reqKey, client, clbk=None, pargs=None,
                            kwargs=None, cond=None):
        ensureReqCompleted(self.looper.loop, reqKey, client, clbk, pargs=pargs,
                           kwargs=kwargs, cond=cond)

    def addAlias(self, reply, err, client, alias, signer):
        if not self.canMakeIndyRequest:
            return True

        txnId = reply[TXN_ID]
        op = {
            TARGET_NYM: alias,
            TXN_TYPE: NYM,
            # TODO: Should REFERENCE be symmetrically encrypted and the key
            # should then be disclosed in another transaction
            REF: txnId
        }
        self.print("Adding alias {}".format(alias), Token.BoldBlue)
        self.aliases[alias] = signer
        client.submit(op, identifier=self.activeSigner.identifier)

    def print(self, msg, token=None, newline=True):
        super().print(msg, token=token, newline=newline)

    def createFunctionMappings(self):
        from collections import defaultdict

        def promptHelper():
            self.print("Changes the prompt to provided principal name")
            self.printUsage(self._getPromptUsage())

        def principalsHelper():
            self.print("A person like Alice, "
                       "an organization like Faber College, "
                       "or an IoT-style thing")

        def loadHelper():
            self.print("Creates the connection, generates DID and signing keys")
            self.printUsage(self._getLoadFileUsage("<request filename>"))

        def showHelper():
            self.print("Shows the info about the connection")
            self.printUsage(self._getShowFileUsage("<request filename>"))

        def showConnectionHelper():
            self.print(
                "Shows connection info in case of one matching connection, "
                "otherwise shows all the matching connections")
            self.printUsage(self._getShowConnectionUsage())

        def connectHelper():
            self.print("Lets you connect to the respective environment")
            self.printUsage(self._getConnectUsage())

        def syncHelper():
            self.print("Synchronizes the connection between the endpoints")
            self.printUsage(self._getSyncConnectionUsage())

        def defaultHelper():
            self.printHelp()

        mappings = {
            'show': showHelper,
            'prompt': promptHelper,
            'principals': principalsHelper,
            'load': loadHelper,
            'show connection': showConnectionHelper,
            'connect': connectHelper,
            'sync': syncHelper
        }

        return defaultdict(lambda: defaultHelper, **mappings)

    def getTopComdMappingKeysForHelp(self):
        return ['helpAction', 'connectTo', 'disconnect', 'statusAction']

    def getHelpCmdIdsToShowUsage(self):
        return ["help", "connect"]

    def cmdHandlerToCmdMappings(self):
        # The 'key' of 'mappings' dictionary is action handler function name
        # without leading underscore sign. Each such funcation name should be
        # mapped here, its other thing that if you don't want to display it
        # in help, map it to None, but mapping should be present, that way it
        # will force developer to either write help message for those cli
        # commands or make a decision to not show it in help message.

        mappings = OrderedDict()
        mappings.update(super().cmdHandlerToCmdMappings())
        mappings['connectTo'] = connectToCmd
        mappings['disconnect'] = disconnectCmd
        mappings['addGenTxnAction'] = addGenesisTxnCmd
        mappings['newDID'] = newDIDCmd
        mappings['sendNymAction'] = sendNymCmd
        mappings['sendGetNymAction'] = sendGetNymCmd
        mappings['sendAttribAction'] = sendAttribCmd
        mappings['sendGetAttrAction'] = sendGetAttrCmd
        mappings['sendNodeAction'] = sendNodeCmd
        mappings['sendPoolUpgAction'] = sendPoolUpgCmd
        mappings['sendPoolConfigAction'] = sendPoolConfigCmd
        mappings['sendSchemaAction'] = sendSchemaCmd
        mappings['sendGetSchemaAction'] = sendGetSchemaCmd
        mappings['sendClaimDefAction'] = sendClaimDefCmd
        mappings['sendGetClaimDefAction'] = sendGetClaimDefCmd
        mappings['showFile'] = showFileCmd
        mappings['loadFile'] = loadFileCmd
        mappings['showConnection'] = showConnectionCmd
        mappings['syncConnection'] = syncConnectionCmd
        mappings['pingTarget'] = pingTargetCmd
        mappings['acceptrequestconnection'] = acceptConnectionCmd
        mappings['showClaim'] = showClaimCmd
        mappings['listClaims'] = listClaimsCmd
        mappings['listConnections'] = listConnectionsCmd
        mappings['reqClaim'] = reqClaimCmd
        mappings['showProofRequest'] = showProofRequestCmd
        mappings['addGenTxnAction'] = addGenesisTxnCmd
        mappings['setAttr'] = setAttrCmd
        mappings['sendProofRequest'] = sendProofRequestCmd
        mappings['sendProof'] = sendProofCmd
        mappings['reqAvailClaims'] = reqAvailClaimsCmd
        mappings['changecurrentkeyreq'] = changeKeyCmd

        # TODO: These seems to be obsolete, so either we need to remove these
        # command handlers or let it point to None
        mappings['addGenesisAction'] = None  # overriden by addGenTxnAction

        return mappings

    @property
    def canMakeIndyRequest(self):
        if not self.hasAnyKey:
            return False
        if not self.activeEnv:
            self._printNotConnectedEnvMessage()
            return False
        if not self.checkIfWalletBelongsToCurrentContext(self._activeWallet):
            self.print(self.getWalletContextMistmatchMsg, Token.BoldOrange)
            return False

        return True

    def getConfig(self, homeDir=None):
        return getConfig(homeDir)


class DummyClient:
    def submitReqs(self, *reqs):
        pass

    @property
    def hasSufficientConnections(self):
        pass
