#!/usr/bin/env python

import sys
import os

import subprocess
from setuptools import setup, find_packages, __version__
from setuptools.command.develop import develop
from setuptools.command.install import install

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

METADATA = os.path.join(SETUP_DIRNAME, 'sovrin_node', '__metadata__.py')
# Load the metadata using exec() so we don't trigger an import of ioflo.__init__
exec(compile(open(METADATA).read(), METADATA, 'exec'))

BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
SAMPLE_DIR = os.path.join(BASE_DIR, ".sovrin")
CONFIG_FILE = os.path.join(BASE_DIR, "sovrin_config.py")

for path in [BASE_DIR, SAMPLE_DIR]:
    if not os.path.exists(path):
        os.makedirs(path)

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        msg = "# Here you can create config entries according to your " \
              "needs.\n " \
              "# For help, refer config.py in the sovrin package.\n " \
              "# Any entry you add here would override that from config " \
              "example\n"
        f.write(msg)


def post_install():
    subprocess.run(['python post-setup.py'], shell=True)


class EnhancedInstall(install):
    def run(self):
        install.run(self)
        post_install()


class EnhancedInstallDev(develop):
    def run(self):
        develop.run(self)
        post_install()

setup(
    name='indy-node-dev',
    version=__version__,
    description='Sovrin node',
    url='https://github.com/hyperledger/indy-node',
    author=__author__,
    author_email='repo@sovrin.org',
    license=__license__,
    keywords='Sovrin Node',
    packages=find_packages(exclude=['docs', 'docs*']) + [
        'data'],
    package_data={
        '': ['*.txt', '*.md', '*.rst', '*.json', '*.conf', '*.html',
             '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL', '*.sovrin']},
    include_package_data=True,
    data_files=[(
        (BASE_DIR, ['data/nssm_original.exe'])
    )],
    install_requires=['indy-plenum-dev==0.4.61',
                      'indy-anoncreds-dev==0.4.18',
                      'python-dateutil',
                      'timeout-decorator'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    scripts=['scripts/sovrin',
             'scripts/change_node_ha',
             'scripts/add_new_node',
             'scripts/reset_client',
             'scripts/start_sovrin_node',
             'scripts/start_node_control_tool.py',
             'scripts/clear_node.py',
             'scripts/get_keys',
             'scripts/generate_sovrin_pool_transactions',
             'scripts/get_package_dependencies_ubuntu.sh',
             'scripts/init_sovrin_keys',
             'scripts/upgrade_sovrin_node_ubuntu1604.sh',
             'scripts/upgrade_sovrin_node_ubuntu1604_test.sh',
             'scripts/upgrade_sovrin_node.bat',
             'scripts/upgrade_sovrin_node_test.bat',
             'scripts/restart_sovrin_node_ubuntu1604.sh',
             'scripts/restart_sovrin_node.bat',
             'scripts/install_sovrin_node.bat',
             'scripts/delete_sovrin_node.bat',
             'scripts/restart_upgrade_agent.bat',
             'scripts/install_nssm.bat'],
    cmdclass={
        'install': EnhancedInstall,
        'develop': EnhancedInstallDev
    }
)
