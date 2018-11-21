import re

from collections import namedtuple
from pathlib import Path

from plenum.common.util import randomString

from plenum.test import waits

from stp_core.common.log import getlogger

from stp_core.loop.eventually import eventually
from indy_common.identity import Identity

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
