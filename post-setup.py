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
import shutil

from indy_common.setup_util import Setup

BASE_DIR = os.path.join(os.path.expanduser("~"), ".indy")
Setup(BASE_DIR).setupCommon()
Setup(BASE_DIR).setupNode()
Setup(BASE_DIR).setupClient()
if not os.path.exists(os.path.join(BASE_DIR, 'nssm.exe')):
    shutil.copy2(os.path.join(BASE_DIR, 'nssm_original.exe'),
                 os.path.join(BASE_DIR, 'nssm.exe'))
