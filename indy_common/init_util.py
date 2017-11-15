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

from plenum.common.init_util import initialize_node_environment as \
    p_initialize_node_environment, cleanup_environment
from indy_common.config_util import getConfig


def initialize_node_environment(name, base_dir, sigseed=None,
                                override_keep=False,
                                config=None):
    config = config or getConfig()
    base_dir = base_dir or config.baseDir
    cleanup_environment(name, base_dir)
    vk, bls_key = p_initialize_node_environment(name, base_dir, sigseed, override_keep)

    return vk, bls_key
