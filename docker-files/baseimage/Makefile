SHELL := /bin/bash

OSNAME ?= ubuntu
DOCKER_NS ?= hyperledger

IMAGE_NAME = $(DOCKER_NS)/$(IMAGE_NAME_SHORT)
DOCKERFILE_NAME = $(IMAGE_NAME_SHORT).$(OSNAME).dockerfile

BASE_IMAGE_NAME := indy-baseimage
BASE_CI_IMAGE_NAME := indy-baseci

define create_image_if_not_exists =
	if [ -z $(shell docker image inspect -f . $(1) 2>/dev/null || true) ]; then \
		docker build -t $(1) -f $(2) .; \
	fi
endef

IMAGES = image/$(BASE_IMAGE_NAME) image/$(BASE_CI_IMAGE_NAME)
	
.PHONY: all clean base-image base-ci-image $(IMAGES)
all: base-ci-image

.PHONY: $(IMAGES)
image/%: IMAGE_NAME_SHORT = $*
$(IMAGES): image/%:
	$(call create_image_if_not_exists,$(IMAGE_NAME),$(DOCKERFILE_NAME))

.PHONY: all base-image base-ci-image $(IMAGES)
base-image: image/$(BASE_IMAGE_NAME)

.PHONY: $(IMAGES)
base-ci-image: base-image image/$(BASE_CI_IMAGE_NAME)
