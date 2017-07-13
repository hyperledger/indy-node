import ast
import datetime
from collections import OrderedDict

import importlib
import json
import os
from functools import partial
from hashlib import sha256
from operator import itemgetter
from typing import Dict, Any, Tuple, Callable, NamedTuple

import asyncio

import base58
from libnacl import randombytes
from plenum.cli.cli import Cli as PlenumCli
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.layout.lexers import SimpleLexer
from pygments.token import Token

from anoncreds.protocol.globals import KEYS
from anoncreds.protocol.types import Schema, ID, ProofRequest
from plenum.cli.constants import PROMPT_ENV_SEPARATOR, NO_ENV
from plenum.cli.helper import getClientGrams
from plenum.cli.phrase_word_completer import PhraseWordCompleter
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import NAME, VERSION, TYPE, VERKEY, DATA, TXN_ID, FORCE
from plenum.common.txn_util import createGenesisTxnFile
from plenum.common.types import f
from plenum.common.util import randomString, getWalletFilePath

from sovrin_client.agent.walleted_agent import WalletedAgent
from sovrin_client.agent.constants import EVENT_NOTIFY_MSG, EVENT_POST_ACCEPT_INVITE, \
    EVENT_NOT_CONNECTED_TO_ANY_ENV
from sovrin_client.agent.msg_constants import ERR_NO_PROOF_REQUEST_SCHEMA_FOUND
from sovrin_client.cli.command import acceptLinkCmd, connectToCmd, \
    disconnectCmd, loadFileCmd, newIdentifierCmd, pingTargetCmd, reqClaimCmd, \
    sendAttribCmd, sendProofCmd, sendGetNymCmd, sendClaimDefCmd, sendNodeCmd, \
    sendGetAttrCmd, sendGetSchemaCmd, sendGetClaimDefCmd, \
    sendNymCmd, sendPoolUpgCmd, sendSchemaCmd, setAttrCmd, showClaimCmd, \
    listClaimsCmd, showFileCmd, showLinkCmd, syncLinkCmd, addGenesisTxnCmd, \
    sendProofRequestCmd, showProofRequestCmd, reqAvailClaimsCmd, listLinksCmd

from sovrin_client.cli.helper import getNewClientGrams, \
    USAGE_TEXT, NEXT_COMMANDS_TO_TRY_TEXT
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.client.wallet.link import Link
from sovrin_client.client.wallet.node import Node
from sovrin_client.client.wallet.upgrade import Upgrade
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.auth import Authoriser
from sovrin_common.config import ENVS
from sovrin_common.config_util import getConfig
from sovrin_common.exceptions import InvalidLinkException, LinkAlreadyExists, \
    LinkNotFound, NotConnectedToNetwork, SchemaNotFound
from sovrin_common.identity import Identity
from sovrin_common.constants import TARGET_NYM, ROLE, TXN_TYPE, NYM, REF, \
    ACTION, SHA256, TIMEOUT, SCHEDULE, GET_SCHEMA, \
    START, JUSTIFICATION, NULL

from stp_core.crypto.signer import Signer
from stp_core.crypto.util import cleanSeed
from stp_core.network.port_dispenser import genHa
from sovrin_common.roles import Roles
from sovrin_common.txn_util import getTxnOrderedFields
from sovrin_common.util import ensureReqCompleted, getIndex
from sovrin_node.__metadata__ import __version__

try:
    nodeMod = importlib.import_module('sovrin_node.server.node')
    nodeClass = nodeMod.Node
except ImportError:
    nodeClass = None

"""
Objective
The plenum cli bootstraps client keys by just adding them to the nodes.
Sovrin needs the client nyms to be added as transactions first.
I'm thinking maybe the cli needs to support something like this:
new node all
<each node reports genesis transactions>
new client steward with identifier <nym> (nym matches the genesis transactions)
client steward add bob (cli creates a signer and an ADDNYM for that signer's
cryptonym, and then an alias for bobto that cryptonym.)
new client bob (cli uses the signer previously stored for this client)
"""

Context = NamedTuple("Context", [("link", Link),
                                 ("proofRequest", Any),
                                 ("selfAttestedAttrs", Any)])


