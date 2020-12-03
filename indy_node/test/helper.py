import json
from contextlib import contextmanager

import base58
from indy.did import replace_keys_start, replace_keys_apply
from indy.ledger import (
    build_attrib_request, build_get_attrib_request,
    build_get_auth_rule_request, build_auth_rule_request,
    build_auth_rules_request)
from libnacl import randombytes

from indy_common.authorize.auth_actions import ADD_PREFIX, EDIT_PREFIX
from indy_common.authorize.auth_constraints import ROLE, CONSTRAINT_ID, ConstraintsEnum, SIG_COUNT, NEED_TO_BE_OWNER, \
    METADATA, OFF_LEDGER_SIGNATURE
from indy_common.config_helper import NodeConfigHelper
from indy_common.constants import NYM, ENDORSER, CONSTRAINT, AUTH_ACTION, AUTH_TYPE, FIELD, NEW_VALUE, OLD_VALUE
from indy_common.test.helper import TempStorage
from indy_node.server.node import Node
from indy_node.server.node_bootstrap import NodeBootstrap
from indy_node.server.upgrader import Upgrader
from plenum.common.constants import TRUSTEE
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import rawToFriendly
from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_req
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.test.test_node import TestNodeCore
from plenum.test.testable import spyable
from stp_core.common.log import getlogger
from stp_core.types import HA

logger = getlogger()


@spyable(methods=[Upgrader.processLedger])
class TestUpgrader(Upgrader):
    pass


class TestNodeBootstrap(NodeBootstrap):
    def init_upgrader(self):
        return TestUpgrader(self.node.id, self.node.name, self.node.dataLocation, self.node.config,
                            self.node.configLedger,
                            actionFailedCallback=self.node.postConfigLedgerCaughtUp,
                            action_start_callback=self.node.notify_upgrade_start)


# noinspection PyShadowingNames,PyShadowingNames
@spyable(
    methods=[Node.handleOneNodeMsg, Node.processRequest, Node.processOrdered,
             Node.postToClientInBox, Node.postToNodeInBox, "eatTestMsg",
             Node.discard,
             Node.reportSuspiciousNode, Node.reportSuspiciousClient,
             Node.processRequest, Node.processPropagate, Node.propagate,
             Node.forward, Node.send, Node.checkPerformance,
             Node.getReplyFromLedger, Node.getReplyFromLedgerForRequest,
             Node.no_more_catchups_needed, Node.onBatchCreated,
             Node.onBatchRejected])
class TestNode(TempStorage, TestNodeCore, Node):
    def __init__(self, *args, **kwargs):
        from plenum.common.stacks import nodeStackClass, clientStackClass
        self.NodeStackClass = nodeStackClass
        self.ClientStackClass = clientStackClass
        if kwargs.get('bootstrap_cls', None) is None:
            kwargs['bootstrap_cls'] = TestNodeBootstrap

        Node.__init__(self, *args, **kwargs)
        TestNodeCore.__init__(self, *args, **kwargs)
        self.cleanupOnStopping = True

    def init_domain_req_handler(self):
        return Node.init_domain_req_handler(self)

    def init_core_authenticator(self):
        return Node.init_core_authenticator(self)

    def onStopping(self, *args, **kwargs):
        # self.graphStore.store.close()
        super().onStopping(*args, **kwargs)
        if self.cleanupOnStopping:
            self.cleanupDataLocation()

    def schedule_node_status_dump(self):
        pass

    def dump_additional_info(self):
        pass

    @property
    def nodeStackClass(self):
        return self.NodeStackClass

    @property
    def clientStackClass(self):
        return self.ClientStackClass


# TODO makes sense to move plenum
def sdk_send_and_check_req_json(
    looper, sdk_pool_handle, sdk_wallet, req_json, no_wait=False
):
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet, req_json)
    if no_wait:
        return req
    resp = sdk_get_and_check_replies(looper, [req])
    return resp


def sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_handle, attrib,
                                dest=None, xhash=None, enc=None):
    _, s_did = sdk_wallet_handle
    t_did = dest or s_did
    attrib_req = looper.loop.run_until_complete(
        build_attrib_request(s_did, t_did, xhash, attrib, enc))
    return sdk_send_and_check_req_json(looper, sdk_pool_handle, sdk_wallet_handle, attrib_req)


def sdk_get_attribute_and_check(looper, sdk_pool_handle, submitter_wallet, target_did, attrib_name):
    _, submitter_did = submitter_wallet
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, target_did, attrib_name, None, None))
    return sdk_send_and_check_req_json(looper, sdk_pool_handle, submitter_wallet, req)


def sdk_add_raw_attribute(looper, sdk_pool_handle, sdk_wallet_handle, name, value):
    _, did = sdk_wallet_handle
    attrData = json.dumps({name: value})
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_handle, attrData)


# AUTH_RULE / GET_AUTH_RULE helpers


def build_auth_rule_request_json(
    looper, submitter_did,
    auth_action, auth_type, field, constraint, old_value=None, new_value=None
):
    return looper.loop.run_until_complete(
        build_auth_rule_request(
            submitter_did=submitter_did,
            txn_type=auth_type,
            action=auth_action,
            field=field,
            old_value=old_value,
            new_value=new_value,
            constraint=json.dumps(constraint)
        )
    )


def build_get_auth_rule_request_json(
    looper, submitter_did,
    auth_type=None,
    auth_action=None,
    field=None,
    old_value=None,
    new_value=None
):
    return looper.loop.run_until_complete(
        build_get_auth_rule_request(
            submitter_did=submitter_did,
            txn_type=auth_type,
            action=auth_action,
            field=field,
            old_value=old_value,
            new_value=new_value
        )
    )


