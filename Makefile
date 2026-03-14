.PHONY: help build up down logs shell restart create-admin create-paper

# Default target — show help
help:
	@echo ""
	@echo "  muTau-Website"
	@echo ""
	@echo "  Usage: make <target> [OPTIONS]"
	@echo ""
	@echo "  Container"
	@echo "    build           Build or rebuild the Docker image"
	@echo "    up              Start all containers in the background"
	@echo "    down            Stop and remove all containers"
	@echo "    restart         Restart only the web container (no rebuild)"
	@echo "    logs            Follow live container logs  (Ctrl+C to exit)"
	@echo "    shell           Open a bash shell inside the web container"
	@echo ""
	@echo "  Admin"
	@echo "    create-admin    Create an admin user"
	@echo "                    EMAIL=  NAME=  PASSWORD="
	@echo ""
	@echo "  Content"
	@echo "    create-paper    Add a research paper to the database"
	@echo "                    PDF_PATH=  TITLE=  AUTHORS=  DATE=  DESCRIPTION="
	@echo "                    (PDF must already be in research/ folder)"
	@echo ""

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec web bash

restart:
	docker compose restart web

# Usage: make create-admin EMAIL=admin@example.com NAME="Max Mueller" PASSWORD=secret
create-admin:
	docker compose exec web python -c "\
import os, sys; sys.path.insert(0, '/app/src'); \
from mutau_website import create_app; \
from mutau_website.extensions import db; \
from mutau_website.models import User; \
app = create_app(); \
app.app_context().push(); \
email = '$(EMAIL)'; \
name = '$(NAME)'; \
pw = '$(PASSWORD)'; \
u = User(email=email, name=name, is_admin=True, is_verified=True); \
u.set_password(pw); \
db.session.add(u); \
db.session.commit(); \
print('Admin created:', email)"

# Usage: make create-paper PDF_PATH="paper.pdf" TITLE="..." AUTHORS="..." DATE="2026-01-15" DESCRIPTION="..."
create-paper:
	docker compose exec web python -c "\
import os, sys; sys.path.insert(0, '/app/src'); \
from dateutil import parser; \
from mutau_website import create_app; \
from mutau_website.extensions import db; \
from mutau_website.models import Paper; \
app = create_app(); \
app.app_context().push(); \
pdf_path = '$(PDF_PATH)'; \
title = '$(TITLE)'; \
authors = '$(AUTHORS)'; \
date = parser.parse('$(DATE)').date(); \
description = '$(DESCRIPTION)'; \
p = Paper(pdf_path=pdf_path, title=title, authors=authors, date=date, description=description); \
db.session.add(p); \
db.session.commit(); \
print('Paper created:', title)"