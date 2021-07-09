#!/bin/bash -xe

PKG_SOURCE_PATH="$1"
VERSION="$2"
PKG_NAME=indy-plenum
IMAGE_NAME="${PKG_NAME}-build-u2004"
OUTPUT_VOLUME_NAME="${3:-"${PKG_NAME}-deb-u2004"}"
PACKAGE_VERSION="${4:-$VERSION}"

if [[ (-z "${PKG_SOURCE_PATH}") || (-z "${VERSION}") ]]; then
    echo "Usage: $0 <path-to-package-sources> <version> [<volume> [package-version]]"
    exit 1;
fi

if [ -z "$5" ]; then
    CMD="/root/build-${PKG_NAME}.sh /input ${VERSION} /output ${PACKAGE_VERSION}"
else
    CMD="$5"
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
