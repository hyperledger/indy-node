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

import os

from ledger.genesis_txn.genesis_txn_file_util import genesis_txn_file

_BASE_DIR = os.path.expanduser('~/.sovrin')
_NETWORKS = ['live', 'local', 'sandbox']


def _update_wallets_dir_name_if_outdated():
    old_named_path = os.path.expanduser(os.path.join(_BASE_DIR, 'keyrings'))
    new_named_path = os.path.expanduser(os.path.join(_BASE_DIR, 'wallets'))
    if not os.path.exists(new_named_path) and os.path.isdir(old_named_path):
        os.rename(old_named_path, new_named_path)


def _update_genesis_txn_file_name_if_outdated(transaction_file):
    old_named_path = os.path.join(_BASE_DIR, transaction_file)
    new_named_path = os.path.join(_BASE_DIR, genesis_txn_file(transaction_file))
    if not os.path.exists(new_named_path) and os.path.isfile(old_named_path):
        os.rename(old_named_path, new_named_path)


def migrate():
    _update_wallets_dir_name_if_outdated()
    for network in _NETWORKS:
        _update_genesis_txn_file_name_if_outdated(
            'pool_transactions_{}'.format(network))
