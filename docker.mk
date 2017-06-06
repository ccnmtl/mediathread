# VERSION=1.0.0
# Docker related stuff
# use wheelhouse/requirements.txt as the sentinal so make
# knows whether it needs to rebuild the wheel directory or not
# has the added advantage that it can just pip install
# from that later on as well

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
WHEELHOUSE ?= wheelhouse
ORG ?= ccnmtl
BUILDER_IMAGE ?= ccnmtl/django.build

# make it easy to override the docker image created. eg:
#     REGISTRY=localhost:5000/ TAG=release-5 make build
# to make an image 'localhost:5000/ccnmtl/app:release-5'
# defaults to docker hub (ie, no registry specified) and no tag.

ifeq ($(origin TAG), undefined)
	IMAGE ?= $(REGISTRY)$(ORG)/$(APP)
else
	IMAGE ?= $(REGISTRY)$(ORG)/$(APP):$(TAG)
endif

$(WHEELHOUSE)/requirements.txt: $(REQUIREMENTS)
	mkdir -p $(WHEELHOUSE)
	docker run --rm \
	-v $(ROOT_DIR):/app \
	-v $(ROOT_DIR)/$(WHEELHOUSE):/wheelhouse \
	$(BUILDER_IMAGE)
	cp $(REQUIREMENTS) $@
	touch $@

# Run this target to rebuild the django image
build: $(WHEELHOUSE)/requirements.txt
	docker build -t $(IMAGE) .

.PHONY: build
