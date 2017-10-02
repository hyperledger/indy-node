from typing import Union, Tuple
import inspect
import re

from collections import namedtuple
from pathlib import Path

from config.config import cmod
from plenum.common.util import randomString

from plenum.test import waits
from indy_client.test.client.TestClient import TestClient

from stp_core.common.log import getlogger
from plenum.common.signer_did import DidSigner
from plenum.common.constants import REQNACK, OP_FIELD_NAME, REJECT, REPLY
from plenum.common.types import f, HA
from stp_core.types import Identifier

from stp_core.loop.eventually import eventually
from plenum.test.test_client import genTestClient as genPlenumTestClient, \
    genTestClientProvider as genPlenumTestClientProvider

from indy_common.identity import Identity
from indy_common.constants import NULL

from indy_client.client.wallet.upgrade import Upgrade
from indy_client.client.wallet.wallet import Wallet

logger = getlogger()


def createNym(looper, nym, creatorClient, creatorWallet: Wallet, role=None,
              verkey=None):
    idy = Identity(identifier=nym,
                   verkey=verkey,
                   role=role)
    creatorWallet.addTrustAnchoredIdentity(idy)
    reqs = creatorWallet.preparePending()
    creatorClient.submitReqs(*reqs)

    def check():
        assert creatorWallet._trustAnchored[nym].seqNo

    timeout = waits.expectedTransactionExecutionTime(
        len(creatorClient.nodeReg)
    )
    looper.run(eventually(check, retryWait=1, timeout=timeout))


def makePendingTxnsRequest(client, wallet):
    wallet.pendSyncRequests()
    prepared = wallet.preparePending()
    client.submitReqs(*prepared)


def buildStewardClient(looper, tdir, stewardWallet):
    s, _ = genTestClient(tmpdir=tdir, usePoolLedger=True)
    s.registerObserver(stewardWallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, stewardWallet)
    return s


def addRole(looper, creatorClient, creatorWallet, name,
            addVerkey=True, role=None):
    wallet = Wallet(name)
    signer = DidSigner()
    idr, _ = wallet.addIdentifier(signer=signer)
    verkey = wallet.getVerkey(idr) if addVerkey else None
    createNym(looper, idr, creatorClient, creatorWallet, verkey=verkey,
              role=role)
    return wallet


def submitPoolUpgrade(
        looper,
        senderClient,
        senderWallet,
        name,
        action,
        version,
        schedule,
        timeout,
        sha256):
    upgrade = Upgrade(name, action, schedule, version, sha256, timeout,
                      senderWallet.defaultId)
    senderWallet.doPoolUpgrade(upgrade)
    reqs = senderWallet.preparePending()
    senderClient.submitReqs(*reqs)

    def check():
        assert senderWallet._upgrades[upgrade.key].seqNo
    timeout = waits.expectedTransactionExecutionTime(
        len(senderClient.nodeReg)
    )
    looper.run(eventually(check, timeout=timeout))


def getClientAddedWithRole(nodeSet, tdir, looper, client, wallet, name,
                           role=None, addVerkey=True,
                           client_connects_to=None):
    newWallet = addRole(looper, client, wallet,
                        name=name, addVerkey=addVerkey, role=role)
    c, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes(count=client_connects_to))
    c.registerObserver(newWallet.handleIncomingReply)
    return c, newWallet


def checkErrorMsg(typ, client, reqId, contains='', nodeCount=4):
    reqs = [x for x, _ in client.inBox if x[OP_FIELD_NAME] == typ and
            x[f.REQ_ID.nm] == reqId]
    for r in reqs:
        assert f.REASON.nm in r
        assert contains in r[f.REASON.nm], '{} not in {}'.format(
            contains, r[f.REASON.nm])
    assert len(reqs) == nodeCount


def checkNacks(client, reqId, contains='', nodeCount=4):
    checkErrorMsg(REQNACK, client, reqId,
                  contains=contains, nodeCount=nodeCount)


