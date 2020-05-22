import logging
import time
import warnings
import pytest

from common.serializers import serialization
from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_map import auth_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.test.constants import IDENTIFIERS
from indy_node.persistence.attribute_store import AttributeStore
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.node import Node
from indy_node.server.node_bootstrap import NodeBootstrap
from ledger.compact_merkle_tree import CompactMerkleTree
from plenum.bls.bls_store import BlsStore
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.ledger import Ledger
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_managers.action_request_manager import ActionRequestManager
from plenum.server.request_managers.read_request_manager import ReadRequestManager
from plenum.server.request_managers.write_request_manager import WriteRequestManager
from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_pool_refresh, prepare_new_node_data, \
    create_and_start_new_node, prepare_node_request, sdk_sign_and_send_prepared_request
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from storage.kv_in_memory import KeyValueStorageInMemory
from stp_core.common.log import Logger

from plenum.common.util import randomString
from plenum.common.constants import VALIDATOR, STEWARD_STRING, POOL_LEDGER_ID, DOMAIN_LEDGER_ID, IDR_CACHE_LABEL, \
    ATTRIB_LABEL, TRUSTEE, STEWARD, KeyValueStorageType, BLS_LABEL, TRUSTEE_STRING
from plenum.test.helper import sdk_get_and_check_replies, waitForViewChange
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir as plenum_tdir, nodeReg, \
    whitelist, concerningLogLevels, logcapture, \
    tdirWithPoolTxns, tdirWithDomainTxns, \
    txnPoolNodeSet, \
    poolTxnData, dirName, poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    patchPluginManager, txnPoolNodesLooper, warncheck, \
    warnfilters as plenum_warnfilters, do_post_node_creation

# noinspection PyUnresolvedReferences
from plenum.test.conftest import sdk_pool_handle as plenum_pool_handle, sdk_pool_data, sdk_wallet_steward, \
    sdk_wallet_handle, sdk_wallet_data, sdk_steward_seed, sdk_wallet_client, sdk_wallet_trustee, \
    sdk_trustee_seed, trustee_data, sdk_client_seed, poolTxnClientData, poolTxnClientNames, \
    sdk_wallet_stewards, create_node_and_not_start, sdk_wallet_handle, sdk_wallet_new_client, sdk_new_client_seed

from indy_common import strict_types
from indy_common.constants import APP_NAME, CONFIG_LEDGER_ID, CONFIG_LEDGER_AUTH_POLICY, NETWORK_MONITOR, ENDORSER
from indy_common.config_helper import NodeConfigHelper

# noinspection PyUnresolvedReferences
from indy_common.test.conftest import general_conf_tdir, tconf as _tconf, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper, setTestLogLevel, node_config_helper_class, config_helper_class

from indy_node.test.helper import TestNode, TestNodeBootstrap

from indy_node.server.upgrader import Upgrader
from indy_node.utils.node_control_utils import NodeControlUtil

from indy_node.test.upgrade.helper import releaseVersion

# typecheck during tests
strict_types.defaultShouldCheck = True

Logger.setLogLevel(logging.NOTSET)


@pytest.fixture(scope="module")
def tconf(_tconf):
    oldMax3PCBatchSize = _tconf.Max3PCBatchSize
    _tconf.Max3PCBatchSize = 1
    yield _tconf
    _tconf.Max3PCBatchSize = oldMax3PCBatchSize

@pytest.fixture(scope='module')
def sdk_pool_handle(plenum_pool_handle, nodeSet):
    return plenum_pool_handle


@pytest.fixture(scope="session")
def warnfilters():
    def _():
        warnings.filterwarnings(
            'ignore',
            category=DeprecationWarning,
            module='indy_common\.persistence\.identity_graph',
            message="The 'warn' method is deprecated")
        warnings.filterwarnings(
            'ignore', category=ResourceWarning, message='unclosed transport')

    return _


