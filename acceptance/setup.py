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

from setuptools import setup

setup(
    name='indy-node-acceptance',
    version='0.0.1',
    description='Acceptance tests for Hyperledger Indy-Node',
    url='https://github.com/hyperledger/indy-node/tree/master/acceptance',
    author='Nikita Spivachuk',
    author_email='nikita.spivachuk@dsr-company.com',
    license='MIT/Apache-2.0',
    install_requires=['python3-indy==1.0.0-dev-177', 'pytest', 'pytest-asyncio',
                      'pytest-runner'],
    setup_requires=['pytest-runner']
)
