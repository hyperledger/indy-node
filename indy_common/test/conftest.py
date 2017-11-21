import os
import shutil
import pytest
import logging

from indy_common import strict_types
from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields
from stp_core.common.log import getlogger

# typecheck during tests
strict_types.defaultShouldCheck = True

# noinspection PyUnresolvedReferences
from indy_common.config import GENERAL_CONFIG_FILE
from plenum.test.conftest import tdir, tdir_for_func, GENERAL_CONFIG_DIR, \
    txnPoolNodesLooper, overriddenConfigValues  # noqa
from indy_common.config_helper import ConfigHelper, NodeConfigHelper

import indy_node.user_config.user_config as user_config
import indy_node.user_config.ubuntu_platform_config as platform_config


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

    general_config_file = open(user_config.__file__, 'r')
    platform_config_file = open(platform_config.__file__, 'r')

    general_config_result_file = open(general_config_path, 'w')

    lines = general_config_file.readlines()
    for line in lines:
        if line.startswith('NETWORK_NAME'):
            line = 'NETWORK_NAME = \'sandbox\''
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


def _tconf(general_config):
    config = getConfig(general_config_dir=general_config)
    for k, v in overriddenConfigValues.items():
        setattr(config, k, v)

    #config.baseDir = tdir
    #config.CLI_BASE_DIR = tdir
    config.MinSepBetweenNodeUpgrades = 5

    return config


@pytest.fixture(scope="module")
def tconf(general_conf_tdir):
    return _tconf(general_conf_tdir)

def test_asdf(tconf):
    pass

@pytest.fixture()
def tconf_for_func(general_conf_tdir_for_func):
    return _tconf(general_conf_tdir_for_func)


#@pytest.fixture(scope="module")
#def conf(tdir):
#    return getConfig(tdir)


#@pytest.fixture(scope="module")
#def tconf(conf, tdir):
#    conf.baseDir = tdir
#    conf.CLI_BASE_DIR = tdir
#    conf.MinSepBetweenNodeUpgrades = 5
#    return conf


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