def checkRejects(client, reqId, contains='', nodeCount=4):
    checkErrorMsg(REJECT, client, reqId, contains=contains,
                  nodeCount=nodeCount)


def checkAccpets(client, reqId, nodeCount=4):
    checkErrorMsg(REPLY, client, reqId, contains='',
                  nodeCount=nodeCount)


def submitAndCheckRejects(
        looper,
        client,
        wallet,
        op,
        identifier,
        contains='UnauthorizedClientRequest',
        check_func=checkRejects):

    reqId = submit(wallet, op, identifier, client)
    timeout = waits.expectedReqNAckQuorumTime()
    looper.run(eventually(check_func,
                          client,
                          reqId,
                          contains,
                          retryWait=1,
                          timeout=timeout))


def submitAndCheckAccepts(looper, client, wallet, op, identifier):

    reqId = submit(wallet, op, identifier, client)
    timeout = waits.expectedReqNAckQuorumTime()
    looper.run(eventually(checkAccpets,
                          client,
                          reqId,
                          retryWait=1,
                          timeout=timeout))


def submit(wallet, op, identifier, client):
    req = wallet.signOp(op, identifier=identifier)
    wallet.pendRequest(req)
    reqs = wallet.preparePending()
    client.submitReqs(*reqs)

    return req.reqId


def genTestClient(nodes=None,
                  nodeReg=None,
                  tmpdir=None,
                  identifier: Identifier = None,
                  verkey: str = None,
                  peerHA: Union[HA, Tuple[str, int]] = None,
                  testClientClass=TestClient,
                  usePoolLedger=False,
                  name: str=None) -> (TestClient, Wallet):
    testClient, wallet = genPlenumTestClient(nodes,
                                             nodeReg,
                                             tmpdir,
                                             testClientClass,
                                             verkey=verkey,
                                             identifier=identifier,
                                             bootstrapKeys=False,
                                             usePoolLedger=usePoolLedger,
                                             name=name)
    testClient.peerHA = peerHA
    return testClient, wallet


def genConnectedTestClient(looper,
                           nodes=None,
                           nodeReg=None,
                           tmpdir=None,
                           identifier: Identifier = None,
                           verkey: str = None
                           ) -> TestClient:
    c, w = genTestClient(nodes, nodeReg=nodeReg, tmpdir=tmpdir,
                         identifier=identifier, verkey=verkey)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    return c, w


def genTestClientProvider(nodes=None,
                          nodeReg=None,
                          tmpdir=None,
                          clientGnr=genTestClient):
    return genPlenumTestClientProvider(nodes, nodeReg, tmpdir, clientGnr)


def clientFromSigner(signer, looper, nodeSet, tdir):
    wallet = Wallet(signer.identifier)
    wallet.addIdentifier(signer)
    s = genTestClient(nodeSet, tmpdir=tdir, identifier=signer.identifier)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    return s


def addUser(looper, creatorClient, creatorWallet, name,
            addVerkey=True):
    wallet = Wallet(name)
    signer = DidSigner()
    idr, _ = wallet.addIdentifier(signer=signer)
    verkey = wallet.getVerkey(idr) if addVerkey else None
    createNym(looper, idr, creatorClient, creatorWallet, verkey=verkey)
    return wallet


def peer_path(filename):
    s = inspect.stack()
    caller = None
    for i in range(1, len(s)):
        # pycharm can wrap calls, so we want to ignore those in the stack
        if 'pycharm' not in s[i].filename:
            caller = s[i].filename
            break
    return Path(caller).parent.joinpath(filename)


def _within_hint(match, ctx):
    w = match.group(1)
    ctx.cmd_within = float(w) if w else None


def _ignore_extra_lines(match, ctx):
    ctx.ignore_extra_lines = True


CommandHints = namedtuple('CommandHints', 'pattern, callback')
command_hints = [
    CommandHints(r'\s*within\s*:\s*(\d*\.?\d*)', _within_hint),
    CommandHints(r'\s*ignore\s*extra\s*lines\s*', _ignore_extra_lines),
]


