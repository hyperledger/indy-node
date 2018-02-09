#!/usr/bin/env bash

DOCKER_IMAGE="$1"
OPENSHIFT_NAMESPACE="$2"

#OPENSHIFT_REGISTRY_ADDRESS=docker-registry.pathfinder.gov.bc.ca/v2
OPENSHIFT_REGISTRY_ADDRESS=172.30.1.1:5000

if [ -z "$DOCKER_IMAGE" ]; then
	echo -n "Enter the name of the docker image: "
	read DOCKER_IMAGE
fi

if [ -z "$OPENSHIFT_NAMESPACE" ]; then
	echo -n "Enter the name of your OpenShift project: "
	read OPENSHIFT_NAMESPACE
fi

#docker pull $DOCKERHUB_IMAGE

OPENSHIFT_IMAGE_SNIPPET=${DOCKER_IMAGE#*/}
OPENSHIFT_IMAGESTREAM_PATH=${OPENSHIFT_REGISTRY_ADDRESS}/${OPENSHIFT_NAMESPACE}/${OPENSHIFT_IMAGE_SNIPPET}

docker tag $DOCKER_IMAGE $OPENSHIFT_IMAGESTREAM_PATH
docker login ${OPENSHIFT_REGISTRY_ADDRESS} -u $(oc whoami) -p $(oc whoami -t)
docker push $OPENSHIFT_IMAGESTREAM_PATH