#!/usr/bin/env python

import sys
import os

from setuptools import setup, find_packages, __version__

v = sys.version_info
if sys.version_info < (3, 5):
    msg = "FAIL: Requires Python 3.5 or later, " \
          "but setup.py was run using {}.{}.{}"
    v = sys.version_info
    print(msg.format(v.major, v.minor, v.micro))
    # noinspection PyPackageRequirements
    print("NOTE: Installation failed. Run setup.py using python3")
    sys.exit(1)

try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're probably being frozen, and __file__ triggered this NameError
    # Work around this
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)

METADATA = os.path.join(SETUP_DIRNAME, 'indy_node', '__metadata__.py')
# Load the metadata using exec() so we don't trigger an import of
# ioflo.__init__
exec(compile(open(METADATA).read(), METADATA, 'exec'))

BASE_DIR = os.path.join(os.path.expanduser("~"), ".indy")
LOG_DIR = os.path.join(BASE_DIR, "log")
CONFIG_FILE = os.path.join(BASE_DIR, "indy_config.py")

tests_require = ['pytest', 'pytest-xdist', 'python3-indy==1.3.1-dev-469']

setup(
    name='indy-node',
    version=__version__,
    description='Indy node',
    url='https://github.com/hyperledger/indy-node',
    author=__author__,
    author_email='hyperledger-indy@lists.hyperledger.org',
    license=__license__,
    keywords='Indy Node',
    packages=find_packages(exclude=['docs', 'docs*']) + [
        'data'],
    package_data={
        '': ['*.txt', '*.md', '*.rst', '*.json', '*.conf', '*.html',
             '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL', '*.indy']},
    include_package_data=True,
    data_files=[(
        (BASE_DIR, ['data/nssm_original.exe'])
    )],
    install_requires=['indy-plenum==1.2.40',
                      'indy-anoncreds==1.0.11',
                      'python-dateutil',
                      'timeout-decorator'],
    setup_requires=['pytest-runner'],
    extras_require={
        'tests': tests_require
    },
    tests_require=tests_require,
    scripts=['scripts/indy',
             'scripts/change_node_ha',
             'scripts/add_new_node',
             'scripts/reset_client',
             'scripts/start_indy_node',
             'scripts/start_node_control_tool',
             'scripts/clear_node.py',
             'scripts/get_keys',
             'scripts/generate_indy_pool_transactions',
             'scripts/init_indy_keys',
             'scripts/upgrade_indy_node_ubuntu1604.sh',
             'scripts/upgrade_indy_node_ubuntu1604_test.sh',
             'scripts/upgrade_indy_node.bat',
             'scripts/upgrade_indy_node_test.bat',
             'scripts/restart_indy_node_ubuntu1604.sh',
             'scripts/restart_indy_node.bat',
             'scripts/restart_sovrin_node_ubuntu1604.sh',
             'scripts/complete_rebranding_upgrade_ubuntu1604.sh',
             'scripts/install_indy_node.bat',
             'scripts/delete_indy_node.bat',
             'scripts/restart_upgrade_agent.bat',
             'scripts/install_nssm.bat',
             'scripts/read_ledger',
             'scripts/test_some_write_keys_others_read_them',
             'scripts/test_users_write_and_read_own_keys',
             'scripts/validator-info',
             'scripts/init_bls_keys',
             'scripts/enable_bls',
             'scripts/create_dirs.sh',
             'scripts/indy_old_cli_export_dids',
             'scripts/setup_iptables',
             'scripts/setup_indy_node_iptables']
)
