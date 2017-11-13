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
#!/usr/bin/env bash

set -e
set -x

OUTPUT_PATH="${1:-.}"

function build_from_pypi {
    PACKAGE_NAME="$1"

    if [ -z "$2" ]; then
        PACKAGE_VERSION=""
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

# build 3rd parties:
#   build_from_pypi <pypi-name> <version>

build_from_pypi timeout-decorator
