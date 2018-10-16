import json
import logging
import types
from collections import OrderedDict
from typing import Any

import sys

import pytest
from stp_core.common.log import getlogger

from plenum.common.constants import STEWARD_STRING
from plenum.common.util import randomString
from plenum.common.messages.node_messages import Commit

from plenum.server.node import Node
from plenum.test.pool_transactions.helper import sdk_add_new_nym, prepare_nym_request, \
    sdk_sign_and_send_prepared_request
from plenum.test.helper import sdk_json_to_request_object
from pympler import asizeof

max_depth = 10


# Self made memory function. We can use it if we want to explore
# something specific.
def get_max(obj, seen=None, now_depth=0, path=str()):
    if now_depth > max_depth:
        return {}
    dictionary = {(path, type(obj)): sys.getsizeof(obj)}
    path += str(type(obj)) + ' ---> '
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return {}
    seen.add(obj_id)
    if isinstance(obj, dict):
        vpath = path + 'value ---> '
        for d in [get_max(v, seen, now_depth + 1, vpath) for v in obj.values()]:
            updater(dictionary, d)
        kpath = path + 'key ---> '
        for d in [get_max(k, seen, now_depth + 1, kpath) for k in obj.keys()]:
            updater(dictionary, d)
    elif hasattr(obj, '__dict__'):
        dpath = path + '__dict__ ---> '
        d = get_max(obj.__dict__, seen, now_depth + 1, dpath)
        updater(dictionary, d)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        ipath = path + '__iter__ ---> '
        for d in [get_max(i, seen, now_depth + 1, ipath) for i in obj]:
            updater(dictionary, d)
    return dictionary


def updater(store_d, new_d):
    for k in new_d.keys():
        if k in store_d:
            store_d[k] += int(new_d[k])
        else:
            store_d[k] = new_d[k]


def dont_send_commit(self, msg: Any, *rids, signer=None, message_splitter=None):
    if isinstance(msg, (Commit)):
        if rids:
            rids = [rid for rid in rids if rid not in self.nodestack.getRemote(self.ignore_node_name).uid]
        else:
            rids = [self.nodestack.getRemote(name).uid for name
                    in self.nodestack.remotes.keys() if name not in self.ignore_node_name]
    self.old_send(msg, *rids, signer=signer, message_splitter=message_splitter)


def dont_send_commit_to(nodes, ignore_node_name):
    for node in nodes:
        if not hasattr(node, 'ignore_node_name'):
            node.ignore_node_name = []
        node.ignore_node_name.append(ignore_node_name)
        node.old_send = types.MethodType(Node.send, node)
        node.send = types.MethodType(dont_send_commit, node)


def reset_sending(nodes):
    for node in nodes:
        node.send = types.MethodType(Node.send, node)


def sdk_add_new_nym_without_waiting(looper, sdk_pool_handle, creators_wallet,
                                    alias=None, role=None, seed=None,
                                    dest=None, verkey=None, skipverkey=False):
    seed = seed or randomString(32)
    alias = alias or randomString(5)
    wh, _ = creators_wallet

    nym_request, new_did = looper.loop.run_until_complete(
        prepare_nym_request(creators_wallet, seed,
                            alias, role, dest, verkey, skipverkey))
    sdk_sign_and_send_prepared_request(looper, creators_wallet,
                                       sdk_pool_handle, nym_request)


# Pytest logger is heavy, so we exclude it
@pytest.fixture
def logger():
    logger = getlogger()
    old_value = logger.getEffectiveLevel()
    logger.root.setLevel(logging.CRITICAL)
    yield logger
    logger.root.setLevel(old_value)


