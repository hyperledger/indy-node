#!/bin/bash -xe

PKG_SOURCE_PATH="$1"
VERSION="$2"
PKG_NAME=indy-node
IMAGE_NAME="${PKG_NAME}-build-u1604"
OUTPUT_VOLUME_NAME="${PKG_NAME}-deb-u1604"

if [[ (-z "${PKG_SOURCE_PATH}") || (-z "${VERSION}") ]]; then
    echo "Usage: $0 <path-to-package-sources> <version>"
    exit 1;
fi

if [ -z "$3" ]; then
    CMD="/root/build-${PKG_NAME}.sh /input ${VERSION} /output"
else
    CMD="$3"
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

