from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_map import auth_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import CONFIG_LEDGER_ID
from indy_node.persistence.attribute_store import AttributeStore
from indy_node.persistence.idr_cache import IdrCache
from indy_node.server.pool_config import PoolConfig
from indy_node.server.request_handlers.action_req_handlers.pool_restart_handler import PoolRestartHandler
from indy_node.server.request_handlers.action_req_handlers.validator_info_handler import ValidatorInfoHandler
from indy_node.server.request_handlers.config_batch_handler import ConfigBatchHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler import AuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rule_handler_1_9_1 import AuthRuleHandler191
from indy_node.server.request_handlers.config_req_handlers.auth_rule.auth_rules_handler import AuthRulesHandler
from indy_node.server.request_handlers.config_req_handlers.flag_handler import FlagRequestHandler
from indy_node.server.request_handlers.config_req_handlers.ledgers_freeze_handler import LedgersFreezeHandler
from indy_node.server.request_handlers.config_req_handlers.node_upgrade_handler import NodeUpgradeHandler
from indy_node.server.request_handlers.config_req_handlers.pool_config_handler import PoolConfigHandler
from indy_node.server.request_handlers.config_req_handlers.pool_upgrade_handler import PoolUpgradeHandler
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_aml_handler import \
    TxnAuthorAgreementAmlHandler
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_disable_handler import \
    TxnAuthorAgreementDisableHandler
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_handler import TxnAuthorAgreementHandler
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_handler_v1 import \
    TxnAuthorAgreementHandlerV1
from indy_node.server.request_handlers.domain_req_handlers.attribute_handler import AttributeHandler
from indy_node.server.request_handlers.domain_req_handlers.claim_def_handler import ClaimDefHandler
from indy_node.server.request_handlers.domain_req_handlers.idr_cache_nym_handler import IdrCacheNymHandler
from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_def_handler import RevocRegDefHandler
from indy_node.server.request_handlers.domain_req_handlers.revoc_reg_entry_handler import RevocRegEntryHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.json_ld_context_handler import \
    JsonLdContextHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_cred_def_handler import \
    RichSchemaCredDefHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_encoding_handler import \
    RichSchemaEncodingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_pres_def_handler import \
    RichSchemaPresDefHandler
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from indy_node.server.request_handlers.idr_cache_batch_handler import IdrCacheBatchHandler
from indy_node.server.request_handlers.pool_req_handlers.node_handler import NodeHandler
from indy_node.server.request_handlers.read_req_handlers.get_attribute_handler import GetAttributeHandler
from indy_node.server.request_handlers.read_req_handlers.get_auth_rule_handler import GetAuthRuleHandler
from indy_node.server.request_handlers.read_req_handlers.get_claim_def_handler import GetClaimDefHandler
from plenum.server.request_handlers.ledgers_freeze.get_frozen_ledgers_handler import GetFrozenLedgersHandler
from indy_node.server.request_handlers.read_req_handlers.get_flag_handler import GetFlagRequestHandler
from indy_node.server.request_handlers.read_req_handlers.get_nym_handler import GetNymHandler
from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_def_handler import GetRevocRegDefHandler
from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_delta_handler import GetRevocRegDeltaHandler
from indy_node.server.request_handlers.read_req_handlers.get_revoc_reg_handler import GetRevocRegHandler
from indy_node.server.request_handlers.read_req_handlers.rich_schema.get_rich_schema_object_by_id_handler import \
    GetRichSchemaObjectByIdHandler
from indy_node.server.request_handlers.read_req_handlers.rich_schema.get_rich_schema_object_by_metadata_handler import \
    GetRichSchemaObjectByMetadataHandler
from indy_node.server.request_handlers.read_req_handlers.get_schema_handler import GetSchemaHandler
from indy_node.server.restarter import Restarter
from indy_node.server.upgrader import Upgrader
from plenum.common.constants import IDR_CACHE_LABEL, ATTRIB_LABEL
from plenum.server.node_bootstrap import NodeBootstrap as PNodeBootstrap
from plenum.server.request_handlers.get_txn_author_agreement_aml_handler import GetTxnAuthorAgreementAmlHandler
from plenum.server.request_handlers.get_txn_author_agreement_handler import GetTxnAuthorAgreementHandler
from storage.helper import initKeyValueStorage


