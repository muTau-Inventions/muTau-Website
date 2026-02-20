PROJECT_NAME := mutau-website
COMPOSE := docker compose

.PHONY: help
help:
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "make build        Build all containers"
	@echo "make up           Start containers"
	@echo "make down         Stop containers"
	@echo "make restart      Restart services"
	@echo "make logs         Show logs"
	@echo "make shell        Open web container shell"
	@echo "make dbshell      Open PostgreSQL shell"
	@echo "make clean        Remove everything"
	@echo ""

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) down
	$(COMPOSE) up -d

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec web /bin/bash

dbshell:
	$(COMPOSE) exec db psql -U mutau -d mutau_db

clean:
	$(COMPOSE) down -v --rmi all
