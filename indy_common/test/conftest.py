#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import pytest
import logging

from indy_common import strict_types
from indy_common.config_util import getConfig
from indy_common.txn_util import getTxnOrderedFields
from stp_core.common.log import getlogger

# typecheck during tests
strict_types.defaultShouldCheck = True

# noinspection PyUnresolvedReferences
from plenum.test.conftest import txnPoolNodesLooper  # noqa


@pytest.fixture(scope="module")
def conf(tdir):
    return getConfig(tdir)


@pytest.fixture(scope="module")
def tconf(conf, tdir):
    conf.baseDir = tdir
    conf.CLI_BASE_DIR = tdir
    conf.MinSepBetweenNodeUpgrades = 5
    return conf


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
