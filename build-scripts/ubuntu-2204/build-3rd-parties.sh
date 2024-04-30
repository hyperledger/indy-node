#!/usr/bin/env bash

set -e
set -x

# Ensure OUTPUT_PATH is defined as a fully qualified path
pushd $(dirname $(realpath "$0"))
OUTPUT_PATH=${1:-.}
if [ ! -d "${OUTPUT_PATH}" ]; then
    mkdir -p ${OUTPUT_PATH}
fi
OUTPUT_PATH=$(realpath ${OUTPUT_PATH})
popd

wheel2debconf="$(dirname "$(realpath "$0")")"/wheel2deb.yml

function build_from_pypi {
    PACKAGE_NAME="$1"

    if [ -z "$2" ]; then
        PACKAGE_VERSION=""
        # Get the most recent package version from PyPI to be included in the package name of the Debian artifact
        curl -X GET "https://pypi.org/pypi/${PACKAGE_NAME}/json" > "${PACKAGE_NAME}.json"
        PACKAGE_VERSION="==$(cat "${PACKAGE_NAME}.json" | jq --raw-output '.info.version')"
        rm "${PACKAGE_NAME}.json"
    else
        PACKAGE_VERSION="==$2"
    fi
    POSTINST_TMP="postinst-${PACKAGE_NAME}"
    PREREM_TMP="prerm-${PACKAGE_NAME}"
    cp postinst "${POSTINST_TMP}"
    cp prerm "${PREREM_TMP}"
    sed -i "s/{package_name}/python3-${PACKAGE_NAME}/" "${POSTINST_TMP}"
    sed -i "s/{package_name}/python3-${PACKAGE_NAME}/" "${PREREM_TMP}"

    fpm --input-type "python" \
        --output-type "deb" \
        --architecture "amd64" \
        --verbose \
        --python-package-name-prefix "python3"\
        --python-bin "/usr/bin/python3" \
        --exclude "*.pyc" \
        --exclude "*.pyo" \
        --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
        --after-install "${POSTINST_TMP}" \
        --before-remove "${PREREM_TMP}" \
        --package "${OUTPUT_PATH}" \
        "${PACKAGE_NAME}${PACKAGE_VERSION}"

    rm "${POSTINST_TMP}"
    rm "${PREREM_TMP}"
}

function build_from_pypi_wheel {
    PACKAGE_NAME=$1

    if [ -z $2 ]; then
        PACKAGE_VERSION=""
        # Get the most recent package version from PyPI to be included in the package name of the Debian artifact
        curl -X GET "https://pypi.org/pypi/${PACKAGE_NAME}/json" > "${PACKAGE_NAME}.json"
        PACKAGE_VERSION="==$(cat "${PACKAGE_NAME}.json" | jq --raw-output '.info.version')"
        rm "${PACKAGE_NAME}.json"
    else
        PACKAGE_VERSION="==$2"
    fi

    rm -rvf /tmp/wheel
    mkdir /tmp/wheel
    pushd /tmp/wheel
    pip3 wheel ${PACKAGE_NAME}${PACKAGE_VERSION}
    # Can't build cytoolz using wheel for rlp, but can't build rlp with fpm
    rm -f /tmp/wheel/cytoolz*
    wheel2deb --config ${wheel2debconf}
    popd
    mv /tmp/wheel/output/*.deb ${OUTPUT_PATH}
    rm -rvf /tmp/wheel
}

# Install any python requirements needed for the builds.
pip3 install wheel2deb 
apt-get update -y && apt-get install -y debhelper

# build 3rd parties:
#   build_from_pypi <pypi-name> <version>
# TODO duplicates list from Jenkinsfile.cd

SCRIPT_PATH="${BASH_SOURCE[0]}"
pushd `dirname ${SCRIPT_PATH}` >/dev/null

build_from_pypi_wheel importlib-metadata 3.10.1
build_from_pypi timeout-decorator 
build_from_pypi distro 1.7.0

popd >/dev/null