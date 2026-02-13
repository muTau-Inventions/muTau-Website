IMAGE_NAME := my-python-app
CONTAINER_NAME := my-python-app-container
PORT := 80

.PHONY: build run stop rm logs bash

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --name $(CONTAINER_NAME) -p $(PORT):80 --rm $(IMAGE_NAME)

stop:
	docker stop $(CONTAINER_NAME) || true

rm:
	docker rm $(CONTAINER_NAME) || true

logs:
	docker logs -f $(CONTAINER_NAME)

bash:
	docker exec -it $(CONTAINER_NAME) /bin/bash
