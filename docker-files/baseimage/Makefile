SHELL := /bin/bash

OSNAME ?= ubuntu
DOCKER_NS ?= hyperledger

BASE_IMAGE_NAME := indy-baseimage
BASE_CI_IMAGE_NAME := indy-baseci

DOCKER_BUILD = docker build

BUILD_DIR = _build

IMAGES = $(BASE_IMAGE_NAME) $(BASE_CI_IMAGE_NAME)

.PHONY: all $(IMAGES) clean

all: base-ci-image

$(BASE_IMAGE_NAME): $(BUILD_DIR)/$(BASE_IMAGE_NAME)

$(BASE_CI_IMAGE_NAME): $(BASE_IMAGE_NAME) $(BUILD_DIR)/$(BASE_CI_IMAGE_NAME)

$(BUILD_DIR)/%: $(BUILD_DIR)/%.$(OSNAME).dockerfile $(BUILD_DIR)/scripts
	$(DOCKER_BUILD) -t $(DOCKER_NS)/$* -f $< $(<D)
	docker images $(DOCKER_NS)/$*
	touch $@

$(BUILD_DIR)/%.$(OSNAME).dockerfile: %.$(OSNAME).dockerfile
	cp -f $< $(@D)

$(BUILD_DIR)/scripts:
	mkdir -p $(@D)
	cp -r $(@F) $(@D)

clean-docker:
	docker images -q hyperledger/indy-* | xargs -r docker rmi -f
	-rm -f $(patsubst %,$(BUILD_DIR)/%, $(IMAGES))

clean:
	rm -rf $(BUILD_DIR)
