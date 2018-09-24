#!/usr/bin/env python

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

tests_require = ['pytest==3.3.1', 'pytest-xdist==1.22.1', 'python3-indy>=1.6.1.dev683']

setup(
    name='indy-perf-load',
    version="1.0.3",
    description='Indy node performance load',
    keywords='Indy Node performance load testing',
    packages=find_packages(),
    package_data={'': ['*.md']},
    include_package_data=True,
    install_requires=['python3-indy>=1.6.1.dev683'],
    setup_requires=['pytest-runner'],
    extras_require={'tests': tests_require},
    tests_require=tests_require,
    scripts=['perf_load/perf_processes.py', 'perf_load/perf_spike_load.py']
)
