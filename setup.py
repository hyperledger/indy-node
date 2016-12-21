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

METADATA = os.path.join(SETUP_DIRNAME, 'sovrin_node', '__metadata__.py')
# Load the metadata using exec() so we don't trigger an import of ioflo.__init__
exec(compile(open(METADATA).read(), METADATA, 'exec'))


setup(
    name='sovrin-node',
    version=__version__,
    description='Sovrin node',
    url='https://github.com/sovrin-foundation/sovrin-node.git',
    author=__author__,
    author_email='dev@evernym.us',
    license=__license__,
    keywords='Sovrin Node',
    install_requires=['sovrin-common'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'sovrin-client'],
    packages=find_packages(exclude=['test', 'test.*',
                                      'docs', 'docs*']),
    package_data={
        '':       ['*.txt',  '*.md', '*.rst', '*.json', '*.conf', '*.html',
                   '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL']},
)
