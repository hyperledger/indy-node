import importlib
import json
import os
import shutil
import tempfile

from indy_common.config_helper import NodeConfigHelper
from indy_node.server.config_helper import create_config_dirs
from plenum.recorder.src.replayer import get_recorders_from_node_data_dir, \
    prepare_node_for_replay_and_replay

from stp_core.types import HA

from stp_core.loop.looper import Looper

from indy_node.server.node import Node

from plenum.server.replicas import Replicas

from plenum.server.replica import Replica

from indy_common.config_util import getConfig
from plenum.recorder.src.replayable_node import create_replayable_node_class

RecordingZipFilePath = '/home/lovesh/rec.zip'

ReplayBaseDirPath = '/home/lovesh/tmp'


def process_recording_zip():
    # Unzip the recording file
    return


def get_updated_config():
    # Update current config with config file from the recording zip
    return getConfig()


def setup_logging():
    pass


def update_loaded_config(config):
    config.USE_WITH_STACK = 2
    import stp_zmq.kit_zstack
    importlib.reload(stp_zmq.kit_zstack)
    import plenum.common.stacks
    importlib.reload(plenum.common.stacks)
    import plenum.server.node
    importlib.reload(plenum.server.node)
    import indy_node.server.node
    importlib.reload(indy_node.server.node)


def replay_node():
    orig_node_dir = '/home/lovesh/Downloads/Node5.20180516165513'
    replaying_node_name = 'Node5'

    pool_name = 'sandbox'

    replay_node_dir = tempfile.TemporaryDirectory().name
    print(replay_node_dir)
    # with tempfile.TemporaryDirectory() as replay_node_dir:
    general_config_dir = create_config_dirs(replay_node_dir)
    config = getConfig(general_config_dir)
    update_loaded_config(config)
    pool_dir = os.path.join(replay_node_dir, pool_name)
    orig_node_pool_dir = os.path.join(orig_node_dir, pool_name)

    # for d in (pool_dir, data_dir):
    #     os.makedirs(d, exist_ok=True)
    #
    # for file in os.listdir(orig_node_pool_dir):
    #     if file.endswith('.json') or file.endswith('_genesis'):
    #         shutil.copy(os.path.join(orig_node_pool_dir, file), pool_dir)
    #
    # shutil.copytree(os.path.join(orig_node_pool_dir, 'keys'),
    #                 os.path.join(pool_dir, 'keys'))
    # shutil.copytree(os.path.join(orig_node_dir, 'plugins'),
    #                 os.path.join(replay_node_dir, 'plugins'))
    trg_var_dir = os.path.join(replay_node_dir, 'var', 'lib', 'indy', pool_name)
    orig_node_data_dir = os.path.join(orig_node_pool_dir, 'data')
    os.makedirs(trg_var_dir, exist_ok=True)
    # shutil.copytree(src_etc_dir, trg_etc_dir)
    for file in os.listdir(orig_node_pool_dir):
        if file.endswith('.json') or file.endswith('_genesis'):
            shutil.copy(os.path.join(orig_node_pool_dir, file), trg_var_dir)

    shutil.copytree(os.path.join(orig_node_pool_dir, 'keys'),
                    os.path.join(trg_var_dir, 'keys'))
    shutil.copytree(os.path.join(orig_node_dir, 'plugins'),
                    os.path.join(os.path.join(replay_node_dir, 'var', 'lib', 'indy'), 'plugins'))

    node_rec, client_rec = get_recorders_from_node_data_dir(
        os.path.join(orig_node_pool_dir, 'data'), replaying_node_name)
    start_times_file = os.path.join(orig_node_data_dir, replaying_node_name, 'start_times')
    with open(start_times_file, 'r') as f:
        start_times = json.loads(f.read())

    replayable_node_class = create_replayable_node_class(Replica,
                                                         Replicas,
                                                         Node)
    node_ha = HA("0.0.0.0", 9701)
    client_ha = HA("0.0.0.0", 9702)

    node_config_helper = NodeConfigHelper(replaying_node_name, config,
                                          chroot=replay_node_dir)
    with Looper(debug=config.LOOPER_DEBUG) as looper:
        replaying_node = replayable_node_class(replaying_node_name,
                                               config_helper=node_config_helper,
                                               ha=node_ha, cliha=client_ha)
        replaying_node = prepare_node_for_replay_and_replay(looper,
                                                            replaying_node,
                                                            node_rec,
                                                            client_rec,
                                                            start_times)
        print('Replaying node, size: {}, root_hash: {}'.format(
            replaying_node.domainLedger.size,
            replaying_node.domainLedger.root_hash
        ))

        print('Final run of looper')
        looper.runFor(10)


if __name__ == "__main__":
    replay_node()
