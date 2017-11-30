import os
import pytest
import logging

from indy_common import strict_types
from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields
from stp_core.common.log import getlogger
from indy_common.config import GENERAL_CONFIG_FILE
from indy_common.config_helper import ConfigHelper, NodeConfigHelper
import indy_node.general_config.general_config as general_config
import indy_node.general_config.ubuntu_platform_config as platform_config

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


def _general_conf_tdir(tmp_dir):
    general_config_dir = os.path.join(tmp_dir, GENERAL_CONFIG_DIR)
    os.makedirs(general_config_dir)
    general_config_path = os.path.join(general_config_dir, GENERAL_CONFIG_FILE)

    general_config_file = open(general_config.__file__, 'r')
    platform_config_file = open(platform_config.__file__, 'r')

    general_config_result_file = open(general_config_path, 'w')

    lines = general_config_file.readlines()
    for line in lines:
        if line.startswith('NETWORK_NAME'):
            line = 'NETWORK_NAME = \'sandbox\'\n'
        general_config_result_file.write(line)
    general_config_result_file.write(platform_config_file.read())

    general_config_file.close()
    platform_config_file.close()
    general_config_result_file.close()

    return general_config_dir


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


def _tconf(general_config, client_temp_dir):
    config = getConfig(general_config_dir=general_config)
    for k, v in overriddenConfigValues.items():
        setattr(config, k, v)
    config.MinSepBetweenNodeUpgrades = 5
    config.CLI_BASE_DIR = client_temp_dir
    config.CLI_NETWORK_DIR = os.path.join(config.CLI_BASE_DIR, 'networks')
    return config


@pytest.fixture(scope="module")
def tconf(general_conf_tdir, client_tdir):
    return _tconf(general_conf_tdir, client_tdir)


@pytest.fixture()
def tconf_for_func(general_conf_tdir_for_func, client_tdir):
    return _tconf(general_conf_tdir_for_func, client_tdir)


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
