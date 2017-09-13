from setuptools import setup, __version__

setup(
    name='indy-node-acceptance',
    version=__version__,
    description='Acceptance tests for Hyperledger Indy-Node',
    url='https://github.com/hyperledger/indy-node/tree/master/acceptance',
    author='Nikita Spivachuk',
    author_email='hyperledger-indy@lists.hyperledger.org',
    license='MIT/Apache-2.0',
    install_requires=['python3-indy==1.0.0-dev-171', 'pytest', 'pytest-asyncio',
                      'pytest-runner'],
    setup_requires=['pytest-runner']
)
