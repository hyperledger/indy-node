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

# resolve metadata
metadata = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'perf_load', '__version__.py'), 'r') as f:
    exec(f.read(), metadata)

tests_require = ['pytest==3.3.1', 'pytest-xdist==1.22.1', 'python3-indy>=1.8.3.dev1103']

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
    packages=find_packages(),
    package_data={'': ['*.md']},
    include_package_data=True,
    install_requires=['python3-indy>=1.8.3.dev1103', 'PyYAML>=3.12', 'libnacl==1.6.1', 'base58'],
    setup_requires=['pytest-runner'],
    extras_require={'tests': tests_require},
    tests_require=tests_require,
    scripts=['perf_load/perf_processes.py', 'perf_load/perf_spike_load.py']
)
