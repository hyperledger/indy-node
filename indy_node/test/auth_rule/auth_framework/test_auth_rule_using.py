import dateutil.tz
import pytest
from datetime import datetime, timedelta
from collections import OrderedDict

from plenum.common.constants import STEWARD, TRUSTEE, IDENTITY_OWNER

from indy_common.constants import (
    ENDORSER, START, NETWORK_MONITOR, NETWORK_MONITOR_STRING
)
from indy_common.authorize import auth_map

from plenum.test.helper import randomText
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.testing_utils import FakeSomething

from indy_node.test.auth_rule.auth_framework.claim_def import AddClaimDefTest, EditClaimDefTest
from indy_node.test.auth_rule.auth_framework.add_roles import AddNewTrusteeTest, AddNewStewardTest, \
    AddNewEndorserTest, AddNewNetworkMonitorTest, AddNewIdentityOwnerTest
from indy_node.test.auth_rule.auth_framework.edit_roles import EditTrusteeToStewardTest, \
    EditTrusteeToEndorserTest, EditTrusteeToNetworkMonitorTest, EditTrusteeToIdentityOwnerTest, \
    EditStewardToTrusteeTest, EditStewardToEndorserTest, EditStewardToNetworkMonitorTest, \
    EditStewardToIdentityOwnerTest, EditEndorserToTrusteeTest, EditEndorserToStewardTest, \
    EditEndorserToIdentityOwnerTest, EditEndorserToNetworkMonitorTest, EditIdentityOwnerToNetworkMonitorTest, \
    EditIdentityOwnerToTrusteeTest, EditIdentityOwnerToEndorserTest, EditIdentityOwnerToStewardTest, \
    EditNetworkMonitorToIdentityOwnerTest, EditNetworkMonitorToTrusteeTest, EditNetworkMonitorToStewardTest, \
    EditNetworkMonitorToEndorserTest, EditStewardToStewardTest, EditTrusteeToTrusteeTest, \
    EditEndorserToEndorserTest, EditNetworkMonitorToNetworkMonitorTest, EditIdentityOwnerToIdentityOwnerTest
from indy_node.test.auth_rule.auth_framework.key_rotation import RotateKeyTest
from indy_node.test.auth_rule.auth_framework.schema import SchemaTest
from indy_node.test.auth_rule.auth_framework.upgrade import StartUpgradeTest, CancelUpgradeTest
from indy_node.test.upgrade.helper import bumpedVersion
from indy_node.test.auth_rule.auth_framework.add_attrib import AddAttribTest
from indy_node.test.auth_rule.auth_framework.edit_attrib import EditAttribTest
from indy_node.test.auth_rule.auth_framework.edit_auth_rules import AuthRulesTest
from indy_node.test.auth_rule.auth_framework.edit_auth_rule import AuthRuleTest
from indy_node.test.auth_rule.auth_framework.node_services import AddNewNodeTest, AddNewNodeEmptyServiceTest, \
    DemoteNodeTest, PromoteNodeTest
from indy_node.test.auth_rule.auth_framework.node_properties import EditNodeIpTest, EditNodePortTest, \
    EditNodeClientIpTest, EditNodeClientPortTest, EditNodeBlsTest
from indy_node.test.auth_rule.auth_framework.pool_config import PoolConfigTest
from indy_node.test.auth_rule.auth_framework.restart import RestartTest
from indy_node.test.auth_rule.auth_framework.revoc_reg_def import AddRevocRegDefTest, \
    EditRevocRegDefTest
from indy_node.test.auth_rule.auth_framework.revoc_reg_entry import AddRevocRegEntryTest, EditRevocRegEntryTest
from indy_node.test.auth_rule.auth_framework.txn_author_agreement import TxnAuthorAgreementTest
from indy_node.test.auth_rule.auth_framework.txn_author_agreement_aml import TxnAuthorAgreementAMLTest
from indy_node.test.auth_rule.auth_framework.validator_info import ValidatorInfoTest
from indy_node.test.pool_config.conftest import poolConfigWTFF
from indy_node.test.upgrade.conftest import patch_packet_mgr_output, EXT_PKT_NAME, EXT_PKT_VERSION


