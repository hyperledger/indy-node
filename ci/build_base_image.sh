#!/bin/bash
set -e

# TODO should be deprecated once base images are pushed to dockerhub

# should be called from the root of the repo

BASE_IMAGE=hyperledger/indy-core-baseci

if [ -z $(docker image inspect -f . "$BASE_IMAGE" 2>/dev/null || true) ]; then
    docker pull "$BASE_IMAGE" || make -C docker-files/baseimage clean all
fi
