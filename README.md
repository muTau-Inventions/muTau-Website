# muTau-Website

Company website for **muTau-Inventions** — AI Models to FPGA, Made Simple.

Built with Flask, PostgreSQL, and Docker.

---

## Setup

```bash
git clone https://github.com/muTau-Inventions/muTau-Website.git
cd muTau-Website
```

Copy the config template and fill in your values:

```bash
cp config_template.yml config.yml
```

Set the required environment variables in `docker-compose.yml` under `web.environment`:

| Variable       | Description                            |
|----------------|----------------------------------------|
| `SECRET_KEY`   | Long random string for session signing |
| `DATABASE_URL` | Set automatically by Docker Compose    |

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Build and start:
```bash
make build
make up
```

The site is available at `http://localhost`.

---

## First Admin Account

```bash
make create-admin EMAIL=admin@example.com NAME="Max Mueller" PASSWORD=yourpassword
```

---

## Configuration (`config.yml`)

| Key                  | Description                                          |
|----------------------|------------------------------------------------------|
| `app.base_url`       | Public URL — used in emails, e.g. `https://example.com` |
| `app.docs_folder`    | Absolute path to Markdown docs (default `/app/docs`) |
| `app.research_folder`| Absolute path to research PDFs (default `/app/research`) |
| `app.log_level`      | `DEBUG` / `INFO` / `WARNING` / `ERROR`               |
| `mail.smtp_host`     | SMTP server hostname                                 |
| `mail.smtp_port`     | SMTP port (default `587`)                            |
| `mail.smtp_use_tls`  | `true` / `false`                                     |
| `mail.smtp_user`     | SMTP login                                           |
| `mail.smtp_password` | SMTP password                                        |
| `mail.from_address`  | Sender address, e.g. `muTau <noreply@example.com>`  |

---

## Content

### Documentation

Place `.md` files in `docs/`. They render automatically at `/docs` in alphabetical order.

```
docs/
├── 01-getting-started.md
└── 02-api-reference.md
```

### Research Papers

Copy the PDF into `research/`, then add it via the admin panel or:

```bash
make create-paper \
  PDF_PATH="paper.pdf" \
  TITLE="My Paper Title" \
  AUTHORS="Max Mueller, Sarah Schmidt" \
  DATE="2026-01-15" \
  DESCRIPTION="Short abstract."
```

---

## Deployment

The CI/CD pipeline builds a Docker image on every GitHub Release and deploys it to the server via SSH.

**Required repository secrets:**

| Secret           | Value                                          |
|------------------|------------------------------------------------|
| `DEPLOY_HOST`    | Server hostname or IP                          |
| `DEPLOY_USER`    | SSH user                                       |
| `DEPLOY_SSH_KEY` | Private SSH key (add public key to the server) |
| `DEPLOY_PATH`    | Absolute path to the project on the server     |

To publish a release: create a tag and release on GitHub. The workflow in `.github/workflows/release.yml` handles the rest.

On the server, `docker-compose.yml` must reference the image from `ghcr.io` (already set up). The deploy step pulls the new image and restarts only the web container without touching the database.

---

## Make Commands

```
make help
```

---

## Structure

```
.
├── docs/                    # Markdown files served at /docs
├── research/                # PDFs served at /research/pdf/<filename>
├── static/                  # CSS, JS, images
├── templates/               # Jinja2 templates
│   ├── admin/
│   ├── auth/
│   ├── email/
│   ├── errors/
│   └── legal/
├── src/mutau_website/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   ├── mail.py              # Email sending
│   ├── seed.py              # Initial product data
│   └── routes/              # Blueprints
├── config_template.yml      # Config template — copy to config.yml
├── docker-compose.yml
├── Dockerfile
└── Makefile
```