#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import json
import os
from shutil import rmtree

import pytest
from indy import pool, wallet

from indy_acceptance.test.client import Client


@pytest.fixture
def pool_name():
    return 'acceptance'


@pytest.fixture
def wallet_name():
    return 'default'


@pytest.fixture
def base_dir_created():
    base_dir = os.path.join(os.path.expanduser('~'), '.indy')

    if os.path.isdir(base_dir):
        rmtree(base_dir)
    elif os.path.isfile(base_dir):
        os.remove(base_dir)

    os.makedirs(base_dir)
    yield
    rmtree(base_dir)


@pytest.fixture
def pool_genesis_txn_path():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    acceptance_dir = os.path.join(test_dir, os.pardir, os.pardir)
    return os.path.join(acceptance_dir, 'pool.txn')


# noinspection PyUnusedLocal
@pytest.fixture
def pool_ledger_created(base_dir_created, pool_name, pool_genesis_txn_path,
                        event_loop):
    event_loop.run_until_complete(pool.create_pool_ledger_config(
        pool_name,
        json.dumps({
            'genesis_txn': str(pool_genesis_txn_path)
        })))
    yield
    event_loop.run_until_complete(pool.delete_pool_ledger_config(pool_name))


# noinspection PyUnusedLocal
@pytest.fixture
def pool_handle(pool_ledger_created, pool_name, event_loop):
    pool_handle = event_loop.run_until_complete(
        pool.open_pool_ledger(pool_name, None))
    yield pool_handle
    event_loop.run_until_complete(pool.close_pool_ledger(pool_handle))


# noinspection PyUnusedLocal
@pytest.fixture
def wallet_created(base_dir_created, pool_ledger_created,
                   pool_name, wallet_name, event_loop):
    event_loop.run_until_complete(
        wallet.create_wallet(pool_name, wallet_name, 'default', None, None))
    yield
    event_loop.run_until_complete(wallet.delete_wallet(wallet_name, None))


# noinspection PyUnusedLocal
@pytest.fixture
def wallet_handle(wallet_created, wallet_name, event_loop):
    wallet_handle = event_loop.run_until_complete(
        wallet.open_wallet(wallet_name, None, None))
    yield wallet_handle
    event_loop.run_until_complete(wallet.close_wallet(wallet_handle))


@pytest.fixture
def client(pool_handle, wallet_handle):
    return Client(pool_handle, wallet_handle)
