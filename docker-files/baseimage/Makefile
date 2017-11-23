SHELL := /bin/bash

OSNAME ?= ubuntu
DOCKER_NS ?= hyperledger

BASE_IMAGE_NAME := indy-baseimage
BASE_CI_IMAGE_NAME := indy-baseci
BASE_CI_CORE_IMAGE_NAME := indy-core-baseci

DOCKER_BUILD = docker build

BUILD_DIR = _build

IMAGES = $(BASE_IMAGE_NAME) $(BASE_CI_IMAGE_NAME) $(BASE_CI_CORE_IMAGE_NAME)

.PHONY: all clean clean-docker $(IMAGES)

all: $(BASE_CI_CORE_IMAGE_NAME)

$(BASE_IMAGE_NAME): $(BUILD_DIR)/$(BASE_IMAGE_NAME)

$(BASE_CI_IMAGE_NAME): $(BASE_IMAGE_NAME) $(BUILD_DIR)/$(BASE_CI_IMAGE_NAME)

$(BASE_CI_CORE_IMAGE_NAME): $(BASE_CI_IMAGE_NAME) $(BUILD_DIR)/$(BASE_CI_CORE_IMAGE_NAME)

$(BUILD_DIR)/%: %.$(OSNAME).dockerfile
	mkdir -p $(@D)
	$(DOCKER_BUILD) -t $(DOCKER_NS)/$* -f $< .
	docker images $(DOCKER_NS)/$*
	touch $@

clean-docker:
	docker images -q hyperledger/indy-* | xargs -r docker rmi -f
	-rm -f $(patsubst %,$(BUILD_DIR)/%, $(IMAGES))

clean:
	rm -rf $(BUILD_DIR)
