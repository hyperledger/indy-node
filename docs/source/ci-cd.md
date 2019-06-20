# Continuous Integration / Delivery

#### Branches

- `master` branch contains the latest changes. All PRs usually need to be sent to master.
- `stable` branch contains latest releases (https://github.com/hyperledger/indy-node/releases). Hotfixes need to be sent to both stable and master.
- `release-*` branches hold release candidates during release workflow
- `hotfix-*` branches hold release candidates during hotfix workflow

#### Pull Requests

- Each PR needs to be reviewed.
- PR can be merged only after all tests pass and code is reviewed.

## Continuous Integration

- for each PR we execute:
    - static code validation
    - Unit/Integration tests
- We use pipeline in code approach and Jenkins as our main CI/CD server.
- CI part of the pipeline (running tests for each PR) is defined in `Jenkinsfile.ci` file.
- CI part is run on Hyperledger and Sovrin Foundation Jenkins servers, so they are public and open as every contributor needs to see results of the tests run for his or her PR.

#### Static Code Validation

- We use flake8 for static code validation.
- It's run against every PR. PR fails if there are some static code validation errors.
- Not all checks are enabled (have a look at `.flake8` file at the project root)
- You can run static code validation locally:
    - Install flake8: `pip install flake8`
    - Run validation on the root folder of the project: `flake8 .`


## Continuous Delivery

- CD part of the pipeline is defined in `Jenkinsfile.cd` file.
- CD part is run on Sovrin Foundation Jenkins server dealing with issuing and uploading new builds.

#### Builds

What artifacts are produced after each push
- to `master` branch:
    - all artifacts include developmental release segment `devN` in their version
    - indy-plenum:
        - indy-plenum in [pypi](https://pypi.python.org/pypi/indy-plenum)
        - indy-plenum deb package in [`https://repo.sovrin.org/deb xenial master-latest`](https://repo.sovrin.org/lib/apt/xenial/master-latest/)
    - indy-node:
        - indy-node in [pypi](https://pypi.python.org/pypi/indy-node)
        - indy-node deb package in [`https://repo.sovrin.org/deb xenial master-latest`](https://repo.sovrin.org/lib/apt/xenial/master-latest/)
        - indy-node deb package in [`https://repo.sovrin.org/deb xenial master`](https://repo.sovrin.org/lib/apt/xenial/master/) (copied from `master-latest`)
        - indy-plenum deb package in [`https://repo.sovrin.org/deb xenial master`](https://repo.sovrin.org/lib/apt/xenial/master/) (copied from `master-latest`)
- to `release-*` and `hotfix-*` branches:
    - all artifacts include pre-release segment `rcN` in their version
    - indy-plenum:
        - indy-plenum in [pypi](https://pypi.python.org/pypi/indy-plenum)
        - indy-plenum deb package in [`https://repo.sovrin.org/deb xenial rc-latest`](https://repo.sovrin.org/lib/apt/xenial/rc-latest/)
    - indy-node:
        - indy-node in [pypi](https://pypi.python.org/pypi/indy-node)
        - indy-node deb package in [`https://repo.sovrin.org/deb xenial rc-latest`](https://repo.sovrin.org/lib/apt/xenial/rc-latest/)
        - indy-node deb package in [`https://repo.sovrin.org/deb xenial rc`](https://repo.sovrin.org/lib/apt/xenial/rc/) (copied from `rc-latest`)
        - indy-plenum deb package in [`https://repo.sovrin.org/deb xenial rc`](https://repo.sovrin.org/lib/apt/xenial/rc/) (copied from `rc-latest`)
- to `stable` branch:
    - indy-plenum:
        - indy-plenum in [pypi](https://pypi.python.org/pypi/indy-plenum)
        - indy-plenum deb package in [`https://repo.sovrin.org/deb xenial stable-latest`](https://repo.sovrin.org/lib/apt/xenial/stable-latest/)
        - indy-plenum release tag (https://github.com/hyperledger/indy-plenum/releases)
    - indy-node:
        - indy-node in [pypi](https://pypi.python.org/pypi/indy-node)
        - indy-node deb package in [`https://repo.sovrin.org/deb xenial stable-latest`](https://repo.sovrin.org/lib/apt/xenial/stable-latest/) (re-packed from `rc-latest`)
        - indy-node deb package in [`https://repo.sovrin.org/deb xenial stable`](https://repo.sovrin.org/lib/apt/xenial/stable/) (copied from `rc-latest`)
        - indy-plenum deb package in [`https://repo.sovrin.org/deb xenial stable`](https://repo.sovrin.org/lib/apt/xenial/stable/) (copied from `stable-latest`)
        - indy-node release tag (https://github.com/hyperledger/indy-node/releases)

Use cases for artifacts
- PyPI artifacts can be used for development experiments, but not intended to be used for production.
- Using deb packages is recommended way to be used for a test/production pool on Ubuntu.
    - indy-node deb package from [`https://repo.sovrin.org/deb xenial stable`](https://repo.sovrin.org/lib/apt/xenial/stable/)
    is one and the only official stable release that can be used for production (stable version).
    - indy-node deb package from [`https://repo.sovrin.org/deb xenial master`](https://repo.sovrin.org/lib/apt/xenial/master/)
    contains the latest changes (from master branch). It's not guaranteed that that this code is stable enough.

#### Packaging

##### Supported platforms and OSes

- Ubuntu 16.04 on x86_64

##### Build scripts

We use [fpm](https://github.com/jordansissel/fpm) for packaging python code into deb packages. Build scripts are placed in `build-scripts` folders:
- https://github.com/hyperledger/indy-node/blob/master/build-scripts
- https://github.com/hyperledger/indy-plenum/blob/master/build-scripts

We also pack some 3rd parties dependencies which are not presented in canonical ubuntu repositories:
- https://github.com/hyperledger/indy-node/blob/master/build-scripts/ubuntu-1604/build-3rd-parties.sh
- https://github.com/hyperledger/indy-plenum/blob/master/build-scripts/ubuntu-1604/build-3rd-parties.sh

Each `build-scripts` folder includes `Readme.md`. Please check them for more details.

#### Versioning

- Please note, that we are using versioning that satisfies [PEP 440](https://www.python.org/dev/peps/pep-0440) with release segment as `MAJOR.MINOR.PATCH` that satisfies [SemVer](https://semver.org/) as well.
- Version is set in the code (see [\_\_version\_\_.json](https://github.com/hyperledger/indy-node/blob/master/indy_node/__version__.json)).
- Version is bumped for new releases / hotfixes either manually or using [bump_version.sh](https://github.com/hyperledger/indy-node/blob/master/indy_node/bump_version.sh) script. The latter is preferred.
- During development phase version includes developmental segment `devN`, where `N` is set for CD pipeline artifacts as incremented build number of build server jobs. In the source code it is just equal to `0` always.
- During release preparation phase (release / hotfix workflows) version includes pre-release segment `rcN`, where `N>=1` and set in the source code by developers.
- Each dependency (including indy-plenum) has a strict version (see [setup.py](https://github.com/hyperledger/indy-node/blob/master/setup.py))
- If you install indy-node (either from pypi, or from deb package), the specified in setup.py version of indy-plenum is installed.
- Master and Stable share the same versioning scheme.
- Differences in master and stable code:
    - `setup.py`: different versions of indy-plenum dependency
    - different versions in migrations scripts


##### For releases `< 1.7.0` (deprecated)
- Please note, that we are using semver-like approach for versioning (major, minor, build) for each of the components.
- Major and minor parts are set in the code (see [\_\_metadata\_\_.py](https://github.com/hyperledger/indy-node/blob/master/indy_node/__metadata__.py)). They must be incremented for new releases manually from code if needed.
- Build part is incremented with each build on Jenkins (so it always increases, but may be not sequentially)
- Each dependency (including indy-plenum) has a strict version (see [setup.py](https://github.com/hyperledger/indy-node/blob/master/setup.py))
- If you install indy-node (either from pypi, or from deb package), the specified in setup.py version of indy-plenum is installed.
- Master and Stable builds usually have different versions.
- Differences in master and stable code:
    - `setup.py`:
        - dev suffix in project names and indy-plenum dependency in master; no suffixes in stable
        - different versions of indy-plenum dependency
    - different versions in migrations scripts

## Release workflow

1. Release candidate preparation
    1. [**Maintainer**] Creates a new release branch `release-X.Y.Z` based on `stable`.
    2. [**Contributor**]
        - Creates a new release candidate branch (e.g. `rc-X.Y.Z.rc1`) based on that release branch.
        - Merges `master` branch.
        - Sets stable version of `indy-plenum` in `setup.py` (for `indy-node` only).
        - Sets new version `X.Y.Z.rc1` (`./bump_version.sh X.Y.Z.rc1`).
        - Commits and pushes changes.
        - Creates a release candidate PR to `release-X.Y.Z`.
    3. [**Maintainer**] Waits for CI, reviews the release candidate PR and either merges the PR or asks for changes.
2. Release candidate acceptance
    1. [**Maintainer**] Once the release candidate PR is merged the maintainer **starts release candidate pipeline manually**.
    2. [**build server**] Once the CD pipeline is started (manually triggered) for branch `release-X.Y.Z` it does the following:
        - creates and pushes release commit to `release-X.Y.Z`;
        - publishes release candidates packages to PyPI and debian `rc` components;
        - performs system testing (`indy-node` only);
        - creates a release PR to merge `release-X.Y.Z` to `stable`;
        - waits for an approval to proceed.
    3. [**Maintainer/QA**] Waits for CI, reviews the release PR and either approves or rejects:
        - may run additional tests against the release candidate before approval;
        - in case of approval lets build server to proceed but **does not merge the release PR manually**;
        - otherwise stops the pipeline and previous steps are repeated for new release candidate `X.Y.Z.rc1` and possible future ones.
    4. [**build server**]
        - once it is approved to proceed performs fast-forward merging to stable and creates tag `vX.Y.Z`;
        - otherwise rollbacks release commit pushed to release branch `release-X.Y.Z`.
3. Publishing
    1. [**build server**] Once the release PR is merged stable pipeline is triggered and it:
        - publishes to PyPI;
        - re-packs `rc` debian package and publishes to debian `stable` components.

Hotfix releases are quite similar except the following difference:
  - hotifx branches `hotfix-X.Y.Z` are created from git tag `vX.Y.(Z-1)`;
  - `master` is not merged since hotfixes (as a rule) should include only fixes for stable code.
