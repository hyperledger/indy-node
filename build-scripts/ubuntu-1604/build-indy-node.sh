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

#!/bin/bash -xe

INPUT_PATH="$1"
VERSION="$2"
OUTPUT_PATH="${3:-.}"

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
    --no-python-fix-dependencies \
    --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
    --before-install "preinst_node" \
    --after-install "postinst_node" \
    --before-remove "prerm" \
    --name "${PACKAGE_NAME}" \
    --package "${OUTPUT_PATH}" \
    "${TMP_DIR}"

rm -rf "${TMP_DIR}"