# marker class for regex pattern
class P(str):
    def match(self, other):
        return re.match('^{}$'.format(self), other)


class RunnerContext:
    def __init__(self):
        self.clis = {}
        self.output = []
        self.cmd_within = None
        self.line_no = 0


class ScriptRunner:
    def __init__(self, CliBuilder, looper, be, do, expect):
        self._cli_builder = CliBuilder
        self._looper = looper
        self._be = be
        self._do = do
        self._expect = expect

        # contexts allows one ScriptRunner maintain state for multiple scripts
        self._contexts = {}
        self._cur_context_name = None

        Router = namedtuple('Router', 'pattern, ends_output, handler')

        self.routers = [
            Router(
                re.compile(r'\s*#(.*)'),
                False,
                self._handleComment),
            Router(
                re.compile(r'\s*(\S*)?\s*>\s*(.*?)\s*(?:<--(.*?))?\s*'),
                True,
                self._handleCommand),
            Router(
                re.compile(r'\s*~\s*(be|start)\s+(.*)'),
                True,
                self._handleBe)]

    # noinspection PyAttributeOutsideInit

    def cur_ctx(self):
        try:
            return self._contexts[self._cur_context_name]
        except KeyError:
            self._contexts[self._cur_context_name] = RunnerContext()
        return self._contexts[self._cur_context_name]

    def run(self, filename, context=None):
        # by default, use a new context for each run
        self._cur_context_name = context if context else randomString()

        contents = Path(filename).read_text()

        for line in contents.lstrip().splitlines():
            self.cur_ctx().line_no += 1
            for r in self.routers:
                m = r.pattern.fullmatch(line)
                if m:
                    if r.ends_output:
                        self._checkOutput()
                    r.handler(m)
                    break
            else:
                self.cur_ctx().output.append(line)

        self._checkOutput()

    def _be_str(self, cli_str, create_if_no_exist=False):
        if cli_str not in self.cur_ctx().clis:
            if not create_if_no_exist:
                raise RuntimeError("{} does not exist; 'start' it first".
                                   format(cli_str))
            self.cur_ctx().clis[cli_str] = next(
                self._cli_builder(cli_str,
                                  looper=self._looper,
                                  unique_name=cli_str + '-' +
                                  self._cur_context_name))
        self._be(self.cur_ctx().clis[cli_str])

    def _handleBe(self, match):
        self._be_str(match.group(2), True)

    def _handleComment(self, match):
        c = match.group(1).strip()
        if c == 'break':
            pass

    def _handleCommand(self, match):
        cli_str = match.group(1)
        if cli_str:
            self._be_str(cli_str)

        cmd = match.group(2)

        hint_str = match.group(3)
        if hint_str:
            hints = hint_str.strip().split(',')
            for hint in hints:
                hint = hint.strip()
                for hint_handler in command_hints:
                    m = re.match(hint_handler.pattern, hint)
                    if m:
                        hint_handler.callback(m, self.cur_ctx())
                        break
                else:
                    raise RuntimeError("no handler found for hint '{}' at "
                                       "line no {}".
                                       format(hint, self.cur_ctx().line_no))

        self._do(cmd)

    def _checkOutput(self):
        if self.cur_ctx().output:
            new = []
            reout = re.compile(r'(.*)<--\s*regex\s*')
            for o in self.cur_ctx().output:
                m = reout.fullmatch(o)
                if m:
                    new.append(P(m.group(1).rstrip()))
                else:
                    new.append(o)

            ignore_extra_lines = False
            if hasattr(self.cur_ctx(), 'ignore_extra_lines'):
                ignore_extra_lines = self.cur_ctx().ignore_extra_lines
            self._expect(new,
                         within=self.cur_ctx().cmd_within,
                         line_no=self.cur_ctx().line_no,
                         ignore_extra_lines=ignore_extra_lines)
            self.cur_ctx().output = []
            self.cur_ctx().cmd_within = None
            self.cur_ctx().ignore_extra_lines = False
