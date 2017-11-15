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

PKG_SOURCE_PATH="$1"
VERSION="$2"
PKG_NAME=indy-node
IMAGE_NAME="${PKG_NAME}-build-u1604"
OUTPUT_VOLUME_NAME="${3:-"${PKG_NAME}-deb-u1604"}"

if [[ (-z "${PKG_SOURCE_PATH}") || (-z "${VERSION}") ]]; then
    echo "Usage: $0 <path-to-package-sources> <version> <volume>"
    exit 1;
fi

if [ -z "$4" ]; then
    CMD="/root/build-${PKG_NAME}.sh /input ${VERSION} /output"
else
    CMD="$4"
fi

docker build -t "${IMAGE_NAME}" -f Dockerfile .
docker volume create --name "${OUTPUT_VOLUME_NAME}"

docker run \
    -i \
    --rm \
    -v "${PKG_SOURCE_PATH}:/input" \
    -v "${OUTPUT_VOLUME_NAME}:/output" \
    -e PKG_NAME="${PKG_NAME}" \
    "${IMAGE_NAME}" \
    $CMD

