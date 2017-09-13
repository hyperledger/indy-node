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