@pytest.fixture(scope='module')
def sdk_node_theta_added(looper,
                         txnPoolNodeSet,
                         tdir,
                         tconf,
                         sdk_pool_handle,
                         sdk_wallet_trustee,
                         allPluginsPath,
                         node_config_helper_class,
                         testNodeClass,
                         name=None,
                         services=[VALIDATOR]):
    new_steward_name = "testClientSteward" + randomString(3)
    new_node_name = name or "Theta"

    new_steward_wallet = sdk_add_new_nym(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         alias=new_steward_name,
                                         role=STEWARD_STRING)

    sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort, key_proof = \
        prepare_new_node_data(tconf, tdir, new_node_name,
                              configClass=node_config_helper_class)

    # filling node request
    _, steward_did = new_steward_wallet
    node_request = looper.loop.run_until_complete(
        prepare_node_request(steward_did,
                             new_node_name=new_node_name,
                             clientIp=clientIp,
                             clientPort=clientPort,
                             nodeIp=nodeIp,
                             nodePort=nodePort,
                             bls_key=bls_key,
                             sigseed=sigseed,
                             services=services,
                             key_proof=key_proof))

    # sending request using 'sdk_' functions
    request_couple = sdk_sign_and_send_prepared_request(looper, new_steward_wallet,
                                                        sdk_pool_handle, node_request)

    # waitng for replies
    sdk_get_and_check_replies(looper, [request_couple])

    new_node = create_and_start_new_node(looper, new_node_name, tdir, sigseed,
                                         (nodeIp, nodePort), (clientIp, clientPort),
                                         tconf, True, allPluginsPath,
                                         testNodeClass,
                                         configClass=node_config_helper_class)

    if services == [VALIDATOR]:
        txnPoolNodeSet.append(new_node)
        looper.run(checkNodesConnected(txnPoolNodeSet))
    sdk_pool_refresh(looper, sdk_pool_handle)
    return new_steward_wallet, new_node


@pytest.fixture(scope="module")
def sdk_wallet_endorser(looper, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                           alias='TA-1', role='ENDORSER')


@pytest.fixture(scope="module")
def sdk_user_wallet_a(nodeSet, sdk_wallet_endorser,
                      sdk_pool_handle, looper):
    return sdk_add_new_nym(looper, sdk_pool_handle,
                           sdk_wallet_endorser, alias='userA',
                           skipverkey=True)


# patch that makes sense in general for tests
# since '_get_curr_info' relies on OS package manager
@pytest.fixture(scope="module")
def patchNodeControlUtil():
    old__get_curr_info = getattr(NodeControlUtil, '_get_curr_info')

    @classmethod
    def _get_curr_info(cls, package):
        from stp_core.common.log import getlogger
        import os
        logger = getlogger()
        if package == APP_NAME:
            return (
                "Package: {}\nStatus: install ok installed\nPriority: extra\nSection: default\n"
                "Installed-Size: 21\nMaintainer: maintainer\nArchitecture: amd64\nVersion: {}\n"
            ).format(APP_NAME, releaseVersion())

        raise ValueError("Only {} is expected, got: {}".format(APP_NAME, package))

    setattr(NodeControlUtil, '_get_curr_info', _get_curr_info)
    yield
    setattr(NodeControlUtil, '_get_curr_info', old__get_curr_info)


# link patching with tdir as the most common fixture to make the patch
# applied regardless usage of the pool (there are cases when node control
# is tested without pool creation)
@pytest.fixture(scope="module")
def tdir(patchNodeControlUtil, plenum_tdir):
    return plenum_tdir


@pytest.fixture(scope="module")
def nodeSet(txnPoolNodeSet):
    return txnPoolNodeSet


@pytest.fixture(scope="module")
def testNodeClass():
    return TestNode


@pytest.fixture(scope="module")
def testNodeBootstrapClass():
    return TestNodeBootstrap


