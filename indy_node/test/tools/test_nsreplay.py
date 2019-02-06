import os

import importlib
import pytest
from plenum.test.recorder.helper import reload_modules_for_recorder, _reload_module
from stp_core.common.log import getlogger, Logger
import tempfile

from indy_node.test.catchup.conftest import some_transactions_done

whitelist = ['cannot find remote with name']


def find_ns_script_dir():
    path = os.path.dirname(__file__)
    path = os.path.join(path, '../../..', 'tools', 'diagnostics')
    path = os.path.abspath(path)
    return path


def load_script(temp_file, script_name):
    spec = importlib.util.spec_from_file_location(script_name, temp_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_script(script_name, args):
    cmd_path = os.path.join(find_ns_script_dir(), script_name)
    with open(cmd_path, 'r+b') as r_file:
        file_content = r_file.read()
        with tempfile.NamedTemporaryFile('w+b', suffix=".py", delete=False) as w_file:
            w_file.write(file_content)
            w_file.flush()

            mod = load_script(w_file.name, script_name)

            args = mod.parse_args(argv=args)
            try:
                rtn = mod.main(args)
            except SystemExit:
                return -1
            return rtn


def test_nscapture_unit_tests():
    cmd_path = os.path.join(find_ns_script_dir(), 'nscapture')
    with open(cmd_path, 'r+b') as r_file:
        file_content = r_file.read()
        with tempfile.NamedTemporaryFile('w+b', suffix=".py") as w_file:
            w_file.write(file_content)
            w_file.flush()

            mod = load_script(w_file.name, 'nscapture')

            rtn = mod.test(None, mod)
            assert rtn == 0, "The internal unit test did not pass"


@pytest.fixture(autouse=True)
def setup_logging(tdir, tconf):
    Logger().apply_config(tconf)
    log_file_name = os.path.join(tdir, 'var', 'log', 'indy', 'sandbox',
                                 'Alpha' + ".log")
    Logger().enableFileLogging(log_file_name)
    logger = getlogger()
    logger.setLevel(tconf.logLevel)


@pytest.fixture(scope="module")
def tconf(tconf):
    tconf.STACK_COMPANION = 1
    reload_modules_for_recorder(tconf)
    import indy_node.server.node
    import indy_node.test.helper
    _reload_module(indy_node.server.node)
    _reload_module(indy_node.test.helper)
    return tconf


@pytest.yield_fixture(scope="session", autouse=True)
def warncheck(warnfilters):
    pass


def test_end_to_end_replay(looper,
                           tdir,
                           tdirWithPoolTxns,
                           tdirWithDomainTxns,
                           nodeSet,
                           sdk_pool_handle,
                           sdk_wallet_trust_anchor
                           ):
    some_transactions_done(looper, nodeSet, sdk_pool_handle,
                           sdk_wallet_trust_anchor)

    for node in nodeSet:
        node.cleanupOnStopping = False
        node.stop()

    root_dir = tdir
    # root_dir = '/home/devin/temp/B6/test/0'

    #  Capture the original
    rtn = run_script('nscapture', ['-r', root_dir, '-n', 'Alpha', '-o', tdir])
    assert rtn == 0, "Capture did not run successfully"

    recording = list(filter(lambda x: x.startswith('Alpha'), os.listdir(tdir)))
    assert len(recording) == 1
    recording = recording.pop()

    #  Replay recording
    replay_path = os.path.join(tdir, 'replayed', '0')
    rtn = run_script('nsreplay', ['-o', replay_path, os.path.join(tdir, recording)])
    assert rtn == 0, "Replay did not run successfully"

    #  Capture the replay
    rtn = run_script('nscapture', ['-r', replay_path, '-n', 'Alpha', '-o', tdir])
    assert rtn == 0, "Capture did not run successfully"

    captures_archives = list(filter(lambda x: x.startswith('Alpha'), os.listdir(tdir)))
    assert len(captures_archives) == 2

    args = []
    for archive in captures_archives:
        args.append(os.path.join(tdir, archive))
    rtn = run_script('nsdiff', args)
    assert rtn == 0, "Recording and replay were not identical"
    pass