class NodeBootstrap(PNodeBootstrap):

    def init_idr_cache_storage(self):
        idr_cache = IdrCache(self.node.name,
                             initKeyValueStorage(self.node.config.idrCacheStorage,
                                                 self.node.dataLocation,
                                                 self.node.config.idrCacheDbName,
                                                 db_config=self.node.config.db_idr_cache_db_config)
                             )
        self.node.db_manager.register_new_store(IDR_CACHE_LABEL, idr_cache)

    def init_attribute_store(self):
        return AttributeStore(
            initKeyValueStorage(
                self.node.config.attrStorage,
                self.node.dataLocation,
                self.node.config.attrDbName,
                db_config=self.node.config.db_attr_db_config)
        )

    def init_attribute_storage(self):
        # ToDo: refactor this on pluggable handlers integration phase
        attr_store = self.init_attribute_store()
        self.node.db_manager.register_new_store(ATTRIB_LABEL, attr_store)

    def _init_storages(self, domain_storage=None):
        super()._init_storages(domain_storage)
        self.init_idr_cache_storage()
        self.init_attribute_storage()

    def _register_pool_req_handlers(self):
        node_handler = NodeHandler(self.node.db_manager,
                                   self.node.bls_bft.bls_crypto_verifier,
                                   self.node.write_req_validator)
        self.node.write_manager.register_req_handler(node_handler)

    def _register_domain_req_handlers(self):
        # Read handlers
        get_nym_handler = GetNymHandler(node=self.node, database_manager=self.node.db_manager)
        get_attribute_handler = GetAttributeHandler(node=self.node, database_manager=self.node.db_manager)
        get_schema_handler = GetSchemaHandler(database_manager=self.node.db_manager)
        get_claim_def_handler = GetClaimDefHandler(database_manager=self.node.db_manager)
        get_revoc_reg_def_handler = GetRevocRegDefHandler(database_manager=self.node.db_manager)
        get_revoc_reg_handler = GetRevocRegHandler(database_manager=self.node.db_manager)
        get_revoc_reg_delta_handler = GetRevocRegDeltaHandler(database_manager=self.node.db_manager,
                                                              get_revocation_strategy=RevocRegDefHandler.get_revocation_strategy)
        # Write handlers
        nym_handler = NymHandler(config=self.node.config,
                                 database_manager=self.node.db_manager,
                                 write_req_validator=self.node.write_req_validator)
        attrib_handler = AttributeHandler(database_manager=self.node.db_manager,
                                          write_req_validator=self.node.write_req_validator)
        schema_handler = SchemaHandler(database_manager=self.node.db_manager,
                                       write_req_validator=self.node.write_req_validator)
        claim_def_handler = ClaimDefHandler(database_manager=self.node.db_manager,
                                            write_req_validator=self.node.write_req_validator)
        revoc_reg_def_handler = RevocRegDefHandler(database_manager=self.node.db_manager,
                                                   write_req_validator=self.node.write_req_validator)
        revoc_reg_entry_handler = RevocRegEntryHandler(database_manager=self.node.db_manager,
                                                       write_req_validator=self.node.write_req_validator,
                                                       get_revocation_strategy=RevocRegDefHandler.get_revocation_strategy,
                                                       node=self.node)
        json_ld_context_handler = JsonLdContextHandler(database_manager=self.node.db_manager,
                                                       write_req_validator=self.node.write_req_validator)
        rich_schema_handler = RichSchemaHandler(database_manager=self.node.db_manager,
                                                write_req_validator=self.node.write_req_validator)
        rich_schema_encoding_handler = RichSchemaEncodingHandler(database_manager=self.node.db_manager,
                                                                 write_req_validator=self.node.write_req_validator)
        rich_schema_mapping_handler = RichSchemaMappingHandler(database_manager=self.node.db_manager,
                                                               write_req_validator=self.node.write_req_validator)
        rich_schema_cred_def_handler = RichSchemaCredDefHandler(database_manager=self.node.db_manager,
                                                                write_req_validator=self.node.write_req_validator)
        rich_schema_pres_def_handler = RichSchemaPresDefHandler(database_manager=self.node.db_manager,
                                                                write_req_validator=self.node.write_req_validator)
        get_rich_schema_obj_by_id_handler = GetRichSchemaObjectByIdHandler(database_manager=self.node.db_manager)
        get_rich_schema_obj_by_metadata_handler = GetRichSchemaObjectByMetadataHandler(
            database_manager=self.node.db_manager)

        # Register write handlers
        self.node.write_manager.register_req_handler(nym_handler)
        self.node.write_manager.register_req_handler(attrib_handler)
        self.node.write_manager.register_req_handler(schema_handler)
        self.node.write_manager.register_req_handler(claim_def_handler)
        self.node.write_manager.register_req_handler(revoc_reg_def_handler)
        self.node.write_manager.register_req_handler(revoc_reg_entry_handler)
        self.node.write_manager.register_req_handler(json_ld_context_handler)
        self.node.write_manager.register_req_handler(rich_schema_handler)
        self.node.write_manager.register_req_handler(rich_schema_encoding_handler)
        self.node.write_manager.register_req_handler(rich_schema_mapping_handler)
        self.node.write_manager.register_req_handler(rich_schema_cred_def_handler)
        self.node.write_manager.register_req_handler(rich_schema_pres_def_handler)
        # Additional handler for idCache
        self.register_idr_cache_nym_handler()
        # Register read handlers
        self.node.read_manager.register_req_handler(get_nym_handler)
        self.node.read_manager.register_req_handler(get_attribute_handler)
        self.node.read_manager.register_req_handler(get_schema_handler)
        self.node.read_manager.register_req_handler(get_claim_def_handler)
        self.node.read_manager.register_req_handler(get_revoc_reg_def_handler)
        self.node.read_manager.register_req_handler(get_revoc_reg_handler)
        self.node.read_manager.register_req_handler(get_revoc_reg_delta_handler)
        self.node.read_manager.register_req_handler(get_rich_schema_obj_by_id_handler)
        self.node.read_manager.register_req_handler(get_rich_schema_obj_by_metadata_handler)

    def _register_config_req_handlers(self):
        # Read handlers
        get_auth_rule_handler = GetAuthRuleHandler(database_manager=self.node.db_manager,
                                                   write_req_validator=self.node.write_req_validator)
        # Write handlers
        auth_rule_handler = AuthRuleHandler(database_manager=self.node.db_manager,
                                            write_req_validator=self.node.write_req_validator)
        auth_rule_handler_1_9_1 = AuthRuleHandler191(database_manager=self.node.db_manager,
                                                     write_req_validator=self.node.write_req_validator)
        auth_rules_handler = AuthRulesHandler(database_manager=self.node.db_manager,
                                              write_req_validator=self.node.write_req_validator)
        pool_config_handler = PoolConfigHandler(database_manager=self.node.db_manager,
                                                write_req_validator=self.node.write_req_validator,
                                                pool_config=self.node.poolCfg)
        pool_upgrade_handler = PoolUpgradeHandler(database_manager=self.node.db_manager,
                                                  upgrader=self.node.upgrader,
                                                  write_req_validator=self.node.write_req_validator,
                                                  pool_manager=self.node.poolManager)
        taa_aml_handler = TxnAuthorAgreementAmlHandler(database_manager=self.node.db_manager,
                                                       write_req_validator=self.node.write_req_validator)
        taa_handler = TxnAuthorAgreementHandler(database_manager=self.node.db_manager,
                                                write_req_validator=self.node.write_req_validator)
        taa_handler_v1 = TxnAuthorAgreementHandlerV1(database_manager=self.node.db_manager,
                                                     write_req_validator=self.node.write_req_validator)

        taa_disable_handler = TxnAuthorAgreementDisableHandler(database_manager=self.node.db_manager,
                                                               write_req_validator=self.node.write_req_validator)

        get_taa_aml_handler = GetTxnAuthorAgreementAmlHandler(database_manager=self.node.db_manager)
        get_taa_handler = GetTxnAuthorAgreementHandler(database_manager=self.node.db_manager)
        node_upgrade_handler = NodeUpgradeHandler(database_manager=self.node.db_manager)
        ledgers_freeze_handler = LedgersFreezeHandler(database_manager=self.node.db_manager,
                                                      write_req_validator=self.node.write_req_validator)
        get_frozen_ledgers_handler = GetFrozenLedgersHandler(database_manager=self.node.db_manager)
        get_flag_handler = GetFlagRequestHandler(node=self.node,
                                                 database_manager=self.node.db_manager)
        flag_handler = FlagRequestHandler(database_manager=self.node.db_manager,
                                          write_req_validator=self.node.write_req_validator)
        # Register write handlers
        self.node.write_manager.register_req_handler(auth_rule_handler)
        self.node.write_manager.register_req_handler(auth_rules_handler)
        self.node.write_manager.register_req_handler(pool_config_handler)
        self.node.write_manager.register_req_handler(pool_upgrade_handler)
        self.node.write_manager.register_req_handler(taa_aml_handler)
        self.node.write_manager.register_req_handler(taa_handler)
        self.node.write_manager.register_req_handler(taa_disable_handler)
        self.node.write_manager.register_req_handler(node_upgrade_handler)
        self.node.write_manager.register_req_handler(ledgers_freeze_handler)
        self.node.write_manager.register_req_handler(flag_handler)
        # Register read handlers
        self.node.read_manager.register_req_handler(get_auth_rule_handler)
        self.node.read_manager.register_req_handler(get_taa_aml_handler)
        self.node.read_manager.register_req_handler(get_taa_handler)
        self.node.read_manager.register_req_handler(get_frozen_ledgers_handler)
        self.node.read_manager.register_req_handler(get_flag_handler)
        # Register write handlers for a version
        self.node.write_manager.register_req_handler_with_version(auth_rule_handler_1_9_1,
                                                                  version="1.9.1")
        self.node.write_manager.register_req_handler_with_version(taa_handler_v1,
                                                                  version="1")

    def _register_action_req_handlers(self):
        # Action handlers
        pool_restart_handler = PoolRestartHandler(database_manager=self.node.db_manager,
                                                  write_req_validator=self.node.write_req_validator,
                                                  restarter=self.node.restarter)
        validator_info_handler = ValidatorInfoHandler(database_manager=self.node.db_manager,
                                                      write_req_validator=self.node.write_req_validator,
                                                      info_tool=self.node._info_tool)
        # Register action handlers
        self.node.action_manager.register_action_handler(pool_restart_handler)
        self.node.action_manager.register_action_handler(validator_info_handler)

    def _register_domain_batch_handlers(self):
        super()._register_domain_batch_handlers()
        self.register_idr_cache_batch_handler()

    def _register_config_batch_handlers(self):
        config_batch_handler = ConfigBatchHandler(database_manager=self.node.db_manager,
                                                  upgrader=self.node.upgrader,
                                                  pool_config=self.node.poolCfg)
        self.node.write_manager.register_batch_handler(config_batch_handler)

    def register_idr_cache_nym_handler(self):
        idr_cache_nym_handler = IdrCacheNymHandler(database_manager=self.node.db_manager)
        self.node.write_manager.register_req_handler(idr_cache_nym_handler)

    def register_idr_cache_batch_handler(self):
        idr_cache_batch_handler = IdrCacheBatchHandler(database_manager=self.node.db_manager)
        self.node.write_manager.register_batch_handler(idr_cache_batch_handler)

    def init_pool_config(self):
        return PoolConfig(self.node.configLedger)

    def init_upgrader(self):
        return Upgrader(self.node.id,
                        self.node.name,
                        self.node.dataLocation,
                        self.node.config,
                        self.node.configLedger,
                        actionFailedCallback=self.node.postConfigLedgerCaughtUp,
                        action_start_callback=self.node.notify_upgrade_start)

    def init_restarter(self):
        return Restarter(self.node.id,
                         self.node.name,
                         self.node.dataLocation,
                         self.node.config)

    def _init_common_managers(self):
        super()._init_common_managers()
        self.node.upgrader = self.init_upgrader()
        self.node.restarter = self.init_restarter()
        self.node.poolCfg = self.init_pool_config()

    def _init_write_request_validator(self):
        constraint_serializer = ConstraintsSerializer(domain_state_serializer)
        config_state = self.node.states[CONFIG_LEDGER_ID]
        self.node.write_req_validator = WriteRequestValidator(config=self.node.config,
                                                              auth_map=auth_map,
                                                              cache=self.node.idrCache,
                                                              config_state=config_state,
                                                              state_serializer=constraint_serializer,
                                                              metrics=self.node.metrics)
