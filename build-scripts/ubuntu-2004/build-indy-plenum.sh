#!/bin/bash -xe

INPUT_PATH=$1
VERSION=$2
OUTPUT_PATH=${3:-.}
PACKAGE_VERSION=${4:-$VERSION}

PACKAGE_NAME=indy-plenum

# copy the sources to a temporary folder
TMP_DIR=$(mktemp -d)
cp -r ${INPUT_PATH}/. ${TMP_DIR}

# prepare the sources
cd ${TMP_DIR}/build-scripts/ubuntu-2004
./prepare-package.sh ${TMP_DIR} ${VERSION}

sed -i 's/{package_name}/'${PACKAGE_NAME}'/' "postinst"
sed -i 's/{package_name}/'${PACKAGE_NAME}'/' "prerm"

fpm --input-type "python" \
    --output-type "deb" \
    --architecture "amd64" \
    --depends "python3-pyzmq (= 18.1.0)" \
    --verbose \
    --python-package-name-prefix "python3"\
    --python-bin "/usr/bin/python3" \
    --exclude "usr/local/lib/python3.8/dist-packages/data" \
    --exclude "usr/local/bin" \
    --exclude "*.pyc" \
    --exclude "*.pyo" \
    --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
    --after-install "postinst" \
    --before-remove "prerm" \
    --name ${PACKAGE_NAME} \
    --version ${PACKAGE_VERSION} \
    --package ${OUTPUT_PATH} \
    ${TMP_DIR}

    # --python-pip "$(which pip)" \
        # ERROR:  download_if_necessary': Unexpected directory layout after easy_install. Maybe file a bug? The directory is /tmp/package-python-build-c42d23109dcca1e98d9f430a04fe79a815f10d8ed7a719633aa969424f94 (RuntimeError)

rm -rf ${TMP_DIR}
