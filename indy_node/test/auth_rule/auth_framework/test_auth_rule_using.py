import pytest

from indy_common.authorize.auth_constraints import IDENTITY_OWNER
from indy_common.constants import TRUST_ANCHOR, NETWORK_MONITOR, NETWORK_MONITOR_STRING
from indy_node.test.auth_rule.auth_framework.add_roles import AddNewTrusteeTest, AddNewStewardTest, \
    AddNewTrustAnchorTest, AddNewNetworkMonitorTest, AddNewIdentityOwnerTest
from indy_node.test.auth_rule.auth_framework.edit_roles import EditTrusteeToStewardTest, \
    EditTrusteeToTrustAnchorTest, EditTrusteeToNetworkMonitorTest, EditTrusteeToIdentityOwnerTest, \
    EditTrusteeToTrusteeTest, EditStewardToTrusteeTest, EditStewardToTrustAnchorTest, EditStewardToNetworkMonitorTest, \
    EditStewardToIdentityOwnerTest, EditTrustAnchorToTrusteeTest, EditTrustAnchorToStewardTest, \
    EditTrustAnchorToIdentityOwnerTest, EditTrustAnchorToNetworkMonitorTest, EditIdentityOwnerToNetworkMonitorTest, \
    EditIdentityOwnerToTrusteeTest, EditIdentityOwnerToTrustAnchorTest, EditIdentityOwnerToStewardTest, \
    EditNetworkMonitorToIdentityOwnerTest, EditNetworkMonitorToTrusteeTest, EditNetworkMonitorToStewardTest, \
    EditNetworkMonitorToTrustAnchorTest
from indy_node.test.auth_rule.auth_framework.key_rotation import RotateKeyTest
from plenum.common.constants import STEWARD, TRUSTEE, \
    IDENTITY_OWNER
from indy_common.authorize import auth_map
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.testing_utils import FakeSomething


class TestAuthRuleUsing():
    map_of_tests = {
        auth_map.add_new_trustee.get_action_id(): AddNewTrusteeTest,
        auth_map.add_new_steward.get_action_id(): AddNewStewardTest,
        auth_map.add_new_trust_anchor.get_action_id(): AddNewTrustAnchorTest,
        auth_map.add_new_network_monitor.get_action_id(): AddNewNetworkMonitorTest,
        auth_map.add_new_identity_owner.get_action_id(): AddNewIdentityOwnerTest,
        auth_map.key_rotation.get_action_id(): RotateKeyTest,
        auth_map.edit_role_actions[TRUSTEE][STEWARD].get_action_id(): EditTrusteeToStewardTest,
        auth_map.edit_role_actions[TRUSTEE][TRUST_ANCHOR].get_action_id(): EditTrusteeToTrustAnchorTest,
        auth_map.edit_role_actions[TRUSTEE][NETWORK_MONITOR].get_action_id(): EditTrusteeToNetworkMonitorTest,
        auth_map.edit_role_actions[TRUSTEE][IDENTITY_OWNER].get_action_id(): EditTrusteeToIdentityOwnerTest,
        auth_map.edit_role_actions[STEWARD][TRUSTEE].get_action_id(): EditStewardToTrusteeTest,
        auth_map.edit_role_actions[STEWARD][TRUST_ANCHOR].get_action_id(): EditStewardToTrustAnchorTest,
        auth_map.edit_role_actions[STEWARD][NETWORK_MONITOR].get_action_id(): EditStewardToNetworkMonitorTest,
        auth_map.edit_role_actions[STEWARD][IDENTITY_OWNER].get_action_id(): EditStewardToIdentityOwnerTest,
        auth_map.edit_role_actions[TRUST_ANCHOR][TRUSTEE].get_action_id(): EditTrustAnchorToTrusteeTest,
        auth_map.edit_role_actions[TRUST_ANCHOR][STEWARD].get_action_id(): EditTrustAnchorToStewardTest,
        auth_map.edit_role_actions[TRUST_ANCHOR][NETWORK_MONITOR].get_action_id(): EditTrustAnchorToNetworkMonitorTest,
        auth_map.edit_role_actions[TRUST_ANCHOR][IDENTITY_OWNER].get_action_id(): EditTrustAnchorToIdentityOwnerTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][TRUSTEE].get_action_id(): EditIdentityOwnerToTrusteeTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][STEWARD].get_action_id(): EditIdentityOwnerToStewardTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][TRUST_ANCHOR].get_action_id(): EditIdentityOwnerToTrustAnchorTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][NETWORK_MONITOR].get_action_id(): EditIdentityOwnerToNetworkMonitorTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][TRUSTEE].get_action_id(): EditNetworkMonitorToTrusteeTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][STEWARD].get_action_id(): EditNetworkMonitorToStewardTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][TRUST_ANCHOR].get_action_id(): EditNetworkMonitorToTrustAnchorTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][IDENTITY_OWNER].get_action_id(): EditNetworkMonitorToIdentityOwnerTest,
    }

    @pytest.fixture(scope="module")
    def sdk_wallet_network_monitor(self, looper, sdk_pool_handle, sdk_wallet_trustee):
        return sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                               alias='NM-1', role=NETWORK_MONITOR_STRING)

    @pytest.fixture(scope="module")
    def env(self,
            looper,
            sdk_pool_handle,
            sdk_wallet_trustee,
            sdk_wallet_steward,
            sdk_wallet_trust_anchor,
            sdk_wallet_client,
            sdk_wallet_network_monitor):
        role_to_wallet = {
            TRUSTEE: sdk_wallet_trustee,
            STEWARD: sdk_wallet_steward,
            TRUST_ANCHOR: sdk_wallet_trust_anchor,
            NETWORK_MONITOR: sdk_wallet_network_monitor,
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
        test = test_cls(env, action_id)
        return action_id, test

    def test_auth_rule_using(self, auth_rule_tests):
        descr, test = auth_rule_tests
        print("Running test: {}".format(descr))
        test.prepare()
        test.run()
        test.result()
