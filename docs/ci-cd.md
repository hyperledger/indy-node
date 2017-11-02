# Continues integration/delivery

- Unit/Integration tests are executed for each PR
- Each PR needs to be reviewed
- PR can be merged only after all tests pass and code is reviewed
- We use pipeline in code approach and Jenkins as our main CI/CD server
- CI part of the pipeline (running tests for each PR) is defined in `Jenkinsfile.ci` file. 
- CI part is run on Hyperledger Jenkins, so it is public and open as every contributor needs to see results of the tests run for his or her PR.
- CD part of the pipeline (running tests for each PR) is defined in `Jenkinsfile.cd` file.
- CD part is run on a private Jenkins server dealing with issuing and uploading new builds. 

#### Branches

- Master branch contains the latest changes. All PRs usually need to be sent to master.
- Stable branch contains latest releases (https://github.com/hyperledger/indy-node/releases). Hotfixes need to be sent to stable.

#### Builds

What artifacts are produced after each push
- to `master` branch:
    - indy-plenum:
        - indy-plenum-dev in [pypi](https://pypi.python.org/pypi/indy-plenum-dev) 
        - indy-plenum deb package in [https://repo.sovrin.org/deb xenial master-latest](https://repo.sovrin.org/lib/apt/xenial/master-latest/)
        - indy-plenum release tag (https://github.com/hyperledger/indy-plenum/releases)
    - indy-node:
        - indy-node-dev in [pypi](https://pypi.python.org/pypi/indy-node-dev)
        - indy-node deb package in [https://repo.sovrin.org/deb xenial master-latest](https://repo.sovrin.org/lib/apt/xenial/master-latest/)
        - indy-node deb package in [https://repo.sovrin.org/deb xenial master](https://repo.sovrin.org/lib/apt/xenial/master/)
        - indy-plenum deb package in [https://repo.sovrin.org/deb xenial master](https://repo.sovrin.org/lib/apt/xenial/master/) (copied from master-latest)
        - indy-node release tag (https://github.com/hyperledger/indy-node/releases)
- to `stable` branch:
    - indy-plenum:
        - indy-plenum in [pypi](https://pypi.python.org/pypi/indy-plenum) 
        - indy-plenum deb package in [https://repo.sovrin.org/deb xenial rc-latest](https://repo.sovrin.org/lib/apt/xenial/rc-latest/)
        - indy-plenum release tag (https://github.com/hyperledger/indy-plenum/releases)
    - indy-node:
        - indy-node in [pypi](https://pypi.python.org/pypi/indy-node)
        - indy-node deb package in [https://repo.sovrin.org/deb xenial rc-latest](https://repo.sovrin.org/lib/apt/xenial/rc-latest/)
        - indy-node deb package in [https://repo.sovrin.org/deb xenial rc](https://repo.sovrin.org/lib/apt/xenial/rc/)
        - indy-plenum deb package in [https://repo.sovrin.org/deb xenial rc](https://repo.sovrin.org/lib/apt/xenial/rc/) (copied from rc-latest)
        - indy-node release tag (https://github.com/hyperledger/indy-node/releases)
        - after build is tested and approved:
            - indy-node deb package in [https://repo.sovrin.org/deb xenial stable](https://repo.sovrin.org/lib/apt/xenial/stable/) (copied from rc)
            - indy-plenum deb package in [https://repo.sovrin.org/deb xenial stable](https://repo.sovrin.org/lib/apt/xenial/stable/) (copied from rc)

Use cases for artifacts
- Pypi artifacts can be used for dev experiments, but not intended to be used for production.
- Using deb packages is recommended way to be used for a test/production pool on Ubuntu.
- indy-node deb package from [https://repo.sovrin.org/deb xenial stable](https://repo.sovrin.org/lib/apt/xenial/stable/) 
is one and the only official stable release that can be used for production. 

#### Versioning

- Please note, that we are using semver-like approach for versioning (major, minor, build) for each of the components. 
- Major and minor parts are set in the code (see [\_\_metadata\_\_.py](https://github.com/hyperledger/indy-node/blob/master/indy_node/__metadata__.py)). They must be incremented for new releases manually from code if needed.
- Build part is incremented with each build on Jenkins (so it always increases, but may be not sequentially)  
- Each dependency (including indy-plenum and indy-anoncreds) has a strict version (see [setup.py](https://github.com/hyperledger/indy-node/blob/master/setup.py))
- If you install indy-node (either from pypi, or from deb package), the specified in setup.py version of indy-plenum is installed.
- Master and Stable builds usually have different versions.
- Differences in master and stable code:
    - `setup.py`:
        - dev suffix in project names and indy-plenum dependency in master; no suffixes in stable
        - different versions of indy-plenum dependency
    - different versions in migrations scripts  

#### Static Code Validation

- We use flake8 for static code validation.
- It's run against every PR. PR fails if there are some static code validation errors.
- Not all checks are enabled (have a look at `.flake8` file at the project root)
- You can run static code validation locally:
    - Install flake8: `pip install flake8`
    - Run validation on the root folder of the project: `flake8 .` 

## How to Create a Stable Release

- Create a new branch based on `stable` in indy-plenum
- Merge `master` branch into this new branch
- Make sure that proper versions and names are used (without dev suffixes) 
- Raise a PR to indy-plenum's stable, and wait until code is reviewed and merged. So, a new release candidate of plenum is created.
- Create a new branch based on `stable` in indy-node
- Merge `master` branch into this new branch
- Change indy-plenum's dependency version to the new one in indy-node's [setup.py](https://github.com/hyperledger/indy-node/blob/stable/setup.py).
- Make sure that proper versions and names are used (without dev suffixes) 
- Raise a PR to indy-node's stable, and wait until code is reviewed and merged. So, a new release candidate of indy-node is created.
- QA needs to test this release candidate from [https://repo.sovrin.org/deb xenial rc](https://repo.sovrin.org/lib/apt/xenial/rc/)
- QA approves the release candidate of indy-plenum.
- QA approves the release candidate of indy-node. So, a new stable release is created.