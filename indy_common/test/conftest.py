import os
import pytest
import logging

from indy_common import strict_types
from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields
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


def _general_conf_tdir(tmp_dir):
    return create_config_dirs(tmp_dir)


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
