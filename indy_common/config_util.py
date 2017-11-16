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
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location

from plenum.common.config_util import getConfig as PlenumConfig, \
    extend_with_default_external_config


CONFIG = None


def getConfig(user_config_dir=None):
    global CONFIG
    if not CONFIG:
        config = PlenumConfig(user_config_dir)
        indyConfig = import_module("indy_common.config")
        config.__dict__.update(indyConfig.__dict__)

        extend_with_default_external_config(config, user_config_dir)

        CONFIG = config
    return CONFIG