def sdk_send_and_check_auth_rule_request(
    looper, sdk_pool_handle, sdk_wallet,
    auth_action, auth_type, field, constraint, old_value=None, new_value=None,
    no_wait=False
):
    req_json = build_auth_rule_request_json(
        looper, sdk_wallet[1],
        auth_action=auth_action,
        auth_type=auth_type,
        field=field,
        old_value=old_value,
        new_value=new_value,
        constraint=constraint
    )

    return sdk_send_and_check_req_json(
        looper, sdk_pool_handle, sdk_wallet, req_json, no_wait=no_wait
    )


def sdk_send_and_check_auth_rules_request(looper, sdk_pool_handle,
                                          sdk_wallet, rules=None, no_wait=False):
    if rules is None:
        rules = [generate_auth_rule(ADD_PREFIX, NYM,
                                    ROLE, ENDORSER),
                 generate_auth_rule(EDIT_PREFIX, NYM,
                                    ROLE, ENDORSER, TRUSTEE)]
    req_json = looper.loop.run_until_complete(
        build_auth_rules_request(submitter_did=sdk_wallet[1], data=json.dumps(rules)))
    return sdk_send_and_check_req_json(
        looper, sdk_pool_handle, sdk_wallet, req_json, no_wait=no_wait
    )


def sdk_send_and_check_get_auth_rule_request(
    looper, sdk_pool_handle, sdk_wallet,
    auth_type=None,
    auth_action=None,
    field=None,
    old_value=None,
    new_value=None
):
    req_json = build_get_auth_rule_request_json(
        looper, sdk_wallet[1],
        auth_type=auth_type,
        auth_action=auth_action,
        field=field,
        old_value=old_value,
        new_value=new_value
    )
    return sdk_send_and_check_req_json(
        looper, sdk_pool_handle, sdk_wallet, req_json
    )


def generate_auth_rule(auth_action=ADD_PREFIX, auth_type=NYM,
                       field=ROLE, new_value=ENDORSER,
                       old_value=None, constraint=None):
    if constraint is None:
        constraint = generate_constraint_entity()
    rule = {CONSTRAINT: constraint,
            AUTH_ACTION: auth_action,
            AUTH_TYPE: auth_type,
            FIELD: field,
            NEW_VALUE: new_value
            }
    if old_value or auth_action == EDIT_PREFIX:
        rule[OLD_VALUE] = old_value
    return rule


def generate_constraint_entity(constraint_id=ConstraintsEnum.ROLE_CONSTRAINT_ID,
                               role=TRUSTEE,
                               sig_count=1,
                               need_to_be_owner=False,
                               off_ledger_signature=None,
                               metadata={}):
    constraint = {CONSTRAINT_ID: constraint_id,
                  ROLE: role,
                  SIG_COUNT: sig_count,
                  NEED_TO_BE_OWNER: need_to_be_owner,
                  METADATA: metadata}
    if off_ledger_signature is not None:
        constraint[OFF_LEDGER_SIGNATURE] = off_ledger_signature
    return constraint


base58_alphabet = set(base58.alphabet.decode("utf-8"))


def check_str_is_base58_compatible(str):
    return not (set(str) - base58_alphabet)


def sdk_rotate_verkey(looper, sdk_pool_handle, wh,
                      did_of_changer,
                      did_of_changed,
                      verkey=None):
    verkey = verkey or looper.loop.run_until_complete(
        replace_keys_start(wh, did_of_changed, json.dumps({})))

    sdk_add_new_nym(looper, sdk_pool_handle,
                    (wh, did_of_changer), dest=did_of_changed,
                    verkey=verkey)
    looper.loop.run_until_complete(
        replace_keys_apply(wh, did_of_changed))
    return verkey


def start_stopped_node(stopped_node, looper, tconf, tdir, allPluginsPath, start=True):
    nodeHa, nodeCHa = HA(*
                         stopped_node.nodestack.ha), HA(*
                                                        stopped_node.clientstack.ha)
    config_helper = NodeConfigHelper(stopped_node.name, tconf, chroot=tdir)
    restarted_node = TestNode(stopped_node.name,
                              config_helper=config_helper,
                              config=tconf,
                              ha=nodeHa, cliha=nodeCHa,
                              pluginPaths=allPluginsPath)
    if start:
        looper.add(restarted_node)
    return restarted_node


def modify_field(string, value, *field_path):
    d = json.loads(string)
    prev = None
    for i in range(0, len(field_path) - 1):
        if prev is None:
            prev = d[field_path[i]]
            continue
        prev = prev[field_path[i]]
    if prev:
        prev[field_path[-1]] = value
    else:
        d[field_path[-1]] = value
    return json.dumps(d)


def createUuidIdentifier():
    return rawToFriendly(randombytes(16))


def createHalfKeyIdentifierAndAbbrevVerkey(seed=None):
    didSigner = DidSigner(seed=seed)
    return didSigner.identifier, didSigner.verkey


def createCryptonym(seed=None):
    return SimpleSigner(seed=seed).identifier


def createUuidIdentifierAndFullVerkey(seed=None):
    didSigner = DidSigner(identifier=createUuidIdentifier(), seed=seed)
    return didSigner.identifier, didSigner.verkey


@contextmanager
def rich_schemas_enabled_scope(tconf):
    old_value = tconf.ENABLE_RICH_SCHEMAS
    tconf.ENABLE_RICH_SCHEMAS = True
    yield tconf
    tconf.ENABLE_RICH_SCHEMAS = old_value
