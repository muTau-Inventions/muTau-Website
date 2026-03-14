.PHONY: help build up down logs shell restart

# Default target
help:
	@echo ""
	@echo "  muTau-Website  (dev)"
	@echo ""
	@echo "  Usage: make <target>"
	@echo ""
	@echo "    build     Build or rebuild the Docker image"
	@echo "    up        Start all containers in the background"
	@echo "    down      Stop and remove all containers"
	@echo "    reset     Removes Volumes and Research papers"
	@echo "    restart   Restart only the web container (no rebuild)"
	@echo "    logs      Follow live container logs  (Ctrl+C to exit)"
	@echo "    shell     Open a bash shell inside the web container"
	@echo ""
	@echo "  All targets use docker-compose.dev.yml."
	@echo "  Admin account is created automatically from env vars on first start."
	@echo ""

COMPOSE = docker compose -f docker-compose.dev.yml

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

reset:
	$(COMPOSE) down -v
	rm -rf research/*

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec web bash

restart:
	$(COMPOSE) restart web