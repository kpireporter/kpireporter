DOCKER_REPO ?= diurnalist/kpireporter
DOCKER_TAG  ?= 0.0.1

.PHONY: build
build: plugin-requirements.txt
	docker build -f docker/Dockerfile -t $(DOCKER_REPO):$(DOCKER_TAG) .

plugin-requirements.txt: $(wildcard plugins/*/requirements.txt)
	cat $^ | sort | uniq > $@
