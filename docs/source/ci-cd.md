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

### Feature Release

#### 1. Release Candidate Preparation

1. [**Maintainer**]
    - Create `release-X.Y.Z` branch from `stable` (during the first RC preparation only).
2. [**Contributor**]
    - Create `rc-X.Y.Z.rcN` branch from `release-X.Y.Z` (`N` starts from `1` and is incremented for each new RC).
    - Apply necessary changes from `master` (either `merge` or `cherry-pick`).
    - (_optional_) [`indy-node`] Set **stable** (just X.Y.Z) `indy-plenum` version in `setup.py`.
    - Set the package version `./bump_version.sh X.Y.Z.rcN`.
    - Commit, push and create a PR to `release-X.Y.Z`.
3. Until PR is merged:
    1. [**build server**]
        - Run CI for the PR and notifies GitHub.
    2. [**Maintainer**]
        - Review the PR.
        - Either ask for changes or merge.
    3. [**Contributor**]
        - (_optional_) Update the PR if either CI failed or reviewer asked for changes.
        - (_optional_) [**indy-node**] Bump `indy-plenum` version in `setup.py` if changes require new `indy-plenum` release.

#### 2. Release Candidate Acceptance

**Note** If any of the following steps fails new release candidate should be prepared.

1. [**Maintainer**]
    - **Start release candidate pipeline manually**.
2. [**build server**]
    - Checkout the repository.
    - Publish to PyPI as `X.Y.Z.rcN`.
    - Bump version locally to `X.Y.Z`, commit and push as the `release commit` to remote.
    - Build debian packages:
        - for the project: source code version would be `X.Y.Z`, debian package version `X.Y.Z~rcN`;
        - for the 3rd party dependencies missed in the official debian repositories.
    - Publish the packages to `rc-latest` debian channel.
    - [`indy-node`] Copy the package along with its dependencies (including `indy-plenum`)
      from `rc-latest` to `rc` channel.
    - [`indy-node`] Run system tests for the `rc` channel.
    - Create **release PR** from `release-X.Y.Z` (that points to `release commit`) branch to `stable`.
    - Notify maintainers.
    - Wait for an approval to proceed. **It shouldn't be provided until `release PR` passes all necessary checks** (e.g. DCO, CI testing, maintainers reviews etc.).
3. [**build server**]
    - Run CI for the PR and notify GitHub.
4. [**QA**]
    - (_optional_) Perform additional testing.
5. [**Maintainer**]
    - Review the PR but **do not merge it**.
    - If approved: let build server to proceed.
    - Otherwise: stop the pipeline.
6. [**build server**]
    - If approved:
        - perform fast-forward merge;
        - create and push tag `vX.Y.Z`;
        - Notify maintainers.
    - Otherwise rollback `release commit` by moving `release-X.Y.Z` to its parent.

#### 3. Publishing

1. [**build server**] triggered once the `release PR` is merged
    - Publish to PyPI as `X.Y.Z`.
    - Download and re-pack debian package `X.Y.Z~rcN` (from `rc-latest` channel) to `X.Y.Z` changing only the package name.
    - Publish the package to `rc-latest` debian channel.
    - Copy the package along with its dependencies from `rc-latest` to `stable-latest` channel.
    - [`indy-node`] Copy the package along with its dependencies (including `indy-plenum`) from `stable-latest` to `stable` channel.
    - [`indy-node`] Run system tests for the `stable` channel.
    - Notify maintainers.

#### 4. New Development Cycle Start

1. [**Contributor**]:
    - Create PR to `master` with version bump to `X'.Y'.Z'.dev0`, where `X'.Y'.Z'` is next target release version. Usually it increments one of `X`, `Y` or `Z` and resets lower parts (check [SemVer](https://semver.org/) for more details), e.g.:
        - `X.Y.Z+1` - bugfix release
        - `X.Y+1.0` - feature release, backwards compatible API additions/changes
        - `X+1.0.0` - major release, backwards incompatible API changes

### Hotfix Release

Hotfix release is quite similar except the following difference:
  - hotfix branches named `hotfix-X.Y.Z`;
  - `master` usually is not merged since hotfixes (as a rule) should include only fixes for stable code.
