import os
import pytest
import logging

from indy_common import strict_types
from indy_common.config import GENERAL_CONFIG_FILE
from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields
from indy_node.general_config import ubuntu_platform_config, windows_platform_config, general_config
from indy_node.server.config_helper import create_config_dirs
from stp_core.common.log import getlogger
from indy_common.config_helper import ConfigHelper, NodeConfigHelper

# typecheck during tests
strict_types.defaultShouldCheck = True

# noinspection PyUnresolvedReferences
from plenum.test.conftest import GENERAL_CONFIG_DIR, \
    txnPoolNodesLooper, overriddenConfigValues  # noqa

logger = getlogger()


@pytest.fixture(scope="module")
def config_helper_class():
    return ConfigHelper


@pytest.fixture(scope="module")
def node_config_helper_class():
    return NodeConfigHelper


def _populate_config_file(config_file, platform='ubuntu'):
    if platform == 'ubuntu':
        platform_config = ubuntu_platform_config
    elif platform == 'windows':
        platform_config = windows_platform_config
    else:
        raise RuntimeError('Unknown platform {}. Cannot load config'.format(platform))

    with open(general_config.__file__, 'r') as general_config_file:
        lines = general_config_file.readlines()
        with open(platform_config.__file__, 'r') as platform_config_file:
            with open(config_file,
                      'w') as general_config_result_file:
                for line in lines:
                    if line.startswith('NETWORK_NAME'):
                        line = 'NETWORK_NAME = \'sandbox\'\n'
                    general_config_result_file.write(line)
                general_config_result_file.write(
                    platform_config_file.read())


def _general_conf_tdir(tmp_dir):
    cdir = create_config_dirs(tmp_dir)
    config_file = os.path.join(cdir, GENERAL_CONFIG_FILE)
    _populate_config_file(config_file)
    return cdir


@pytest.fixture(scope='module')
def general_conf_tdir(tdir):
    general_config_dir = _general_conf_tdir(tdir)
    logger.debug("module-level general config directory: {}".format(general_config_dir))
    return general_config_dir


@pytest.fixture()
def general_conf_tdir_for_func(tdir_for_func):
    general_config_dir = _general_conf_tdir(tdir_for_func)
    logger.debug("function-level general config directory: {}".format(general_config_dir))
    return general_config_dir


def _tconf(general_config):
    config = getConfig(general_config_dir=general_config)
    for k, v in overriddenConfigValues.items():
        setattr(config, k, v)
    config.MinSepBetweenNodeUpgrades = 5
    return config


@pytest.fixture(scope="module")
def tconf(general_conf_tdir):
    return _tconf(general_conf_tdir)


@pytest.fixture()
def tconf_for_func(general_conf_tdir_for_func):
    return _tconf(general_conf_tdir_for_func)


@pytest.fixture(scope="module")
def poolTxnTrusteeNames():
    return "Trustee1",


@pytest.fixture(scope="module")  # noqa
def looper(txnPoolNodesLooper):
    return txnPoolNodesLooper


@pytest.fixture(scope="module")
def domainTxnOrderedFields():
    return getTxnOrderedFields()


@pytest.fixture(autouse=True)
def setTestLogLevel():
    logger = getlogger()
    logger.level = logging.NOTSET
