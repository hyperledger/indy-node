from copy import deepcopy

from datetime import datetime, timedelta

import dateutil
import dateutil.tz

from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent


def test_pool_upgrade_same_time_different_days(looper, tconf, nodeSet,
                                               validUpgrade, sdk_pool_handle,
                                               sdk_wallet_trustee, nodeIds):
    day_in_sec = 24 * 60 * 60
    upgr1 = deepcopy(validUpgrade)
    schedule = {}
    unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
    startAt = unow + timedelta(seconds=day_in_sec)
    for i in nodeIds:
        schedule[i] = datetime.isoformat(startAt)
        startAt = startAt + timedelta(seconds=day_in_sec)
    upgr1['schedule'] = schedule

    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee, upgr1)
