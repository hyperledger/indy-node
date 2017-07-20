import pytest
import logging

from sovrin_common import strict_types
from sovrin_common.config_util import getConfig
from sovrin_common.txn_util import getTxnOrderedFields
from stp_core.common.log import getlogger

# typecheck during tests
strict_types.defaultShouldCheck = True

# noinspection PyUnresolvedReferences
from plenum.test.conftest import txnPoolNodesLooper


@pytest.fixture(scope="module")
def conf(tdir):
    return getConfig(tdir)


@pytest.fixture(scope="module")
def tconf(conf, tdir):
    conf.baseDir = tdir
    conf.MinSepBetweenNodeUpgrades = 5
    return conf


@pytest.fixture(scope="module")
def poolTxnTrusteeNames():
    return "Trustee1",


@pytest.fixture(scope="module")
def looper(txnPoolNodesLooper):
    return txnPoolNodesLooper


@pytest.fixture(scope="module")
def domainTxnOrderedFields():
    return getTxnOrderedFields()


@pytest.fixture(autouse=True)
def setTestLogLevel():
    logger = getlogger()
    logger.level = logging.NOTSET