@pytest.fixture(scope="module")
def newNodeAdded(looper, nodeSet, tdir, tconf, sdk_pool_handle,
                 sdk_wallet_trustee, allPluginsPath):
    view_no = nodeSet[0].viewNo
    new_steward_wallet, new_node = sdk_node_theta_added(looper,
                                                        nodeSet,
                                                        tdir,
                                                        tconf,
                                                        sdk_pool_handle,
                                                        sdk_wallet_trustee,
                                                        allPluginsPath,
                                                        node_config_helper_class=NodeConfigHelper,
                                                        testNodeClass=TestNode,
                                                        name='')
    waitForViewChange(looper=looper, txnPoolNodeSet=nodeSet,
                      expectedViewNo=view_no + 1)
    ensureElectionsDone(looper=looper, nodes=nodeSet)
    return new_steward_wallet, new_node


@pytest.fixture(scope='module')
def nodeIds(nodeSet):
    return next(iter(nodeSet)).poolManager.nodeIds


@pytest.fixture(scope="module")
def pool_ledger(tconf, tmpdir_factory):
    tdir = tmpdir_factory.mktemp('').strpath
    return Ledger(CompactMerkleTree(),
                  dataDir=tdir)


@pytest.fixture(scope="module")
def domain_ledger(tconf, tmpdir_factory):
    tdir = tmpdir_factory.mktemp('').strpath
    return Ledger(CompactMerkleTree(),
                  dataDir=tdir)


@pytest.fixture(scope="module")
def config_ledger(tconf, tmpdir_factory):
    tdir = tmpdir_factory.mktemp('').strpath
    return Ledger(CompactMerkleTree(),
                  dataDir=tdir)


@pytest.fixture(scope="module")
def config_state():
    return PruningState(KeyValueStorageInMemory())


@pytest.fixture(scope="module")
def domain_state():
    return PruningState(KeyValueStorageInMemory())


@pytest.fixture(scope="module")
def pool_state():
    return PruningState(KeyValueStorageInMemory())


@pytest.fixture(scope="module")
def idr_cache_store(idr_cache):
    return idr_cache


@pytest.fixture(scope="module")
def attrib_store():
    return AttributeStore(KeyValueStorageInMemory())


@pytest.fixture(scope="module")
def bls_store():
    return BlsStore(key_value_type=KeyValueStorageType.Memory,
                    data_location=None,
                    key_value_storage_name="BlsInMemoryStore",
                    serializer=serialization.multi_sig_store_serializer)


@pytest.fixture(scope='module')
def idr_cache():
    cache = IdrCache("Cache",
                     KeyValueStorageInMemory())
    i = 0

    for id in IDENTIFIERS[TRUSTEE]:
        i += 1
        cache.set(id, i, int(time.time()), role=TRUSTEE,
                  verkey="trustee_identifier_verkey", isCommitted=False)

    for id in IDENTIFIERS[STEWARD]:
        i += 1
        cache.set(id, i, int(time.time()), role=STEWARD,
                  verkey="steward_identifier_verkey", isCommitted=False)

    for id in IDENTIFIERS[ENDORSER]:
        i += 1
        cache.set(id, i, int(time.time()), role=ENDORSER,
                  verkey="endorser_identifier_verkey", isCommitted=False)

    for id in IDENTIFIERS[NETWORK_MONITOR]:
        i += 1
        cache.set(id, i, int(time.time()), role=NETWORK_MONITOR,
                  verkey="network_monitor_identifier_verkey", isCommitted=False)

    for id in IDENTIFIERS["OtherRole"]:
        i += 1
        cache.set(id, i, int(time.time()), role='OtherRole',
                  verkey="other_verkey", isCommitted=False)

    for id in IDENTIFIERS[None]:
        i += 1
        cache.set(id, i, int(time.time()), role=None,
                  verkey="identity_owner_verkey", isCommitted=False)

    return cache


@pytest.fixture(scope="module")
def constraint_serializer():
    return ConstraintsSerializer(domain_state_serializer)


