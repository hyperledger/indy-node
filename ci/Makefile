SHELL := /bin/bash

IMAGE_NAME_16 ?= indy-node-test-sixteen
IMAGE_NAME_18 ?= indy-node-test-eighteen

.PHONY: all test_docker test_docker_1804

all: test_docker test_docker_1804

test_docker:
	$(eval UID := $(shell id -u))
	docker build -t $(IMAGE_NAME_16) --build-arg uid=$(UID) -f ubuntu-1604.dockerfile .
	$(eval REPO_PATH := $(realpath ..))
	$(eval WORKDIR := /home/indy/indy-node)
	docker run --rm -it -w $(WORKDIR) -v $(REPO_PATH):$(WORKDIR) $(IMAGE_NAME_16) \
		bash -c "pip install .[tests] && python -m pytest"

test_docker_1804:
	$(eval UID := $(shell id -u))
	docker build -t $(IMAGE_NAME_18) --build-arg uid=$(UID) -f ubuntu-1804.dockerfile .
	$(eval REPO_PATH := $(realpath ..))
	$(eval WORKDIR := /home/indy/indy-node)
	docker run --rm -it -w $(WORKDIR) -v $(REPO_PATH):$(WORKDIR) $(IMAGE_NAME_18) \
		bash -c "pip install .[tests] && python -m pytest"