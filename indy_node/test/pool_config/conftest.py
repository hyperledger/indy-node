import pytest

from plenum.common.constants import STEWARD

from indy_common.constants import START, FORCE
from indy_node.test import waits
from indy_node.test.pool_config.helper import ensurePoolConfigSent
from indy_client.test.helper import getClientAddedWithRole
from stp_core.loop.eventually import eventually


def genPoolConfig(writes: bool, force: bool):
    return dict(writes=writes, force=force)


@pytest.fixture(scope='module')
def poolConfigWTFF():
    return genPoolConfig(writes=True, force=False)


@pytest.fixture(scope='module')
def poolConfigWFFF():
    return genPoolConfig(writes=False, force=False)


@pytest.fixture(scope='module')
def poolConfigWTFT():
    return genPoolConfig(writes=True, force=True)


@pytest.fixture(scope='module')
def poolConfigWFFT():
    return genPoolConfig(writes=False, force=True)


@pytest.fixture(scope="module")
def poolConfigSent(looper, nodeSet, trustee, trusteeWallet, poolCfg):
    ensurePoolConfigSent(looper, trustee, trusteeWallet, poolCfg)
