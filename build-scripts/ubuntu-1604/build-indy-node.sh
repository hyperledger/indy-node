#!/usr/bin/env bash

set -x
set -e

INPUT_PATH=$1
OUTPUT_PATH=${2:-.}

PACKAGE_NAME=indy-node
POSTINST_TMP=postinst-${PACKAGE_NAME}
PREREM_TMP=prerm-${PACKAGE_NAME}

cp prerm ${PREREM_TMP}
sed -i 's/{package_name}/'${PACKAGE_NAME}'/' ${PREREM_TMP}

fpm --input-type "python" \
    --output-type "deb" \
    --architecture "amd64" \
    --verbose \
    --python-package-name-prefix "python3" \
    --python-bin "/usr/bin/python3" \
    --exclude "*.pyc" \
    --exclude "*.pyo" \
    --no-python-fix-dependencies \
    --maintainer "Sovrin Foundation <repo@sovrin.org>" \
    --before-install "preinst_node" \
    --after-install "postinst_node" \
    --before-remove ${PREREM_TMP} \
    --name ${PACKAGE_NAME} \
    --package ${OUTPUT_PATH} \
    ${INPUT_PATH}

rm ${PREREM_TMP}
