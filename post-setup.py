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
