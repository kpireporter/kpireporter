DOCKER_REPO ?= kpireporter/kpireporter
DOCKER_TAG  ?= 0.0.1

.PHONY: build
build: plugin-requirements.txt
	docker build -f docker/Dockerfile -t $(DOCKER_REPO):$(DOCKER_TAG) .

.PHONY: build-dev
build-dev: plugin-requirements.txt
	docker build -f docker/Dockerfile --target dev -t $(DOCKER_REPO):dev .

plugin-requirements.txt: $(wildcard plugins/*/requirements.txt)
	cat $^ | sort | uniq > $@