nodeCount = 7

from stp_core.common.log import Logger
Logger().enableStdLogging()


class TestAuthRuleUsing():
    map_of_tests = OrderedDict({
        auth_map.adding_new_node.get_action_id(): AddNewNodeTest,
        auth_map.adding_new_node_with_empty_services.get_action_id(): AddNewNodeEmptyServiceTest,
        auth_map.demote_node.get_action_id(): DemoteNodeTest,
        auth_map.promote_node.get_action_id(): PromoteNodeTest,
        auth_map.change_node_ip.get_action_id(): EditNodeIpTest,
        auth_map.change_node_port.get_action_id(): EditNodePortTest,
        auth_map.change_client_ip.get_action_id(): EditNodeClientIpTest,
        auth_map.change_client_port.get_action_id(): EditNodeClientPortTest,
        auth_map.change_bls_key.get_action_id(): EditNodeBlsTest,
        auth_map.add_new_trustee.get_action_id(): AddNewTrusteeTest,
        auth_map.add_new_steward.get_action_id(): AddNewStewardTest,
        auth_map.add_new_endorser.get_action_id(): AddNewEndorserTest,
        auth_map.add_new_network_monitor.get_action_id(): AddNewNetworkMonitorTest,
        auth_map.add_new_identity_owner.get_action_id(): AddNewIdentityOwnerTest,
        auth_map.add_attrib.get_action_id(): AddAttribTest,
        auth_map.edit_attrib.get_action_id(): EditAttribTest,
        auth_map.add_revoc_reg_def.get_action_id(): AddRevocRegDefTest,
        auth_map.edit_revoc_reg_def.get_action_id(): EditRevocRegDefTest,
        auth_map.add_revoc_reg_entry.get_action_id(): AddRevocRegEntryTest,
        auth_map.edit_revoc_reg_entry.get_action_id(): EditRevocRegEntryTest,
        auth_map.edit_role_actions[TRUSTEE][STEWARD].get_action_id(): EditTrusteeToStewardTest,
        auth_map.edit_role_actions[TRUSTEE][ENDORSER].get_action_id(): EditTrusteeToEndorserTest,
        auth_map.edit_role_actions[TRUSTEE][NETWORK_MONITOR].get_action_id(): EditTrusteeToNetworkMonitorTest,
        auth_map.edit_role_actions[TRUSTEE][IDENTITY_OWNER].get_action_id(): EditTrusteeToIdentityOwnerTest,
        auth_map.edit_role_actions[STEWARD][TRUSTEE].get_action_id(): EditStewardToTrusteeTest,
        auth_map.edit_role_actions[STEWARD][ENDORSER].get_action_id(): EditStewardToEndorserTest,
        auth_map.edit_role_actions[STEWARD][NETWORK_MONITOR].get_action_id(): EditStewardToNetworkMonitorTest,
        auth_map.edit_role_actions[STEWARD][IDENTITY_OWNER].get_action_id(): EditStewardToIdentityOwnerTest,
        auth_map.edit_role_actions[ENDORSER][TRUSTEE].get_action_id(): EditEndorserToTrusteeTest,
        auth_map.edit_role_actions[ENDORSER][STEWARD].get_action_id(): EditEndorserToStewardTest,
        auth_map.edit_role_actions[ENDORSER][NETWORK_MONITOR].get_action_id(): EditEndorserToNetworkMonitorTest,
        auth_map.edit_role_actions[ENDORSER][IDENTITY_OWNER].get_action_id(): EditEndorserToIdentityOwnerTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][TRUSTEE].get_action_id(): EditIdentityOwnerToTrusteeTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][STEWARD].get_action_id(): EditIdentityOwnerToStewardTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][ENDORSER].get_action_id(): EditIdentityOwnerToEndorserTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][NETWORK_MONITOR].get_action_id(): EditIdentityOwnerToNetworkMonitorTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][TRUSTEE].get_action_id(): EditNetworkMonitorToTrusteeTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][STEWARD].get_action_id(): EditNetworkMonitorToStewardTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][ENDORSER].get_action_id(): EditNetworkMonitorToEndorserTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][IDENTITY_OWNER].get_action_id(): EditNetworkMonitorToIdentityOwnerTest,
        auth_map.edit_role_actions[TRUSTEE][TRUSTEE].get_action_id(): EditTrusteeToTrusteeTest,
        auth_map.edit_role_actions[STEWARD][STEWARD].get_action_id(): EditStewardToStewardTest,
        auth_map.edit_role_actions[ENDORSER][ENDORSER].get_action_id(): EditEndorserToEndorserTest,
        auth_map.edit_role_actions[NETWORK_MONITOR][NETWORK_MONITOR].get_action_id(): EditNetworkMonitorToNetworkMonitorTest,
        auth_map.edit_role_actions[IDENTITY_OWNER][IDENTITY_OWNER].get_action_id(): EditIdentityOwnerToIdentityOwnerTest,
        auth_map.key_rotation.get_action_id(): RotateKeyTest,
        auth_map.txn_author_agreement_aml.get_action_id(): TxnAuthorAgreementAMLTest,
        auth_map.add_schema.get_action_id(): SchemaTest,
        auth_map.add_claim_def.get_action_id(): AddClaimDefTest,
        auth_map.edit_claim_def.get_action_id(): EditClaimDefTest,
        auth_map.start_upgrade.get_action_id(): StartUpgradeTest,
        auth_map.cancel_upgrade.get_action_id(): CancelUpgradeTest,
        auth_map.pool_restart.get_action_id(): RestartTest,
        auth_map.pool_config.get_action_id(): PoolConfigTest,
        auth_map.auth_rule.get_action_id(): AuthRuleTest,
        auth_map.auth_rules.get_action_id(): AuthRulesTest,
        auth_map.validator_info.get_action_id(): ValidatorInfoTest,
    })

    # TODO a workaround until sdk aceepts empty TAA to make possible its deactivation
    map_of_tests[auth_map.txn_author_agreement.get_action_id()] = TxnAuthorAgreementTest

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
        startAt = unow + timedelta(seconds=1000)
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
    def sdk_wallet_network_monitor(self, looper, sdk_pool_handle, sdk_wallet_trustee):
        return sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                               alias='NM-1', role=NETWORK_MONITOR_STRING)

    @pytest.fixture(scope="module")  # noqa: F811
    def env(self,
            looper,
            tconf,
            tdir,
            sdk_pool_handle,
            sdk_wallet_trustee,
            sdk_wallet_steward,
            sdk_wallet_endorser,
            sdk_wallet_client,
            validUpgrade,
            poolConfigWTFF,
            sdk_wallet_network_monitor,
            txnPoolNodeSet):
        role_to_wallet = {
            TRUSTEE: sdk_wallet_trustee,
            STEWARD: sdk_wallet_steward,
            ENDORSER: sdk_wallet_endorser,
            NETWORK_MONITOR: sdk_wallet_network_monitor,
            IDENTITY_OWNER: sdk_wallet_client,
        }
        return FakeSomething(looper=looper,
                             tconf=tconf,
                             tdir=tdir,
                             sdk_pool_handle=sdk_pool_handle,
                             sdk_wallet_trustee=sdk_wallet_trustee,
                             sdk_wallet_steward=sdk_wallet_steward,
                             sdk_wallet_client=sdk_wallet_client,
                             role_to_wallet=role_to_wallet,
                             txnPoolNodeSet=txnPoolNodeSet,
                             valid_upgrade=validUpgrade,
                             pool_config_wtff=poolConfigWTFF)

    @pytest.fixture(scope='module', params=[k for k in map_of_tests.keys()])
    def auth_rule_tests(self, request, env):
        action_id = request.param
        test_cls = self.map_of_tests[action_id]
        test = test_cls(env, action_id)
        return action_id, test

    def test_auth_rule_using(self, auth_rule_tests):
        descr, test = auth_rule_tests
        print("Running test: {}".format(descr))
        test.prepare()
        test.run()
        test.result()
        test.down()
