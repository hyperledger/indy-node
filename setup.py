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
CONFIG_FILE = os.path.join(BASE_DIR, "sovrin_config.py")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

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


class PostInstall(install):
    def run(self):
        install.run(self)
        post_install()


class PostInstallDev(develop):
    def run(self):
        develop.run(self)
        post_install()

setup(
    name='sovrin-node',
    version=__version__,
    description='Sovrin node',
    url='https://github.com/sovrin-foundation/sovrin-node.git',
    author=__author__,
    author_email='dev@evernym.us',
    license=__license__,
    keywords='Sovrin Node',
    packages=find_packages(exclude=['docs', 'docs*']) + [
        'data'],
    package_data={
        '': ['*.txt', '*.md', '*.rst', '*.json', '*.conf', '*.html',
             '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL', '*.sovrin']},
    include_package_data=True,
    data_files=[(
        (BASE_DIR, ['data/nssm.exe'])
    )],
    install_requires=['sovrin-common', 'python-dateutil'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'sovrin-client'],
    scripts=['scripts/start_sovrin_node',
             'scripts/node_control_tool.py', 
             'scripts/upgrade_sovrin_node_ubuntu1604.sh',
             'scripts/upgrade_sovrin_node_ubuntu1604_test.sh',
             'scripts/upgrade_sovrin_node.bat',
             'scripts/upgrade_sovrin_node_test.bat', 
             'scripts/install_sovrin_node.bat',
             'scripts/delete_sovrin_node.bat',
             'scripts/install_nssm.bat'],
    cmdclass={
        'install': PostInstall,
        'develop': PostInstallDev
    }
)
