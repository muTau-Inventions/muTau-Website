.PHONY: build up down logs shell restart

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f web

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
