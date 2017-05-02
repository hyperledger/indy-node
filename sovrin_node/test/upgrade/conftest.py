from datetime import datetime, timedelta

import dateutil.tz
import pytest

from sovrin_common.constants import START
from sovrin_node.test.upgrade.helper import bumpedVersion


@pytest.fixture(scope='module')
def nodeIds(nodeSet):
    return nodeSet[0].poolManager.nodeIds


@pytest.fixture(scope='module')
def validUpgrade(nodeIds, tconf):
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=30)
    acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=acceptableDiff + 3)
    # TODO select or create a timeout from 'waits' if it is needed
    return dict(name='upgrade-13', version=bumpedVersion(), action=START,
                schedule=schedule, sha256='aad1242', timeout=1)
