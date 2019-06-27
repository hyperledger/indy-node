#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

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
    here = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # it can be the case when we are being run as script or frozen
    here = os.path.abspath(os.path.dirname(sys.argv[0]))

metadata = {'__file__': os.path.join(here, 'indy_node', '__metadata__.py')}
with open(metadata['__file__'], 'r') as f:
    exec(f.read(), metadata)

BASE_DIR = os.path.join(os.path.expanduser("~"), ".indy")

tests_require = ['pytest==3.3.1', 'pytest-xdist==1.22.1', 'python3-indy==1.9.0-dev-1139', 'pytest-asyncio==0.8.0']

setup(
    name=metadata['__title__'],
    version=metadata['__version__'],
    description=metadata['__description__'],
    long_description=metadata['__long_description__'],
    keywords=metadata['__keywords__'],
    url=metadata['__url__'],
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    maintainer=metadata['__maintainer__'],
    license=metadata['__license__'],
    packages=find_packages(exclude=['docs', 'docs*']) + [
        'data'],
    # TODO move that to MANIFEST.in
    package_data={
        '': ['*.txt', '*.md', '*.rst', '*.json', '*.conf', '*.html',
             '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL', '*.indy']},
    include_package_data=True,
    data_files=[(
        (BASE_DIR, ['data/nssm_original.exe'])
    )],
    install_requires=['indy-plenum==1.9.0',
                      'python-dateutil',
                      'timeout-decorator==0.4.0',
                      'distro==1.3.0'],
    setup_requires=['pytest-runner'],
    extras_require={
        'tests': tests_require
    },
    tests_require=tests_require,
    scripts=['scripts/start_indy_node',
             'scripts/start_node_control_tool',
             'scripts/clear_node.py',
             'scripts/get_keys',
             'scripts/get_metrics',
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
             'scripts/validator-info',
             'scripts/validator-info-history',
             'scripts/init_bls_keys',
             'scripts/create_dirs.sh',
             'scripts/setup_iptables',
             'scripts/setup_indy_node_iptables',
             'scripts/current_validators',
             'scripts/node_address_list',
             'scripts/generate_bls_proof_of_possession',
             'tools/diagnostics/nscapture',
             'tools/diagnostics/nsdiff',
             'tools/diagnostics/nsreplay',
             ]
)
