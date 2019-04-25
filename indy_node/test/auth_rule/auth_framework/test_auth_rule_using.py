import pytest

from indy_common.authorize.auth_constraints import IDENTITY_OWNER
from indy_common.constants import TRUST_ANCHOR
from indy_node.test.auth_rule.auth_framework.add_roles import AddNewTrusteeTest, AddNewStewardTest, \
    AddNewTrustAnchorTest, AddNewNetworkMonitorTest, AddNewIdentityOwnerTest
from indy_node.test.auth_rule.auth_framework.claim_def import ClaimDefTest
from indy_node.test.auth_rule.auth_framework.key_rotation import RotateKeyTest
from indy_node.test.auth_rule.auth_framework.schema import SchemaTest
from plenum.common.constants import STEWARD, TRUSTEE, \
    IDENTITY_OWNER
from indy_common.authorize import auth_map
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
    }

    @pytest.fixture(scope="module")
    def env(self,
            looper,
            sdk_pool_handle,
            sdk_wallet_trustee,
            sdk_wallet_steward,
            sdk_wallet_trust_anchor,
            sdk_wallet_client):
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
                             role_to_wallet=role_to_wallet)

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
