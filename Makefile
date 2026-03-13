.PHONY: build up down logs shell restart

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

# Usage: make create-admin EMAIL=admin@example.com NAME="Admin" PASSWORD=secret
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
