#!/bin/bash -xe

INPUT_PATH="$1"
VERSION="$2"
OUTPUT_PATH="${3:-.}"
PACKAGE_VERSION=${4:-$VERSION}

PACKAGE_NAME=indy-node

# copy the sources to a temporary folder
TMP_DIR="$(mktemp -d)"
cp -r "${INPUT_PATH}/." "${TMP_DIR}"

# prepare the sources
cd "${TMP_DIR}/build-scripts/ubuntu-1604"
./prepare-package.sh "${TMP_DIR}" "${VERSION}"


sed -i "s/{package_name}/${PACKAGE_NAME}/" "prerm"

fpm --input-type "python" \
    --output-type "deb" \
    --architecture "amd64" \
    --verbose \
    --python-package-name-prefix "python3" \
    --python-bin "/usr/bin/python3" \
    --exclude "*.pyc" \
    --exclude "*.pyo" \
    --depends at \
    --depends iptables \
    --depends libsodium18 \
    --no-python-fix-dependencies \
    --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
    --before-install "preinst_node" \
    --after-install "postinst_node" \
    --before-remove "prerm" \
    --name "${PACKAGE_NAME}" \
    --version ${PACKAGE_VERSION} \
    --package "${OUTPUT_PATH}" \
    "${TMP_DIR}"

rm -rf "${TMP_DIR}"
