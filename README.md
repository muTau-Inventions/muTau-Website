# muTau-Website

Company website for **muTau-Inventions** — AI Models to FPGA, Made Simple.

Built with Flask, PostgreSQL, and Docker.

---

## Development

```bash
git clone https://github.com/muTau-Inventions/muTau-Website.git
cd muTau-Website
cp config_template.yml config.yml   # then edit config.yml
```

Adjust the env vars in `docker-compose.dev.yml` (SECRET_KEY, ADMIN_* credentials), then:

```bash
make build
make up
```

Site: `http://localhost` · pgAdmin: `http://localhost:5050`

All make commands use `docker-compose.dev.yml`. Run `make help` for a full list.

### Live editing

`templates/` and `static/` are bind-mounted in dev, so changes are visible after
`make restart` — no rebuild needed.

### First admin account

Set these env vars in `docker-compose.dev.yml` before the first `make up`:

```yaml
ADMIN_EMAIL: admin@example.com
ADMIN_NAME: Admin
ADMIN_PASSWORD: yourpassword
```

The account is created automatically on first startup if no admin exists yet.

---

## Configuration (`config.yml`)

`config.yml` is never committed (it's in `.gitignore`). Copy from the template:

```bash
cp config_template.yml config.yml
```

| Key                   | Description                                               |
|-----------------------|-----------------------------------------------------------|
| `app.base_url`        | Public URL — used in email links, e.g. `https://example.com` |
| `app.log_level`       | `DEBUG` / `INFO` / `WARNING` / `ERROR`                    |
| `mail.smtp_host`      | SMTP server                                               |
| `mail.smtp_port`      | SMTP port (default `587`)                                 |
| `mail.smtp_use_tls`   | `true` / `false`                                          |
| `mail.smtp_user`      | SMTP login                                                |
| `mail.smtp_password`  | SMTP password                                             |
| `mail.from_address`   | Sender, e.g. `muTau <noreply@example.com>`               |

---

## Content

### Documentation

Place `.md` files in `docs/`. They render at `/docs` in alphabetical order.

```
docs/
├── 01-getting-started.md
└── 02-api-reference.md
```

### Research Papers

Drop PDFs into `research/` and add them via the admin panel at `/admin/papers`.

---

## Production Deployment

Deployments are triggered automatically by publishing a GitHub Release.
The CI workflow (`.github/workflows/release.yml`) builds and pushes a Docker image
to `ghcr.io/mutau-inventions/mutau-website:latest`, then deploys via SSH.

**Required repository secrets:**

| Secret           | Value                                          |
|------------------|------------------------------------------------|
| `DEPLOY_HOST`    | Server hostname or IP                          |
| `DEPLOY_USER`    | SSH user                                       |
| `DEPLOY_SSH_KEY` | Private SSH key (add public key to the server) |
| `DEPLOY_PATH`    | Absolute path to the project on the server     |

**On the server**, only three files are needed:

```
/your/deploy/path/
├── config.yml        ← your live config (not in repo)
├── docs/             ← bind-mounted into container
├── research/         ← bind-mounted into container
└── docker-compose.yml
```

`templates/` and `static/` are baked into the image — no volume mounts needed.

To deploy manually:

```bash
docker compose pull
docker compose up -d --no-deps web
```

---

## Project Structure

```
.
├── docs/                      # Markdown docs (runtime mount)
├── research/                  # Research PDFs (runtime mount, gitignored)
├── static/                    # CSS, JS, images (baked into image)
├── templates/                 # Jinja2 templates (baked into image)
│   ├── admin/
│   ├── auth/
│   ├── email/
│   ├── errors/
│   └── legal/
├── src/mutau_website/
│   ├── __init__.py            # App factory, admin seed
│   ├── models.py              # Database models
│   ├── mail.py                # Email sending (threaded)
│   ├── seed.py                # Initial product data
│   └── routes/                # Flask blueprints
├── .github/workflows/
│   └── release.yml            # CI/CD pipeline
├── config_template.yml        # Copy to config.yml and fill in values
├── docker-compose.yml         # Production
├── docker-compose.dev.yml     # Development (local build + pgAdmin)
├── Dockerfile
└── Makefile                   # Dev shortcuts (make help)
```