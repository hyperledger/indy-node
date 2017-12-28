SHELL := /bin/bash

OSNAME ?= ubuntu
DOCKER_NS ?= hyperledger

BASE_IMAGE_NAME := indy-baseimage
BASE_CI_IMAGE_NAME := indy-baseci
BASE_CI_CORE_IMAGE_NAME := indy-core-baseci
BUILD_DIR ?= _build

DOCKER_TAG ?= $(VERSION)
VERSION_FILE = $*.version

COMMIT_SHA := $(shell git rev-parse HEAD)


IMAGES = $(BASE_IMAGE_NAME) $(BASE_CI_IMAGE_NAME) $(BASE_CI_CORE_IMAGE_NAME)

.PHONY: all publish clean clean-docker $(IMAGES)


all: $(BASE_CI_CORE_IMAGE_NAME)

$(BASE_IMAGE_NAME): $(BUILD_DIR)/$(BASE_IMAGE_NAME)

$(BASE_CI_IMAGE_NAME): $(BASE_IMAGE_NAME) $(BUILD_DIR)/$(BASE_CI_IMAGE_NAME)

$(BASE_CI_CORE_IMAGE_NAME): $(BASE_CI_IMAGE_NAME) $(BUILD_DIR)/$(BASE_CI_CORE_IMAGE_NAME)

$(BUILD_DIR)/%: %.$(OSNAME).dockerfile
	mkdir -p $(@D)
	$(eval VERSION = $(shell cat $(VERSION_FILE)))
	cp $(VERSION_FILE) $(@D)
	echo $(COMMIT_SHA) >>$(@D)/$(VERSION_FILE)
	sed 's/__VERSION_FILE__/$(@D)\/$(VERSION_FILE)/g; s/__NS__/$(DOCKER_NS)/g' $< >$(@D)/$<
	docker build -t $(DOCKER_NS)/$*:$(DOCKER_TAG) -f $(@D)/$< .
	docker images $(DOCKER_NS)/$*
	touch $@

publish: clean $(BASE_CI_CORE_IMAGE_NAME)
	$(eval _BASE_NAME := $(word 2,$^))
	$(eval VERSION := $(shell cat $(_BASE_NAME).version))
	$(eval _IMAGE_NAME := $(DOCKER_NS)/$(_BASE_NAME):$(DOCKER_TAG))

	@echo "Going to push '$(_IMAGE_NAME)' to docker hub"
	@docker login --username=$(DOCKER_HUB_USERNAME) --password=$(DOCKER_HUB_PASSWORD)
	docker push $(_IMAGE_NAME) || \
		(echo "docker push failed" && docker logout && exit 1)
	docker logout
	@echo "Done"

clean-docker:
	docker images -q hyperledger/indy-* | xargs -r docker rmi -f
	-rm -f $(patsubst %,$(BUILD_DIR)/%, $(IMAGES))

clean:
	rm -rf $(BUILD_DIR)
