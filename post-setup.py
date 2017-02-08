import os
import shutil

from sovrin_common.setup_util import Setup

BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
Setup(BASE_DIR).setupNode()
if not os.path.exists(os.path.join(BASE_DIR, 'nssm.exe')):
    shutil.copy2(os.path.join(BASE_DIR, 'nssm_original.exe'), os.path.join(BASE_DIR, 'nssm.exe'))