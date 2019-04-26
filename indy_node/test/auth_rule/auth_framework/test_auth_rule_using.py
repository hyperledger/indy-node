import dateutil.tz
import pytest
from datetime import datetime, timedelta

from indy_node.test.upgrade.conftest import patch_packet_mgr_output, EXT_PKT_NAME, EXT_PKT_VERSION

from indy_common.authorize.auth_constraints import IDENTITY_OWNER
from indy_common.constants import TRUST_ANCHOR, START
from indy_node.test.auth_rule.auth_framework.add_roles import AddNewTrusteeTest, AddNewStewardTest, \
    AddNewTrustAnchorTest, AddNewNetworkMonitorTest, AddNewIdentityOwnerTest
from indy_node.test.auth_rule.auth_framework.claim_def import ClaimDefTest
from indy_node.test.auth_rule.auth_framework.key_rotation import RotateKeyTest
from indy_node.test.auth_rule.auth_framework.schema import SchemaTest
from indy_node.test.auth_rule.auth_framework.upgrade import UpgradeTest
from indy_node.test.upgrade.helper import bumpedVersion
from plenum.common.constants import STEWARD, TRUSTEE, \
    IDENTITY_OWNER
from indy_common.authorize import auth_map
from plenum.test.helper import randomText
from plenum.test.testing_utils import FakeSomething


class TestAuthRuleUsing():
    map_of_tests = {
        auth_map.add_new_trustee.get_action_id(): AddNewTrusteeTest,
        auth_map.add_new_steward.get_action_id(): AddNewStewardTest,
        auth_map.add_new_trust_anchor.get_action_id(): AddNewTrustAnchorTest,
        auth_map.add_new_network_monitor.get_action_id(): AddNewNetworkMonitorTest,
        auth_map.add_new_identity_owner.get_action_id(): AddNewIdentityOwnerTest,
        auth_map.key_rotation.get_action_id(): RotateKeyTest,
        auth_map.add_schema.get_action_id(): SchemaTest,
        auth_map.add_schema.get_action_id(): ClaimDefTest,
        auth_map.start_upgrade.get_action_id(): UpgradeTest,
    }

    @pytest.fixture(scope='module')
    def pckg(self):
        return (EXT_PKT_NAME, EXT_PKT_VERSION)

    @pytest.fixture(scope='module')
    def monkeymodule(self):
        from _pytest.monkeypatch import MonkeyPatch
        mpatch = MonkeyPatch()
        yield mpatch
        mpatch.undo()

    @pytest.fixture(scope='module')
    def validUpgrade(self, nodeIds, tconf, pckg, monkeymodule):
        schedule = {}
        unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        startAt = unow + timedelta(seconds=100)
        acceptableDiff = tconf.MinSepBetweenNodeUpgrades + 1
        for i in nodeIds:
            schedule[i] = datetime.isoformat(startAt)
            startAt = startAt + timedelta(seconds=acceptableDiff + 3)

        new_version = bumpedVersion(pckg[1])
        patch_packet_mgr_output(monkeymodule, pckg[0], pckg[1], new_version)

        return dict(name='upgrade-{}'.format(randomText(3)), version=new_version,
                    action=START, schedule=schedule, timeout=1, package=pckg[0],
                    sha256='db34a72a90d026dae49c3b3f0436c8d3963476c77468ad955845a1ccf7b03f55')

    @pytest.fixture(scope="module")
    def env(self,
            looper,
            sdk_pool_handle,
            sdk_wallet_trustee,
            sdk_wallet_steward,
            sdk_wallet_trust_anchor,
            sdk_wallet_client,
            validUpgrade):
        role_to_wallet = {
            TRUSTEE: sdk_wallet_trustee,
            STEWARD: sdk_wallet_steward,
            TRUST_ANCHOR: sdk_wallet_trust_anchor,
            IDENTITY_OWNER: sdk_wallet_client,
        }
        return FakeSomething(looper=looper,
                             sdk_pool_handle=sdk_pool_handle,
                             sdk_wallet_trustee=sdk_wallet_trustee,
                             sdk_wallet_steward=sdk_wallet_steward,
                             sdk_wallet_client=sdk_wallet_client,
                             role_to_wallet=role_to_wallet,
                             valid_upgrade=validUpgrade)

    @pytest.fixture(scope='module', params=[(k, v) for k, v in map_of_tests.items()])
    def auth_rule_tests(self, request, env):
        action_id, test_cls = request.param
        test = test_cls(env)
        return action_id, test

    def test_auth_rule_using(self, auth_rule_tests):
        descr, test = auth_rule_tests
        print("Running test: {}".format(descr))
        test.prepare()
        test.run()
        test.result()
