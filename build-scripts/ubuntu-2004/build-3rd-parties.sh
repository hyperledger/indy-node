#!/usr/bin/env bash

set -e
set -x

OUTPUT_PATH=${1:-.}

# function build_rocksdb_deb {
#     VERSION=$1
#     # VERSION_TAG="v$VERSION"
#     VERSION_TAG="rocksdb-$VERSION"
#     git clone https://github.com/evernym/rocksdb.git /tmp/rocksdb
#     cd /tmp/rocksdb
#     git checkout $VERSION_TAG
#     sed -i 's/-m rocksdb@fb.com/-m "Hyperledger <hyperledger-indy@lists.hyperledger.org>"/g' \
#         ./build_tools/make_package.sh
#     # Changed build process according to official docs with DEBUG_LEVEL=0
#     PORTABLE=1 EXTRA_CFLAGS="-fPIC" EXTRA_CXXFLAGS="-fPIC" DEBUG_LEVEL=0 make static_lib package
#     cp ./rocksdb_* $OUTPUT_PATH
#     # Install it in the system as it is needed by python-rocksdb.
#     make install
#     cd -
#     rm -rf /tmp/rocksdb
# }

function build_rocksdb_deb {
    VERSION=$1
    # VERSION_TAG="v$VERSION"
    VERSION_TAG="v$VERSION"
    git clone https://github.com/facebook/rocksdb.git /tmp/rocksdb
    cd /tmp/rocksdb
    git checkout $VERSION_TAG
    sed -i 's/-m rocksdb@fb.com/-m "Hyperledger <hyperledger-indy@lists.hyperledger.org>"/g' \
        ./build_tools/make_package.sh
    # Changed build process according to official docs with DEBUG_LEVEL=0
    PORTABLE=1 EXTRA_CFLAGS="-fPIC" EXTRA_CXXFLAGS="-fPIC" DEBUG_LEVEL=0 make static_lib package
    cp ./package/rocksdb_* $OUTPUT_PATH
    # Install it in the system as it is needed by python-rocksdb.
    make install
    cd -
    rm -rf /tmp/rocksdb
}

function build_from_pypi {
    PACKAGE_NAME=$1

    if [ -z $2 ]; then
        PACKAGE_VERSION=""
    else
        PACKAGE_VERSION="==$2"
    fi
    POSTINST_TMP=postinst-${PACKAGE_NAME}
    PREREM_TMP=prerm-${PACKAGE_NAME}
    cp postinst ${POSTINST_TMP}
    cp prerm ${PREREM_TMP}
    if [[ ${PACKAGE_NAME} =~ ^python-* ]]; then
        PACKAGE_NAME_TMP="${PACKAGE_NAME/python-/}"
    else
        PACKAGE_NAME_TMP=$PACKAGE_NAME
    fi
    sed -i 's/{package_name}/python3-'${PACKAGE_NAME_TMP}'/' ${POSTINST_TMP}
    sed -i 's/{package_name}/python3-'${PACKAGE_NAME_TMP}'/' ${PREREM_TMP}

    if [ -z $3 ]; then
        fpm --input-type "python" \
            --output-type "deb" \
            --architecture "amd64" \
            --verbose \
            --python-package-name-prefix "python3"\
            --python-bin "/usr/bin/python3" \
            --exclude "*.pyc" \
            --exclude "*.pyo" \
            --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
            --after-install ${POSTINST_TMP} \
            --before-remove ${PREREM_TMP} \
            --package ${OUTPUT_PATH} \
            ${PACKAGE_NAME}${PACKAGE_VERSION}
    else
        fpm --input-type "python" \
            --output-type "deb" \
            --architecture "amd64" \
            --python-setup-py-arguments "--zmq=bundled" \
            --verbose \
            --python-package-name-prefix "python3"\
            --python-bin "/usr/bin/python3" \
            --exclude "*.pyc" \
            --exclude "*.pyo" \
            --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
            --after-install ${POSTINST_TMP} \
            --before-remove ${PREREM_TMP} \
            --package ${OUTPUT_PATH} \
            ${PACKAGE_NAME}${PACKAGE_VERSION}
            
            # --python-pip "$(which pip)" \
        # ERROR:  download_if_necessary': Unexpected directory layout after easy_install. Maybe file a bug? The directory is /tmp/package-python-build-c42d23109dcca1e98d9f430a04fe79a815f10d8ed7a719633aa969424f94 (RuntimeError)
    fi

    rm ${POSTINST_TMP}
    rm ${PREREM_TMP}
}

# TODO duplicates list from Jenkinsfile.cd

# Build rocksdb at first
build_rocksdb_deb 5.17.2

build_from_pypi ioflo 2.0.2
build_from_pypi orderedset 2.0.3
build_from_pypi base58 2.1.0
build_from_pypi prompt-toolkit 3.0.14
build_from_pypi rlp 0.6.0
build_from_pypi sha3 0.2.1
build_from_pypi libnacl 1.7.2
build_from_pypi six 1.15.0
build_from_pypi portalocker 2.1.0
build_from_pypi sortedcontainers 2.3.0
build_from_pypi sortedcontainers 1.5.7
build_from_pypi setuptools 50.3.2
build_from_pypi python-dateutil 2.8.1
build_from_pypi semver 2.13.0
##### not referenced
##### build_from_pypi pygments 2.7.4
build_from_pypi psutil 5.8.0
# build_from_pypi pyzmq 20.0.0 bundled
build_from_pypi pyzmq 18.1.0 bundled
##### not referenced
##### build_from_pypi intervaltree 3.1.0
build_from_pypi jsonpickle 1.5.0
# TODO: add libsnappy dependency for python-rocksdb package
build_from_pypi python-rocksdb 0.7.0
build_from_pypi pympler 0.9
build_from_pypi packaging 20.8
build_from_pypi python-ursa 0.1.1
build_from_pypi pyparsing 2.4.7
build_from_pypi eth-utils 1.10.0
build_from_pypi pytest 6.2.2
build_from_pypi wcwidth 0.2.5

build_from_pypi eth-hash 0.3.1
build_from_pypi eth-typing 2.2.2
build_from_pypi leveldb 0.201
build_from_pypi ujson 4.0.2

### pytest dependencies
build_from_pypi attrs 20.3.0
build_from_pypi iniconfig 1.1.1
build_from_pypi pluggy 0.13.1
build_from_pypi py 1.10.0
build_from_pypi toml 0.10.2
build_from_pypi msgpack 0.6.2

build_from_pypi toolz 0.11.1

