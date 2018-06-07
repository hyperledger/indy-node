import subprocess
import os

import logging
import pytest
from plenum.test.recorder.helper import reload_modules_for_recorder, _reload_module
from stp_core.common.log import getlogger, Logger

from indy_node.test.catchup.conftest import some_transactions_done


def find_ns_script_dir():
    path = os.path.dirname(__file__)
    path = os.path.join(path, '../../..', 'tools', 'diagnostics')
    path = os.path.abspath(path)
    return path


def test_nscapture_unit_tests():
    path = os.path.join(find_ns_script_dir(), 'nscapture')
    rtn = subprocess.run([path, '-t'])
    assert rtn.returncode == 0, "The internal unit test did not pass"


@pytest.fixture(autouse=True)
def setup_logging(tdir, tconf):
    Logger().apply_config(tconf)
    log_file_name = os.path.join(tdir, 'var', 'log', 'indy', 'sandbox',
                                 'Alpha' + ".log")
    Logger().enableFileLogging(log_file_name)
    logger = getlogger()
    logger.setLevel(tconf.logLevel)

#
# @pytest.fixture(autouse=True)
# def turn_recorder(tconf):
#     reload_modules_for_recorder(tconf)
#

@pytest.fixture(scope="module")
def tconf(tconf):
    tconf.STACK_COMPANION = 1
    reload_modules_for_recorder(tconf)
    import indy_node.server.node
    import indy_node.test.helper
    _reload_module(indy_node.server.node)
    _reload_module(indy_node.test.helper)
    return tconf


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
    capture_cmd_path = os.path.join(find_ns_script_dir(), 'nscapture')
    rtn = subprocess.run([capture_cmd_path, '-r', root_dir, '-n', 'Alpha', '-o', tdir])
    assert rtn.returncode == 0, "Capture did not run successfully"

    recording = list(filter(lambda x: x.startswith('Alpha'), os.listdir(tdir)))
    assert len(recording) == 1
    recording = recording.pop()

    #  Replay recording
    replay_cmd_path = os.path.join(find_ns_script_dir(), 'nsreplay')
    replay_path = os.path.join(tdir, 'replayed', '0')
    rtn = subprocess.run([replay_cmd_path, '-o', replay_path, os.path.join(tdir, recording)])
    assert rtn.returncode == 0, "Replay did not run successfully"

    #  Capture the replay
    rtn = subprocess.run([capture_cmd_path, '-r', replay_path, '-n', 'Alpha', '-o', tdir])
    assert rtn.returncode == 0, "Capture did not run successfully"

    captures_archives = list(filter(lambda x: x.startswith('Alpha'), os.listdir(tdir)))
    assert len(captures_archives) == 2

    diff_cmd_path = os.path.join(find_ns_script_dir(), 'nsdiff')
    cmd = [diff_cmd_path]
    cmd.extend(captures_archives)
    rtn = subprocess.run(cmd, cwd=tdir)
    assert rtn.returncode == 0, "Recording and replay were not identical"
    pass