@pytest.mark.skip('Unskip if you need to debug')
def test_memory_debugging(looper,
                          nodeSet,
                          sdk_wallet_trust_anchor,
                          sdk_pool_handle,
                          logger):
    # Settings
    requests_count = 500
    file_name = '.memory_data.txt'

    # Sets for emulating commits problems
    set1 = list(nodeSet)
    set1.remove(nodeSet[0])
    set2 = list(nodeSet)
    set2.remove(nodeSet[1])
    set3 = list(nodeSet)
    set3.remove(nodeSet[2])
    primary = nodeSet[0]

    memory_dicts = OrderedDict()

    memory_dicts['After starting'] = asizeof.asized(primary, detail=15)

    while primary.master_replica.lastPrePrepareSeqNo < requests_count:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trust_anchor)

    memory_dicts['After ordering'] = asizeof.asized(primary, detail=15)

    # Emulate commit sending problems
    dont_send_commit_to(set1, nodeSet[0].name)
    dont_send_commit_to(set2, nodeSet[1].name)
    dont_send_commit_to(set3, nodeSet[2].name)

    # Sending requests until nodes generate `unordered_requests_count` 3pc batches
    while primary.master_replica.lastPrePrepareSeqNo < requests_count * 2:
        sdk_add_new_nym_without_waiting(looper, sdk_pool_handle, sdk_wallet_trust_anchor)

    memory_dicts['After {} unordered'.format(requests_count)] = asizeof.asized(primary, detail=15)

    # Remove commit problems
    reset_sending(set1)
    reset_sending(set2)
    reset_sending(set3)

    # primary ask for commits
    for i in range(primary.master_replica.last_ordered_3pc[1], primary.master_replica.lastPrePrepareSeqNo):
        primary.replicas._replicas.values()[0]._request_commit((0, i))
    for i in range(primary.replicas._replicas.values()[1].last_ordered_3pc[1],
                   primary.replicas._replicas.values()[1].lastPrePrepareSeqNo):
        primary.replicas._replicas.values()[1]._request_commit((0, i))
    looper.runFor(5)

    memory_dicts['After {} ordered'.format(requests_count)] = asizeof.asized(primary, detail=15)

    # primary clear queues
    primary.replicas._replicas.values()[0]._gc(primary.replicas._replicas.values()[0].last_ordered_3pc)
    primary.replicas._replicas.values()[1]._gc(primary.replicas._replicas.values()[1].last_ordered_3pc)

    memory_dicts['After _gc called'] = asizeof.asized(primary, detail=15)

    # Emulate problems again
    dont_send_commit_to(set1, nodeSet[0].name)
    dont_send_commit_to(set2, nodeSet[1].name)
    dont_send_commit_to(set3, nodeSet[2].name)

    while primary.master_replica.lastPrePrepareSeqNo < requests_count * 3:
        sdk_add_new_nym_without_waiting(looper, sdk_pool_handle, sdk_wallet_trust_anchor)

    memory_dicts['After {} unordered again'.format(requests_count)] = asizeof.asized(primary, detail=15)

    # Remove commit problems
    reset_sending(set1)
    reset_sending(set2)
    reset_sending(set3)

    for i in range(primary.master_replica.last_ordered_3pc[1], primary.master_replica.lastPrePrepareSeqNo):
        primary.replicas._replicas.values()[0]._request_commit((0, i))
    for i in range(primary.replicas._replicas.values()[1].last_ordered_3pc[1],
                   primary.replicas._replicas.values()[1].lastPrePrepareSeqNo):
        primary.replicas._replicas.values()[1]._request_commit((0, i))
    looper.runFor(5)

    memory_dicts['After {} ordered again'.format(requests_count)] = asizeof.asized(primary, detail=15)

    primary.replicas._replicas.values()[0]._gc(primary.replicas._replicas.values()[0].last_ordered_3pc)
    primary.replicas._replicas.values()[1]._gc(primary.replicas._replicas.values()[1].last_ordered_3pc)

    memory_dicts['After _gc called again'] = asizeof.asized(primary, detail=15)

    file = open(file_name, 'w')
    indent = 75
    for k, size_obj in memory_dicts.items():
        # Formatting
        header = str(k) + ': {}'.format(size_obj.size) + ' bytes. Detailed size:'
        if len(header) < indent:
            header += ' ' * (indent - len(header))
        file.write(header)

        size_obj = next(r for r in size_obj.refs if r.name == '__dict__')
        # Sort in descending order to select most 'heavy' collections
        for num, sub_obj in enumerate(sorted(size_obj.refs, key=lambda v: v.size, reverse=True)):
            if num > 10:
                break
            file.write('[{} : {}],      '.format(sub_obj.name, sub_obj.size))
        file.write('\n')
    file.close()


@pytest.mark.skip('Unskip if you need to debug')
def test_requests_collection_debugging(looper,
                                       nodeSet,
                                       sdk_wallet_trustee):
    primary = nodeSet[0]

    seed = randomString(32)
    alias = randomString(5)
    wh, _ = sdk_wallet_trustee
    nym_request, new_did = looper.loop.run_until_complete(
        prepare_nym_request(sdk_wallet_trustee, seed,
                            alias, STEWARD_STRING))

    nym_request = json.loads(nym_request)
    a = sys.getsizeof(primary.requests)

    mas = []
    for _ in range(50000):
        req = sdk_json_to_request_object(nym_request)
        req.reqId = randomString(32)
        mas.append(req)
        primary.requests.add_propagate(req, 'asd')
        primary.requests.mark_as_forwarded(req, 2)
        primary.requests.set_finalised(req)

    b = sys.getsizeof(primary.requests)
    lb = len(primary.requests)

    for req in mas:
        primary.requests.mark_as_executed(req)
        primary.requests.free(req.key)
        primary.requests.free(req.key)

    c = sys.getsizeof(primary.requests)
    lc = len(primary.requests)

    for _ in range(100000):
        req = sdk_json_to_request_object(nym_request)
        req.reqId = randomString(32)
        mas.append(req)
        primary.requests.add_propagate(req, 'asd')
        primary.requests.mark_as_forwarded(req, 2)
        primary.requests.set_finalised(req)

    d = sys.getsizeof(primary.requests)
    ld = len(primary.requests)

    print(a)
    print(b, lb)
    print(c, lc)
    print(d, ld)
