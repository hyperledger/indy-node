SHELL := /bin/bash

IMAGE_NAME ?= indy-node-test

.PHONY: all test_docker

all: test_docker

test_docker:
	$(eval UID := $(shell id -u))
	docker build -t $(IMAGE_NAME) --build-arg uid=$(UID) -f ubuntu.dockerfile .
	$(eval REPO_PATH := $(realpath ..))
	$(eval WORKDIR := /home/indy/indy-node)
	docker run --rm -it -w $(WORKDIR) -v $(REPO_PATH):$(WORKDIR) $(IMAGE_NAME) \
		bash -c "pip install .[tests] && python -m pytest"