@pytest.fixture(scope='module')
def write_auth_req_validator(idr_cache,
                             constraint_serializer,
                             config_state):
    validator = WriteRequestValidator(config=FakeSomething(authPolicy=CONFIG_LEDGER_AUTH_POLICY),
                                      auth_map=auth_map,
                                      cache=idr_cache,
                                      config_state=config_state,
                                      state_serializer=constraint_serializer)
    return validator


@pytest.fixture(scope="module")
def db_manager(pool_state, domain_state, config_state,
               pool_ledger, domain_ledger, config_ledger,
               idr_cache_store,
               attrib_store,
               bls_store):
    dbm = DatabaseManager()
    dbm.register_new_database(POOL_LEDGER_ID, pool_ledger, pool_state)
    dbm.register_new_database(DOMAIN_LEDGER_ID, domain_ledger, domain_state)
    dbm.register_new_database(CONFIG_LEDGER_ID, config_ledger, config_state)
    dbm.register_new_store(IDR_CACHE_LABEL, idr_cache_store)
    dbm.register_new_store(ATTRIB_LABEL, attrib_store)
    dbm.register_new_store(BLS_LABEL, bls_store)
    return dbm


@pytest.fixture(scope="module")
def fake_pool_cfg():
    return FakeSomething()


@pytest.fixture(scope="module")
def fake_upgrader():
    return FakeSomething()


@pytest.fixture(scope="module")
def fake_restarter():
    return FakeSomething()


@pytest.fixture(scope="module")
def fake_pool_manager():
    return FakeSomething()


@pytest.fixture(scope="module")
def fake_node(db_manager, fake_pool_cfg, fake_upgrader, fake_restarter, fake_pool_manager):
    wm = WriteRequestManager(database_manager=db_manager)
    rm = ReadRequestManager()
    am = ActionRequestManager()
    return FakeSomething(name="fake_node",
                         dataLocation="//place_that_cannot_exist",
                         genesis_dir="//place_that_cannot_exist",
                         ledger_ids=Node.ledger_ids,
                         write_manager=wm,
                         read_manager=rm,
                         action_manager=am,
                         db_manager=db_manager,
                         write_req_validator=write_auth_req_validator,
                         config=FakeSomething(
                             stewardThreshold=20,
                             poolTransactionsFile="//pool_genesis_that_cannot_exist",
                             domainTransactionsFile="//domain_genesis_that_cannot_exist"
                         ),
                         poolCfg=fake_pool_cfg,
                         upgrader=fake_upgrader,
                         restarter=fake_restarter,
                         poolManager=fake_pool_manager)


@pytest.fixture(scope="module")
def _managers(write_auth_req_validator,
              fake_node):
    nbs = TestNodeBootstrap(fake_node)
    nbs._register_domain_req_handlers()
    nbs._register_domain_batch_handlers()
    nbs._register_config_req_handlers()
    nbs._register_config_batch_handlers()
    return fake_node.write_manager, fake_node.read_manager


@pytest.fixture(scope="module")
def write_manager(_managers):
    return _managers[0]


@pytest.fixture(scope="module")
def read_manager(_managers):
    return _managers[1]


@pytest.fixture(scope='module')
def write_request_validation(write_auth_req_validator):
    def wrapped(*args, **kwargs):
        try:
            write_auth_req_validator.validate(*args, **kwargs)
        except UnauthorizedClientRequest:
            return False
        return True

    return wrapped


@pytest.fixture(scope='module')
def sdk_wallet_trustee_list(looper,
                            sdk_wallet_trustee,
                            sdk_pool_handle):
    sdk_wallet_trustee_list = []
    for i in range(3):
        wallet = sdk_add_new_nym(looper,
                                 sdk_pool_handle,
                                 sdk_wallet_trustee,
                                 alias='trustee{}'.format(i),
                                 role=TRUSTEE_STRING)
        sdk_wallet_trustee_list.append(wallet)
    return sdk_wallet_trustee_list