class SovrinCli(PlenumCli):
    name = 'sovrin'
    properName = 'Sovrin'
    fullName = 'Sovrin Identity platform'
    githubUrl = 'https://github.com/sovrin-foundation/sovrin-common/tree/stable/data'

    NodeClass = nodeClass
    ClientClass = Client
    _genesisTransactions = []

    override_file_path = None

    def __init__(self, *args, **kwargs):
        self.aliases = {}  # type: Dict[str, Signer]
        self.trustAnchors = set()
        self.users = set()
        self._agent = None
        super().__init__(*args, **kwargs)
        # Available environments
        self.envs = self.config.ENVS
        # This specifies which environment the cli is connected to test or live
        self.activeEnv = None

        # TODO bad code smell
        self.curContext = Context(None, None, {})  # type: Context

    @staticmethod
    def getCliVersion():
        return __version__

    @property
    def lexers(self):
        lexerNames = [
            'send_nym',
            'send_get_nym',
            'send_attrib',
            'send_schema',
            'send_claim_def',
            'send_node',
            'send_pool_upg',
            'add_genesis',
            'show_file',
            'conn',
            'disconn',
            'load_file',
            'show_link',
            'sync_link',
            'ping_target'
            'show_claim',
            'list_claims',
            'list_links',
            # 'show_claim_req',
            'show_proof_req',
            'req_claim',
            'accept_link_invite',
            'set_attr',
            'send_proof_request'
            'send_proof',
            'new_id',
            'req_avail_claims'
        ]
        lexers = {n: SimpleLexer(Token.Keyword) for n in lexerNames}
        # Add more lexers to base class lexers
        return {**super().lexers, **lexers}

    @property
    def completers(self):
        completers = {}
        completers["nym"] = WordCompleter([])
        completers["role"] = WordCompleter([Roles.TRUST_ANCHOR.name, Roles.STEWARD.name])
        completers["send_nym"] = PhraseWordCompleter(sendNymCmd.id)
        completers["send_get_nym"] = PhraseWordCompleter(sendGetNymCmd.id)
        completers["send_attrib"] = PhraseWordCompleter(sendAttribCmd.id)
        completers["send_schema"] = PhraseWordCompleter(sendSchemaCmd.id)
        completers["send_claim_def"] = PhraseWordCompleter(sendClaimDefCmd.id)
        completers["send_node"] = PhraseWordCompleter(sendNodeCmd.id)
        completers["send_pool_upg"] = PhraseWordCompleter(sendPoolUpgCmd.id)
        completers["add_genesis"] = PhraseWordCompleter(
            addGenesisTxnCmd.id)
        completers["show_file"] = WordCompleter([showFileCmd.id])
        completers["load_file"] = WordCompleter([loadFileCmd.id])
        completers["show_link"] = PhraseWordCompleter(showLinkCmd.id)
        completers["conn"] = WordCompleter([connectToCmd.id])
        completers["disconn"] = WordCompleter([disconnectCmd.id])
        completers["env_name"] = WordCompleter(list(self.config.ENVS.keys()))
        completers["sync_link"] = WordCompleter([syncLinkCmd.id])
        completers["ping_target"] = WordCompleter([pingTargetCmd.id])
        completers["show_claim"] = PhraseWordCompleter(showClaimCmd.id)
        completers["req_claim"] = PhraseWordCompleter(reqClaimCmd.id)
        completers["accept_link_invite"] = PhraseWordCompleter(acceptLinkCmd.id)
        completers["set_attr"] = WordCompleter([setAttrCmd.id])
        completers["new_id"] = PhraseWordCompleter(newIdentifierCmd.id)
        completers["list_claims"] = PhraseWordCompleter(listClaimsCmd.id)
        completers["list_links"] = PhraseWordCompleter(listLinksCmd.id)
        completers["show_proof_req"] = PhraseWordCompleter(
            showProofRequestCmd.id)
        completers["send_proof_request"] = PhraseWordCompleter(
            sendProofRequestCmd.id)
        completers["send_proof"] = PhraseWordCompleter(sendProofCmd.id)
        completers["req_avail_claims"] = PhraseWordCompleter(reqAvailClaimsCmd.id)

        return {**super().completers, **completers}

    def initializeGrammar(self):
        self.clientGrams = getClientGrams() + getNewClientGrams()
        super().initializeGrammar()

    @property
    def actions(self):
        actions = super().actions
        # Add more actions to base class for sovrin CLI
        if not self._sendNymAction in actions:
            actions.extend([self._sendNymAction,
                            self._sendGetNymAction,
                            self._sendAttribAction,
                            self._sendGetAttrAction,
                            self._sendNodeAction,
                            self._sendPoolUpgAction,
                            self._sendSchemaAction,
                            self._sendGetSchemaAction,
                            self._sendClaimDefAction,
                            self._sendGetClaimDefAction,
                            self._addGenTxnAction,
                            self._showFile,
                            self._loadFile,
                            self._showLink,
                            self._connectTo,
                            self._disconnect,
                            self._syncLink,
                            self._pingTarget,
                            self._showClaim,
                            self._listClaims,
                            self._listLinks,
                            self._reqClaim,
                            self._showProofRequest,
                            self._acceptInvitationLink,
                            self._setAttr,
                            self._sendProofRequest,
                            self._sendProof,
                            self._newIdentifier,
                            self._reqAvailClaims
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
                           inviter: Link=None):
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
    def _getShowLinkUsage(linkName=None):
        return ['{} "{}"'.format(
            showLinkCmd.id,
            linkName or "<link-name>")]

    @staticmethod
    def _getSyncLinkUsage(linkName=None):
        return ['{} "{}"'.format(
            syncLinkCmd.id,
            linkName or "<link-name>")]

    @staticmethod
    def _getAcceptLinkUsage(linkName=None):
        return ['{} "{}"'.format(
            acceptLinkCmd.id,
            linkName or "<link-name>")]

    @staticmethod
    def _getPromptUsage():
        return ["prompt <principal name>"]

    @property
    def allEnvNames(self):
        return "|".join(sorted(self.envs.keys(), reverse=True))

    def _getConnectUsage(self):
        return ["{} <{}>".format(
            connectToCmd.id,
            self.allEnvNames)]

    def _printMsg(self, notifier, msg):
        self.print(msg)

    def _printSuggestionPostAcceptLink(self, notifier,
                                       link: Link):
        suggestions = []
        if len(link.availableClaims) > 0:
            claimName = "|".join([n.name for n in link.availableClaims])
            claimName = claimName or "<claim-name>"
            suggestions += self._getShowClaimUsage(claimName)
            suggestions += self._getReqClaimUsage(claimName)
        if len(link.proofRequests) > 0:
            for pr in link.proofRequests:
                suggestions += self._getShowProofRequestUsage(pr)
                suggestions += self._getSendProofUsage(pr, link)
        if suggestions:
            self.printSuggestion(suggestions)
        else:
            self.print("")

    def sendToAgent(self, msg: Any, link: Link):
        if not self.agent:
            return

        endpoint = link.remoteEndPoint
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
                                     prefix="Not connected to Sovrin network"):

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
                                    self._printSuggestionPostAcceptLink)
        agent.registerEventListener(EVENT_NOT_CONNECTED_TO_ANY_ENV,
                                    self._handleNotConnectedToAnyEnv)

    def deregisterAgentListeners(self, agent):
        agent.deregisterEventListener(EVENT_NOTIFY_MSG, self._printMsg)
        agent.deregisterEventListener(EVENT_POST_ACCEPT_INVITE,
                                    self._printSuggestionPostAcceptLink)
        agent.deregisterEventListener(EVENT_NOT_CONNECTED_TO_ANY_ENV,
                                    self._handleNotConnectedToAnyEnv)

    @property
    def agent(self) -> WalletedAgent:
        if self._agent is None:
            _, port = genHa()
            agent = WalletedAgent(name=randomString(6),
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
                    data=json.loads(reply[DATA])
                    if data:
                        idr = base58.b58decode(nym)
                        if data.get(VERKEY) is None:
                            if len(idr) == 32:
                                self.print(
                                    "Current verkey is same as identifier {}"
                                        .format(nym), Token.BoldBlue)
                            else:
                                self.print(
                                    "No verkey ever assigned to the identifier {}".
                                    format(nym), Token.BoldBlue)
                            return
                        if data.get(VERKEY) == '':
                            self.print("No active verkey found for the identifier {}".
                                       format(nym), Token.BoldBlue)
                        else:
                            self.print("Current verkey for NYM {} is {}".
                                       format(nym, data[VERKEY]), Token.BoldBlue)
                else:
                    self.print("NYM {} not found".format(nym), Token.BoldBlue)
            except BaseException as e:
                self.print("Error during fetching verkey: {}".format(e),
                           Token.BoldOrange)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, getNymReply)

    def _addNym(self, nym, role, newVerKey=None, otherClientName=None):
        idy = Identity(nym, verkey=newVerKey, role=role)
        try:
            self.activeWallet.addTrustAnchoredIdentity(idy)
        except Exception as e:
            if e.args[0] == 'identifier already added':
                pass
            else:
                raise e
        reqs = self.activeWallet.preparePending()
        req, = self.activeClient.submitReqs(*reqs)
        printStr = "Adding nym {}".format(nym)

        if otherClientName:
            printStr = printStr + " for " + otherClientName
        self.print(printStr)

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Error: {}".format(error), Token.BoldBlue)
            else:
                self.print("Nym {} added".format(reply[TARGET_NYM]),
                           Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, out)
        return True

    def _addAttribToNym(self, nym, raw, enc, hsh):
        attrib = self.activeWallet.build_attrib(nym, raw, enc, hsh)
        # TODO: What is the purpose of this?
        # if nym != self.activeWallet.defaultId:
        #     attrib.dest = nym

        self.activeWallet.addAttribute(attrib)
        reqs = self.activeWallet.preparePending()
        req, = self.activeClient.submitReqs(*reqs)
        self.print("Adding attributes {} for {}".format(attrib.value, nym))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Error: {}".format(error), Token.BoldOrange)
            else:
                self.print("Attribute added for nym {}".
                           format(reply[TARGET_NYM]), Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, out)

    def _getAttr(self, nym, raw, enc, hsh):
        assert int(bool(raw)) + int(bool(enc)) + int(bool(hsh)) == 1
        if raw:
            l = LedgerStore.RAW
            data = raw
        elif enc:
            l = LedgerStore.ENC
            data = enc
        elif hsh:
            l = LedgerStore.HASH
            data = hsh
        else:
            raise RuntimeError('One of raw, enc, or hash are required.')

        attrib = Attribute(data, dest=nym, ledgerStore=l)
        req = self.activeWallet.requestAttribute(attrib, sender=self.activeWallet.defaultId)
        self.activeClient.submitReqs(req)
        self.print("Getting attr {}".format(nym))

        def getAttrReply(reply, err, *args):
            if reply and reply[DATA]:
                data=json.loads(reply[DATA])
                if data:
                    self.print(
                    "Found attribute {}"
                    .format(json.dumps(data)))
            else:
                self.print("Attr not found")

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, getAttrReply)

    def _getSchema(self, nym, name, version):
        req = self.activeWallet.requestSchema(nym,name,version,sender=self.activeWallet.defaultId)
        self.activeClient.submitReqs(req)
        self.print("Getting schema {}".format(nym))

        def getSchema(reply, err, *args):
            try:
                if reply and reply[DATA]:
                    self.print(
                        "Found schema {}"
                        .format(reply[DATA]))
                else:
                    self.print("Schema not found")
            except:
                self.print('"data" must be in proper format', Token.Error)


        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, getSchema)

    def _getClaimDef(self, seqNo, signature):
        req = self.activeWallet.requestClaimDef(seqNo, signature, sender=self.activeWallet.defaultId)
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
            except:
                self.print('"data" must be in proper format', Token.Error)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, getClaimDef)

    def _sendNodeTxn(self, nym, data):
        node = Node(nym, data, self.activeIdentifier)
        self.activeWallet.addNode(node)
        reqs = self.activeWallet.preparePending()
        req, = self.activeClient.submitReqs(*reqs)
        self.print("Sending node request for node identifier {} by {} "
                   "(request id: {})".format(nym, self.activeIdentifier,
                                             req.reqId))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print("Node request failed with error: {}".format(error), Token.BoldOrange)
            else:
                self.print("Node request completed {}".format(reply[TARGET_NYM]),
                           Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, out)

    def _sendPoolUpgTxn(self, name, version, action, sha256, schedule=None,
                        justification=None, timeout=None, force=False):
        upgrade = Upgrade(name, version, action, sha256, schedule=schedule,
                          trustee=self.activeIdentifier, timeout=timeout,
                          justification=justification, force=force)
        self.activeWallet.doPoolUpgrade(upgrade)
        reqs = self.activeWallet.preparePending()
        req, = self.activeClient.submitReqs(*reqs)
        self.print("Sending pool upgrade {} for version {}".
                   format(name, version))

        def out(reply, error, *args, **kwargs):
            if error:
                self.print(
                    "Pool upgrade failed: {}".format(error),
                    Token.BoldOrange)
            else:
                self.print("Pool upgrade successful", Token.BoldBlue)

        self.looper.loop.call_later(.2, self._ensureReqCompleted,
                                    req.key, self.activeClient, out)

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
            if not self.canMakeSovrinRequest:
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
            if not self.canMakeSovrinRequest:
                return True
            destId = matchedVars.get('dest_id')
            self._getNym(destId)
            return True

    def _sendAttribAction(self, matchedVars):
        if matchedVars.get('send_attrib') == sendAttribCmd.id:
            if not self.canMakeSovrinRequest:
                return True
            nym = matchedVars.get('dest_id')
            raw = matchedVars.get('raw') \
                if matchedVars.get('raw') else None
            enc = ast.literal_eval(matchedVars.get('enc')) \
                if matchedVars.get('enc') else None
            hsh = matchedVars.get('hash') \
                if matchedVars.get('hash') else None
            self._addAttribToNym(nym, raw, enc, hsh)
            return True

    def _sendGetAttrAction(self, matchedVars):
        if matchedVars.get('send_get_attr') == sendGetAttrCmd.id:
            if not self.hasAnyKey:
                return True
            if not self.canMakeSovrinRequest:
                return True
            nym = matchedVars.get('dest_id')
            raw = matchedVars.get('raw') \
                if matchedVars.get('raw') else None
            enc = ast.literal_eval(matchedVars.get('enc')) \
                if matchedVars.get('enc') else None
            hsh = matchedVars.get('hash') \
                if matchedVars.get('hash') else None
            self._getAttr(nym,raw,enc,hsh)
            return True

    def _sendGetSchemaAction(self, matchedVars):
        if matchedVars.get('send_get_schema') == sendGetSchemaCmd.id:
            if not self.canMakeSovrinRequest:
                return True
            self.logger.debug("Processing GET_SCHEMA request")
            nym = matchedVars.get('dest_id')
            name = matchedVars.get('name')
            version = matchedVars.get('version')
            self._getSchema(nym,name,version)
            return True

    def _sendGetClaimDefAction(self, matchedVars):
        if matchedVars.get('send_get_claim_def') == sendGetClaimDefCmd.id:
            if not self.canMakeSovrinRequest:
                return True
            self.logger.debug("Processing GET_CLAIM_DEF request")
            seqNo = int(matchedVars.get('ref'))
            signature = matchedVars.get('signature_type')
            self._getClaimDef(seqNo,signature)
            return True

    def _sendNodeAction(self, matchedVars):
        if matchedVars.get('send_node') == sendNodeCmd.id:
            if not self.canMakeSovrinRequest:
                return True
            nym = matchedVars.get('dest_id')
            data = matchedVars.get('data').strip()
            try:
                data = ast.literal_eval(data)
                self._sendNodeTxn(nym, data)
            except:
                self.print('"data" must be in proper format', Token.Error)
            return True

    def _sendPoolUpgAction(self, matchedVars):
        if matchedVars.get('send_pool_upg') == sendPoolUpgCmd.id:
            if not self.canMakeSovrinRequest:
                return True
            name = matchedVars.get(NAME).strip()
            version = matchedVars.get(VERSION).strip()
            action = matchedVars.get(ACTION).strip()
            sha256 = matchedVars.get(SHA256).strip()
            timeout = matchedVars.get(TIMEOUT)
            schedule = matchedVars.get(SCHEDULE)
            justification = matchedVars.get(JUSTIFICATION)
            force = matchedVars.get(FORCE, "False")
            force = force == "True"
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
            except:
                self.print('"schedule" must be in proper format', Token.Error)
                return True
            if timeout:
                timeout = int(timeout.strip())
            self._sendPoolUpgTxn(name, version, action, sha256,
                                 schedule=schedule, timeout=timeout,
                                 justification=justification, force=force)
            return True

    def _sendSchemaAction(self, matchedVars):
        if matchedVars.get('send_schema') == sendSchemaCmd.id:
            self.agent.loop.call_soon(asyncio.ensure_future,
                                      self._sendSchemaActionAsync(matchedVars))
            return True

    async def _sendSchemaActionAsync(self, matchedVars):
        if not self.canMakeSovrinRequest:
            return True

        schema = await self.agent.issuer.genSchema(
            name=matchedVars.get(NAME),
            version=matchedVars.get(VERSION),
            attrNames=[s.strip() for s in matchedVars.get(KEYS).split(",")])

        self.print("The following schema is published "
                   "to the Sovrin distributed ledger\n", Token.BoldBlue,
                   newline=False)
        self.print("{}".format(str(schema)))
        self.print("Sequence number is {}".format(schema.seqId),
                   Token.BoldBlue)

        return True

    def _sendClaimDefAction(self, matchedVars):
        if matchedVars.get('send_claim_def') == sendClaimDefCmd.id:
            self.agent.loop.call_soon(asyncio.ensure_future,
                                      self._sendClaimDefActionAsync(matchedVars))
            return True


    async def _sendClaimDefActionAsync(self, matchedVars):
        if not self.canMakeSovrinRequest:
            return True
        reference = int(matchedVars.get(REF))
        id = ID(schemaId=reference)
        try:
            pk, pkR = await self.agent.issuer.genKeys(id)
        except SchemaNotFound:
            self.print("Schema with seqNo {} not found".format(reference),
                       Token.BoldOrange)
            return False

        self.print("The claim definition was published to the"
                   " Sovrin distributed ledger:\n", Token.BoldBlue,
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
                filePath = SovrinCli._getFilePath(givenFilePath)
                try:
                    # TODO: Shouldn't just be the wallet be involved in loading
                    # an invitation.
                    link = self.agent.loadInvitationFile(filePath)
                    self._printShowAndAcceptLinkUsage(link.name)
                except (FileNotFoundError, TypeError):
                    self.print("Given file does not exist")
                    msgs = self._getShowFileUsage() + self._getLoadFileUsage()
                    self.printUsage(msgs)
                except LinkAlreadyExists:
                    self.print("Link already exists")
                except LinkNotFound:
                    self.print("No link invitation found in the given file")
                except ValueError:
                    self.print("Input is not a valid json"
                               "please check and try again")
                except InvalidLinkException as e:
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

    def _getInvitationMatchingLinks(self, linkName):
        exactMatched = {}
        likelyMatched = {}
        # if we want to search in all wallets, then,
        # change [self.activeWallet] to self.wallets.values()
        walletsToBeSearched = [self.activeWallet]  # self.wallets.values()
        for w in walletsToBeSearched:
            # TODO: This should be moved to wallet
            invitations = w.getMatchingLinks(linkName)
            for i in invitations:
                if i.name == linkName:
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
        #           "Default": [linkWithExactName],
        #           "WalletOne" : [linkWithExactName],
        #     }, "likelyMatched": {
        #           "Default": [similarMatches1, similarMatches2],
        #           "WalletOne": [similarMatches2, similarMatches3]
        #     }
        # }
        return {
            "exactlyMatched": exactMatched,
            "likelyMatched": likelyMatched
        }

    def _syncLinkPostEndPointRetrieval(self, postSync,
                                       link: Link, reply, err, **kwargs):
        if err:
            self.print('    {}'.format(err))
            return True

        postSync(link)

    def _printUsagePostSync(self, link):
        self._printShowAndAcceptLinkUsage(link.name)

    def _getTargetEndpoint(self, li, postSync):
        if not self.activeWallet.identifiers:
            self.print("No key present in keyring for making request on Sovrin,"
                       " so adding one")
            self._newSigner(wallet=self.activeWallet)
        if self._isConnectedToAnyEnv():
            self.print("\nSynchronizing...")
            doneCallback = partial(self._syncLinkPostEndPointRetrieval,
                                   postSync, li)
            try:
                self.agent.sync(li.name, doneCallback)
            except NotConnectedToNetwork:
                self._printCannotSyncSinceNotConnectedEnvMessage()
        else:
            if not self.activeEnv:
                self._printCannotSyncSinceNotConnectedEnvMessage()

    def _getOneLinkForFurtherProcessing(self, linkName):
        totalFound, exactlyMatchedLinks, likelyMatchedLinks = \
            self._getMatchingInvitationsDetail(linkName)

        if totalFound == 0:
            self._printNoLinkFoundMsg()
            return None

        if totalFound > 1:
            self._printMoreThanOneLinkFoundMsg(linkName, exactlyMatchedLinks,
                                               likelyMatchedLinks)
            return None
        li = self._getOneLink(exactlyMatchedLinks, likelyMatchedLinks)
        if SovrinCli.isNotMatching(linkName, li.name):
            self.print('Expanding {} to "{}"'.format(linkName, li.name))
        return li

    def _sendAcceptInviteToTargetEndpoint(self, link: Link):
        self.agent.accept_invitation(link)

    def _acceptLinkPostSync(self, link: Link):
        if link.isRemoteEndpointAvailable:
            self._sendAcceptInviteToTargetEndpoint(link)
        else:
            self.print("Remote endpoint ({}) not found, "
                       "can not connect to {}\n".format(
                link.remoteEndPoint, link.name))
            self.logger.debug("{} has remote endpoint {}".
                              format(link, link.remoteEndPoint))

    def _acceptLinkInvitation(self, linkName):
        li = self._getOneLinkForFurtherProcessing(linkName)

        if li:
            if li.isAccepted:
                self._printLinkAlreadyExcepted(li.name)
            else:
                self.print("Invitation not yet verified.")
                if not li.linkLastSynced:
                    self.print("Link not yet synchronized.")

                if self._isConnectedToAnyEnv():
                    self.print("Attempting to sync...")
                    self._getTargetEndpoint(li, self._acceptLinkPostSync)
                else:
                    if li.isRemoteEndpointAvailable:
                        self._sendAcceptInviteToTargetEndpoint(li)
                    else:
                        self.print("Invitation acceptance aborted.")
                        self._printNotConnectedEnvMessage(
                            "Cannot sync because not connected")

    def _syncLinkInvitation(self, linkName):
        li = self._getOneLinkForFurtherProcessing(linkName)
        if li:
            self._getTargetEndpoint(li, self._printUsagePostSync)

    @staticmethod
    def isNotMatching(source, target):
        return source.lower() != target.lower()

    @staticmethod
    def removeSpecialChars(name):
        return name.replace('"', '').replace("'", "") if name else None

    def _printSyncLinkUsage(self, linkName):
        msgs = self._getSyncLinkUsage(linkName)
        self.printSuggestion(msgs)

    def _printSyncAndAcceptUsage(self, linkName):
        msgs = self._getSyncLinkUsage(linkName) + \
               self._getAcceptLinkUsage(linkName)
        self.printSuggestion(msgs)

    def _printLinkAlreadyExcepted(self, linkName):
        self.print("Link {} is already accepted\n".format(linkName))

    def _printShowAndAcceptLinkUsage(self, linkName=None):
        msgs = self._getShowLinkUsage(linkName) + \
               self._getAcceptLinkUsage(linkName)
        self.printSuggestion(msgs)

    def _printShowAndLoadFileUsage(self):
        msgs = self._getShowFileUsage() + self._getLoadFileUsage()
        self.printUsage(msgs)

    def _printShowAndLoadFileSuggestion(self):
        msgs = self._getShowFileUsage() + self._getLoadFileUsage()
        self.printSuggestion(msgs)

    def _printNoLinkFoundMsg(self):
        self.print("No matching link invitations found in current keyring")
        self._printShowAndLoadFileSuggestion()

    def _isConnectedToAnyEnv(self):
        return self.activeEnv and self.activeClient and \
               self.activeClient.hasSufficientConnections

    def _acceptInvitationLink(self, matchedVars):
        if matchedVars.get('accept_link_invite') == acceptLinkCmd.id:
            linkName = SovrinCli.removeSpecialChars(matchedVars.get('link_name'))
            self._acceptLinkInvitation(linkName)
            return True

    def _pingTarget(self, matchedVars):
        if matchedVars.get('ping') == pingTargetCmd.id:
            linkName = SovrinCli.removeSpecialChars(
                matchedVars.get('target_name'))
            li = self._getOneLinkForFurtherProcessing(linkName)
            if li:
                if li.isRemoteEndpointAvailable:
                    self.agent._pingToEndpoint(li.name, li.remoteEndPoint)
                else:
                    self.print("Please sync first to get target endpoint")
                    self._printSyncLinkUsage(li.name)
            return True

    def _syncLink(self, matchedVars):
        if matchedVars.get('sync_link') == syncLinkCmd.id:
            # TODO: Shouldn't we remove single quotes too?
            linkName = SovrinCli.removeSpecialChars(matchedVars.get('link_name'))
            self._syncLinkInvitation(linkName)
            return True

    def _getMatchingInvitationsDetail(self, linkName):
        linkInvitations = self._getInvitationMatchingLinks(
            SovrinCli.removeSpecialChars(linkName))

        exactlyMatchedLinks = linkInvitations["exactlyMatched"]
        likelyMatchedLinks = linkInvitations["likelyMatched"]

        totalFound = sum([len(v) for v in {**exactlyMatchedLinks,
                                           **likelyMatchedLinks}.values()])
        return totalFound, exactlyMatchedLinks, likelyMatchedLinks

    @staticmethod
    def _getOneLink(exactlyMatchedLinks, likelyMatchedLinks) -> Link:
        li = None
        if len(exactlyMatchedLinks) == 1:
            li = list(exactlyMatchedLinks.values())[0][0]
        else:
            li = list(likelyMatchedLinks.values())[0][0]
        return li

    def _printMoreThanOneLinkFoundMsg(self, linkName, exactlyMatchedLinks,
                                      likelyMatchedLinks):
        self.print('More than one link matches "{}"'.format(linkName))
        exactlyMatchedLinks.update(likelyMatchedLinks)
        for k, v in exactlyMatchedLinks.items():
            for li in v:
                self.print("{}".format(li.name))
        self.print("\nRe enter the command with more specific "
                   "link invitation name")
        self._printShowAndAcceptLinkUsage()

    def _showLink(self, matchedVars):
        if matchedVars.get('show_link') == showLinkCmd.id:
            linkName = matchedVars.get('link_name').replace('"', '')

            totalFound, exactlyMatchedLinks, likelyMatchedLinks = \
                self._getMatchingInvitationsDetail(linkName)

            if totalFound == 0:
                self._printNoLinkFoundMsg()
                return True

            if totalFound == 1:
                li = self._getOneLink(exactlyMatchedLinks, likelyMatchedLinks)

                if SovrinCli.isNotMatching(linkName, li.name):
                    self.print('Expanding {} to "{}"'.format(linkName, li.name))

                self.print("{}".format(str(li)))
                if li.isAccepted:
                    self._printSuggestionPostAcceptLink(self, li)
                else:
                    self._printSyncAndAcceptUsage(li.name)
            else:
                self._printMoreThanOneLinkFoundMsg(linkName,
                                                   exactlyMatchedLinks,
                                                   likelyMatchedLinks)

            return True

    # def _printNoClaimReqFoundMsg(self):
    #     self.print("No matching Claim Requests found in current keyring\n")
    #
    def _printNoProofReqFoundMsg(self):
        self.print("No matching Proof Requests found in current keyring\n")

    def _printNoClaimFoundMsg(self):
        self.print("No matching Claims found in "
                   "any links in current keyring\n")

    def _printMoreThanOneLinkFoundForRequest(self, requestedName, linkNames):
        self.print('More than one link matches "{}"'.format(requestedName))
        for li in linkNames:
            self.print("{}".format(li))
            # TODO: Any suggestion in more than one link?

    # TODO: Refactor following three methods
    # as most of the pattern looks similar

    def _printRequestAlreadyMade(self, extra=""):
        msg = "Request already made."
        if extra:
            msg += "Extra info: {}".format(extra)
        self.print(msg)

    def _printMoreThanOneClaimFoundForRequest(self, claimName, linkAndClaimNames):
        self.print('More than one match for "{}"'.format(claimName))
        for li, cl in linkAndClaimNames:
            self.print("{} in {}".format(li, cl))

    def _findProofRequest(self, claimReqName: str, linkName: str=None) -> \
            (Link, ProofRequest):
        matchingLinksWithClaimReq = self.activeWallet. \
            findAllProofRequests(claimReqName, linkName)  # TODO rename claimReqName -> proofRequestName

        if len(matchingLinksWithClaimReq) == 0:
            self._printNoProofReqFoundMsg()
            return None, None

        if len(matchingLinksWithClaimReq) > 1:
            linkNames = [ml.name for ml, cr in matchingLinksWithClaimReq]
            self._printMoreThanOneLinkFoundForRequest(claimReqName, linkNames)
            return None, None

        return matchingLinksWithClaimReq[0]

    def _getOneLinkAndAvailableClaim(self, claimName, printMsgs: bool = True) -> \
            (Link, Schema):
        matchingLinksWithAvailableClaim = self.activeWallet. \
            getMatchingLinksWithAvailableClaim(claimName)

        if len(matchingLinksWithAvailableClaim) == 0:
            if printMsgs:
                self._printNoClaimFoundMsg()
            return None, None

        if len(matchingLinksWithAvailableClaim) > 1:
            linkNames = [ml.name for ml, _ in matchingLinksWithAvailableClaim]
            if printMsgs:
                self._printMoreThanOneLinkFoundForRequest(claimName, linkNames)
            return None, None

        return matchingLinksWithAvailableClaim[0]

    async def _getOneLinkAndReceivedClaim(self, claimName, printMsgs: bool = True) -> \
            (Link, Tuple, Dict):
        matchingLinksWithRcvdClaim = await self.agent.getMatchingLinksWithReceivedClaimAsync(claimName)

        if len(matchingLinksWithRcvdClaim) == 0:
            if printMsgs:
                self._printNoClaimFoundMsg()
            return None, None, None

        if len(matchingLinksWithRcvdClaim) > 1:
            linkNames = [ml.name for ml, _, _ in matchingLinksWithRcvdClaim]
            if printMsgs:
                self._printMoreThanOneLinkFoundForRequest(claimName, linkNames)
            return None, None, None

        return matchingLinksWithRcvdClaim[0]

    def _setAttr(self, matchedVars):
        if matchedVars.get('set_attr') == setAttrCmd.id:
            attrName = matchedVars.get('attr_name')
            attrValue = matchedVars.get('attr_value')
            curLink, curProofReq, selfAttestedAttrs = self.curContext
            if curProofReq:
                selfAttestedAttrs[attrName] = attrValue
            else:
                self.print("No context, use below command to set the context")
                self.printUsage(self._getShowProofRequestUsage())
            return True

    def _reqClaim(self, matchedVars):
        if matchedVars.get('req_claim') == reqClaimCmd.id:
            claimName = SovrinCli.removeSpecialChars(
                matchedVars.get('claim_name'))
            matchingLink, ac = \
                self._getOneLinkAndAvailableClaim(claimName, printMsgs=False)
            if matchingLink:
                name, version, origin = ac
                if SovrinCli.isNotMatching(claimName, name):
                    self.print('Expanding {} to "{}"'.format(
                        claimName, name))
                self.print("Found claim {} in link {}".
                           format(claimName, matchingLink.name))
                if not self._isConnectedToAnyEnv():
                    self._printNotConnectedEnvMessage()
                    return True

                schemaKey = (name, version, origin)
                self.print("Requesting claim {} from {}...".format(
                    name, matchingLink.name))

                self.agent.sendReqClaim(matchingLink, schemaKey)
            else:
                self._printNoClaimFoundMsg()
            return True

    def _createNewIdentifier(self, identifier, seed,
                             alias=None):
        if not self.isValidSeedForNewKey(seed):
            return True

        if not seed:
            seed = randombytes(32)

        cseed = cleanSeed(seed)

        signer = DidSigner(identifier=identifier, seed=cseed, alias=alias)

        id, signer = self.activeWallet.addIdentifier(identifier,
                                                     seed=cseed, alias=alias)
        self.print("Identifier created in keyring {}".format(self.activeWallet))
        self.print("New identifier is {}".format(signer.identifier))
        self.print("New verification key is {}".format(signer.verkey))
        self._setActiveIdentifier(id)

    def _reqAvailClaims(self, matchedVars):
        if matchedVars.get('req_avail_claims') == reqAvailClaimsCmd.id:
            linkName = SovrinCli.removeSpecialChars(matchedVars.get('link_name'))
            li = self._getOneLinkForFurtherProcessing(linkName)
            if li:
                self.agent.sendRequestForAvailClaims(li)
            return True

    def _newIdentifier(self, matchedVars):
        if matchedVars.get('new_id') == newIdentifierCmd.id:
            identifier = matchedVars.get('id')
            alias = matchedVars.get('alias')

            seed = matchedVars.get('seed')
            self._createNewIdentifier(identifier, seed, alias)
            return True

    def _sendProof(self, matchedVars):
        if matchedVars.get('send_proof') == sendProofCmd.id:
            proofName = SovrinCli.removeSpecialChars(
                matchedVars.get('proof_name').strip())
            linkName = SovrinCli.removeSpecialChars(
                matchedVars.get('link_name').strip())

            li, proofReq = self._findProofRequest(proofName, linkName)

            if not li or not proofReq:
                return False

            self.logger.debug("Building proof using {} for {}".
                              format(proofReq, li))

            # if link or proof request doesn't match with context information,
            # then set the context accordingly
            if li != self.curContext.link or \
                            proofReq != self.curContext.proofRequest:
                self.curContext = Context(li, proofReq, {})

            self.agent.sendProof(li, proofReq)

            return True

    def _sendProofRequest(self, matchedVars):
        if matchedVars.get('send_proof_req') == 'send proof-request':
            proofRequestName = SovrinCli.removeSpecialChars(
                matchedVars.get('proof_request_name').strip())
            target = SovrinCli.removeSpecialChars(
                matchedVars.get('target').strip())

            li = self._getOneLinkForFurtherProcessing(target)

            if li:
                result = self.agent.sendProofReq(li, proofRequestName)
                if result != ERR_NO_PROOF_REQUEST_SCHEMA_FOUND:
                    self.print('Sent proof request "{}" to {}'
                               .format(proofRequestName, target))
                else:
                    self.print(ERR_NO_PROOF_REQUEST_SCHEMA_FOUND)
            else:
                self.print('No link found with name {}'.format(target))

            return True

    async def _showReceivedOrAvailableClaim(self, claimName):
        matchingLink, rcvdClaim, attributes = \
            await self._getOneLinkAndReceivedClaim(claimName)
        if matchingLink:
            self.print("Found claim {} in link {}".
                       format(claimName, matchingLink.name))

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
                       "in any links in current keyring")

    def _printRequestClaimMsg(self, claimName):
        self.printSuggestion(self._getReqClaimUsage(claimName))

    @staticmethod
    def _formatProofRequestAttribute(attributes, verifiableAttributes,
                                     matchingLinkAndReceivedClaim):
        getClaim = itemgetter(2)
        containsAttr = lambda key: lambda t: key in getClaim(t)
        formatted = 'Attributes:\n'

        for k, v in attributes.items():
            # determine if we need to show number for claims which
            # were participated in proof generation
            attrClaimIndex = getIndex(containsAttr(k), matchingLinkAndReceivedClaim)
            showClaimNumber = attrClaimIndex > -1 and \
                              len(matchingLinkAndReceivedClaim) > 1

            formatted += ('    '
                          + ('[{}] '.format(attrClaimIndex + 1)
                             if showClaimNumber else '')
                          + str(k)
                          + (' (V)' if k in verifiableAttributes else '')
                          + ': ' + str(v) + '\n')

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
                            k not in alreadyFulfilledAttrs else '  ')
                            + k + ': ' + '{}\n'.format('None' if v is None else v)
                            )
                if not k in alreadyFulfilledAttrs:
                    alreadyFulfilledAttrs[k] = True

            claimNumber += 1

        return toPrint

    async def _fulfillProofRequestByContext(self, c: Context):
        matchingLinkAndReceivedClaim = await self.agent.getClaimsUsedForAttrs(
            c.proofRequest.attributes)

        # filter all those claims who has some None value
        # since they are not yet requested
        filteredMatchingClaims = []
        for li, cl, issuedAttrs in matchingLinkAndReceivedClaim:
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
        proof_req_name = SovrinCli.removeSpecialChars(proofReqName)
        matchingLink, proofRequest = self._findProofRequest(proof_req_name)

        if matchingLink and proofRequest:
            if matchingLink != self.curContext.link or \
                            proofRequest != self.curContext.proofRequest:
                self.curContext = Context(matchingLink, proofRequest, {})
            self.print('Found proof request "{}" in link "{}"'.
                       format(proofRequest.name, matchingLink.name))

            return await self._fulfillProofRequestByContext(self.curContext)
        else:
            return False

    async def _showProofWithMatchingClaims(self, c: Context):
        self.print(c.proofRequest.fixedInfo + self._formatProofRequestAttribute(
            c.proofRequest.attributes,
            [v.name for k, v in c.proofRequest.verifiableAttributes.items()],
            c.proofRequest.fulfilledByClaims
        ))

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
        if matchedVars.get('show_proof_req') == showProofRequestCmd.id:
            proof_request_name = SovrinCli.removeSpecialChars(
                matchedVars.get('proof_req_name'))

            self.agent.loop.call_soon(asyncio.ensure_future,
                                      self._fulfillAndShowConstructedProof(
                                          proof_request_name))
            return True

    def _showClaim(self, matchedVars):
        if matchedVars.get('show_claim') == showClaimCmd.id:
            claimName = SovrinCli.removeSpecialChars(
                matchedVars.get('claim_name'))
            self.agent.loop.call_soon(asyncio.ensure_future,
                                      self._showReceivedOrAvailableClaim(claimName))

            return True

    def _listClaims(self, matchedVars):
        if matchedVars.get('list_claims') == listClaimsCmd.id:
            link_name = SovrinCli.removeSpecialChars(matchedVars.get('link_name'))

            li = self._getOneLinkForFurtherProcessing(link_name)
            if li:
                # TODO sync if needed, send msg to agent
                self._printAvailClaims(li)
            return True

    def _listLinks(self, matchedVars):
        if matchedVars.get('list_links') == listLinksCmd.id:
            links = self.activeWallet.getLinkNames()
            if len(links) == 0:
                self.print("No links exists")
            else:
                for link in links:
                    self.print(link + "\n")
            return True

    def _printAvailClaims(self, link):
        self.print(link.avail_claims_str())

    def _showFile(self, matchedVars):
        if matchedVars.get('show_file') == showFileCmd.id:
            givenFilePath = matchedVars.get('file_path')
            filePath = SovrinCli._getFilePath(givenFilePath)
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
        if not os.path.isfile(os.path.join(self.basedirpath,
                                           self.envs[envName].poolLedger)):
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
        self.config.poolTransactionsFile = None
        self.config.domainTransactionsFile = None
        self._setPrompt(self.currPromptText.replace("{}{}".format(
            PROMPT_ENV_SEPARATOR, oldEnv), ""))

        if not toConnectToNewEnv:
            self.print("Disconnected from {}".format(oldEnv), Token.BoldGreen)

        if toConnectToNewEnv is None:
            self.restoreLastActiveWallet()

    def printWarningIfActiveWalletIsIncompatible(self):
        if self._activeWallet:
            if not self.checkIfWalletBelongsToCurrentContext(self._activeWallet):
                self.print(self.getWalletContextMistmatchMsg, Token.BoldOrange)
                self.print("Any changes made to this keyring won't "
                           "be persisted.", Token.BoldOrange)

    def moveActiveWalletToNewContext(self, newEnv):
        if self._activeWallet:
            if not self._activeWallet.env or self._activeWallet.env == NO_ENV:
                currentWalletName = self._activeWallet.name
                self._activeWallet.env = newEnv
                randomSuffix = ''
                sourceWalletFilePath = getWalletFilePath(
                    self.getContextBasedKeyringsBaseDir(), self.walletFileName)
                targetContextDir = os.path.join(self.getKeyringsBaseDir(),
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

                self.print("Current active keyring got moved to '{}' "
                           "environment. Here is the detail:".format(newEnv),
                           Token.BoldBlue)
                self.print("    keyring name: {}".format(
                    currentWalletName), Token.BoldBlue)
                self.print("    old location: {}".format(
                    sourceWalletFilePath), Token.BoldBlue)
                self.print("    new location: {}".format(
                    targetWalletFilePath), Token.BoldBlue)
                if randomSuffix != '':
                    self.print("    new keyring name: {}".format(
                        self._activeWallet.name), Token.BoldBlue)
                    self.print("    Note:\n       Target environment "
                               "already had a keyring with name '{}', so we "
                               "renamed current active keyring to '{}'.\n      "
                               " You can always rename any keyring with more "
                               "meaningful name with 'rename keyring' command.".
                               format(currentWalletName, self._activeWallet.name),
                               Token.BoldBlue)
                self._activeWallet = None
        pass

    def _connectTo(self, matchedVars):
        if matchedVars.get('conn') == connectToCmd.id:
            envName = matchedVars.get('env_name')
            envError = self.canConnectToEnv(envName)
            if envError:
                self.print(envError, token=Token.Error)
                self._printConnectUsage()
            else:
                if self.nodeReg:
                    oldEnv = self.activeEnv

                    self._saveActiveWallet()

                    if not oldEnv:
                        self.moveActiveWalletToNewContext(envName)

                    isAnyWalletExistsForNewEnv = \
                        self.isAnyWalletFileExistsForGivenEnv(envName)

                    if oldEnv or isAnyWalletExistsForNewEnv:
                        self._disconnectFromCurrentEnv(envName)

                    self.config.poolTransactionsFile = self.envs[envName].poolLedger
                    self.config.domainTransactionsFile = \
                        self.envs[envName].domainLedger
                    # Prompt has to be changed, so it show the environment too
                    self.activeEnv = envName
                    self._setPrompt(self.currPromptText.replace("{}{}".format(
                        PROMPT_ENV_SEPARATOR, oldEnv), ""))

                    if isAnyWalletExistsForNewEnv:
                        self.restoreLastActiveWallet()

                    self.printWarningIfActiveWalletIsIncompatible()

                    self._buildClientIfNotExists(self.config)
                    self.print("Connecting to {}...".format(envName), Token.BoldGreen)

                    self.ensureClientConnected()

                else:
                    msg = '\nThe information required to connect this client to the nodes cannot be found. ' \
                          '\nThis is an error. To correct the error, get the file containing genesis transactions ' \
                          '\n(the file name is `{}`) from the github repository and place ' \
                          '\nit in directory `{}`.\n' \
                          '\nThe github url is {}.\n'.format(self.config.poolTransactionsFile,
                                                             self.config.baseDir,
                                                             self.githubUrl)
                    self.print(msg)

            return True

    @property
    def getActiveEnv(self):
        prompt, env = PlenumCli.getPromptAndEnv(self.name,
                                                self.currPromptText)
        return env

    def getAllSubDirNamesForKeyrings(self):
        lst = list(ENVS.keys())
        lst.append(NO_ENV)
        return lst

    def updateEnvNameInWallet(self):
        if not self._activeWallet.getEnvName:
            self._activeWallet.env = self.activeEnv if self.activeEnv \
                else NO_ENV

    def getStatus(self):
        # TODO: This needs to show active keyring and active identifier
        if not self.activeEnv:
            self._printNotConnectedEnvMessage()
        else:
            if self.activeClient.hasSufficientConnections:
                msg = "Connected to {} Sovrin network".format(self.activeEnv)
            else:
                msg = "Attempting connection to {} Sovrin network". \
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
            txn = {
                TXN_TYPE: NYM,
                TARGET_NYM: nym,
                TXN_ID: sha256(randomString(6).encode()).hexdigest()
            }
            if role:
                txn[ROLE] = role.upper()
            # TODO: need to check if this needs to persist as well
            self.genesisTransactions.append(txn)
            self.print('Genesis transaction added.')
            return True

    @staticmethod
    def bootstrapClientKey(client, node, identifier=None):
        pass

    def ensureClientConnected(self):
        if self._isConnectedToAnyEnv():
            self.print("Connected to {}.".format(self.activeEnv), Token.BoldBlue)
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
        if not self.canMakeSovrinRequest:
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
            self.print("Creates the link, generates Identifier and signing keys")
            self.printUsage(self._getLoadFileUsage("<invitation filename>"))

        def showHelper():
            self.print("Shows the info about the link invitation")
            self.printUsage(self._getShowFileUsage("<invitation filename>"))

        def showLinkHelper():
            self.print("Shows link info in case of one matching link, "
                       "otherwise shows all the matching links")
            self.printUsage(self._getShowLinkUsage())

        def connectHelper():
            self.print("Lets you connect to the respective environment")
            self.printUsage(self._getConnectUsage())

        def syncHelper():
            self.print("Synchronizes the link between the endpoints")
            self.printUsage(self._getSyncLinkUsage())

        def defaultHelper():
            self.printHelp()

        mappings = {
            'show': showHelper,
            'prompt': promptHelper,
            'principals': principalsHelper,
            'load': loadHelper,
            'show link': showLinkHelper,
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
        mappings['newIdentifier'] = newIdentifierCmd
        mappings['sendNymAction'] = sendNymCmd
        mappings['sendGetNymAction'] = sendGetNymCmd
        mappings['sendAttribAction'] = sendAttribCmd
        mappings['sendGetAttrAction'] = sendGetAttrCmd
        mappings['sendNodeAction'] = sendNodeCmd
        mappings['sendPoolUpgAction'] = sendPoolUpgCmd
        mappings['sendSchemaAction'] = sendSchemaCmd
        mappings['sendGetSchemaAction'] = sendGetSchemaCmd
        mappings['sendClaimDefAction'] = sendClaimDefCmd
        mappings['sendGetClaimDefAction'] = sendGetClaimDefCmd
        mappings['showFile'] = showFileCmd
        mappings['loadFile'] = loadFileCmd
        mappings['showLink'] = showLinkCmd
        mappings['syncLink'] = syncLinkCmd
        mappings['pingTarget'] = pingTargetCmd
        mappings['acceptInvitationLink'] = acceptLinkCmd
        mappings['showClaim'] = showClaimCmd
        mappings['listClaims'] = listClaimsCmd
        mappings['listLinks'] = listLinksCmd
        mappings['reqClaim'] = reqClaimCmd
        mappings['showProofRequest'] = showProofRequestCmd
        mappings['acceptInvitationLink'] = acceptLinkCmd
        mappings['addGenTxnAction'] = addGenesisTxnCmd
        mappings['setAttr'] = setAttrCmd
        mappings['sendProofRequest'] = sendProofRequestCmd
        mappings['sendProof'] = sendProofCmd
        mappings['newIdentifier'] = newIdentifierCmd
        mappings['reqAvailClaims'] = reqAvailClaimsCmd

        # TODO: These seems to be obsolete, so either we need to remove these
        # command handlers or let it point to None
        mappings['addGenesisAction'] = None  # overriden by addGenTxnAction

        return mappings

    @property
    def canMakeSovrinRequest(self):
        if not self.hasAnyKey:
            return False
        if not self.activeEnv:
            self._printNotConnectedEnvMessage()
            return False
        if not self.checkIfWalletBelongsToCurrentContext(self._activeWallet):
            self.print(self.getWalletContextMistmatchMsg, Token.BoldOrange)
            return False

        return True

    def getConfig(homeDir=None):
        return getConfig(homeDir)


class DummyClient:
    def submitReqs(self, *reqs):
        pass

    @property
    def hasSufficientConnections(self):
        pass
