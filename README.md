# muTau-Website

Company website for **muTau-Inventions**: AI Models to FPGA, Made Simple.

Built with Flask, PostgreSQL, (pgweb), and Docker.

---

## Development

```bash
git clone https://github.com/muTau-Inventions/muTau-Website.git
cd muTau-Website
cp config_template.yml config.yml   # then edit config.yml
cp .env_template .env # then edit .env
```

After editing those two files run:
```bash
make build
make up
```

Site: `http://localhost:80` · pgweb: `http://localhost:8080`

All make commands use `docker-compose.dev.yml`. Run `make help` for a full list.

### Live editing

`templates/` and `static/` are bind-mounted in dev, so changes are visible after `make restart`. Please note that `make restart` only restarts the web container (app image).

---

## Environment Variables (`.env`)

`.env` should never be committed. Copy from the template:

```bash
cp .env_template.yml .env
```

| Key                   | Description                                                                   |
|------------------------|------------------------------------------------------------------------------|
| `POSTGRES_USER`        | PostgreSQL username.                                                         |
| `POSTGRES_PASSWORD`    | PostgreSQL password.                                                         |
| `POSTGRES_DB`          | Name of the application’s PostgreSQL database e.g mutau.                     |
| `POSTGRES_PORT`        | PostgreSQL port (default `5432`).                                            |
| `WEB_SECRET_KEY`       | Secret key for session signing and encryption.                               |
| `WEB_ADMIN_EMAIL`      | Default administrator email.                                                 |
| `WEB_ADMIN_NAME`       | Display name of the admin account.                                           |
| `WEB_ADMIN_PASSWORD`   | Password for the admin account.                                              |

## Configuration (`config.yml`)

`config.yml` should never be committed. Copy from the template:

```bash
cp config_template.yml config.yml
```

| Key                   | Description                                               |
|-----------------------|-----------------------------------------------------------|
| `app.base_url`        | Public URL used in email links, e.g. `https://example.com`|
| `app.log_level`       | `DEBUG` / `INFO` / `WARNING` / `ERROR`                    |
| `mail.smtp_host`      | SMTP server                                               |
| `mail.smtp_port`      | SMTP port (default `587`)                                 |
| `mail.smtp_use_tls`   | `true` / `false`                                          |
| `mail.smtp_user`      | SMTP login                                                |
| `mail.smtp_password`  | SMTP password                                             |
| `mail.from_address`   | Sender, e.g. `muTau <noreply@example.com>`                |

---

## Content

### Documentation

Place `.md` files in `docs/`. They render at `/docs` in alphabetical order.

```
docs/
├── 01-getting-started.md
└── 02-api-reference.md
```

---

## Production Deployment

Deployments are triggered automatically by publishing a GitHub Release.
The CI workflow (`.github/workflows/docker-publish.yml`) builds and pushes a Docker image
to `ghcr.io/mutau-inventions/mutau-website:latest`.



**On the server**, only four files are needed:

```
/your/deploy/path/
├── .env                your live enviroment vars
├── config.yml          your live config
├── docs/               bind-mounted into container
├── research/           bind-mounted into container
└── docker-compose.yml  copy from repo
```

`templates/` and `static/` are baked into the release image already.

---

## Project Structure

```
.
├── docs/                      # Markdown docs
├── research/                  # Research PDFs
├── static/                    # CSS, JS, images
├── templates/                 # Jinja2 templates
├── src/mutau_website/         # Source Code
├── .github/workflows/         # Github Workflows
│   ├── ci.yml                 # CI Test Build on every push to github
│   └── release.yml            # CD Publish Image on ghrc.io
├── .env                       # docker compose and hight level values across containers. See Enviroment Variables section
├── config.yml                 # configuration of web container. See Configuration section
├── docker-compose.yml         # Production
├── docker-compose.dev.yml     # Development (local build + pgweb)
├── Dockerfile                 # Docker Image file
└── Makefile                   # Dev shortcuts (make help)
```

## LICENSE
This Repository does not fall under any Open Source license yet.