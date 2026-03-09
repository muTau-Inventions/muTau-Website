# muTau-Website

Company website for **muTau-Inventions** — AI Models to FPGA, Made Simple.

Built with Flask, PostgreSQL, and Docker. Features a public-facing marketing site, product catalogue, research papers, documentation, a contact/offer form, user authentication, and an admin panel.

---

## Quick Start

```bash
git clone https://github.com/muTau-Inventions/muTau-Website.git
cd muTau-Website
```

Copy and edit the environment file:

```bash
cp docker-compose.yml docker-compose.override.yml
# Set SECRET_KEY and DATABASE_URL in docker-compose.override.yml
```

Then build and run:

```bash
make build
make up
```

The app is available at `http://localhost`.

---

## Environment Variables

| Variable       | Description                         | Required |
|----------------|-------------------------------------|----------|
| `DATABASE_URL` | PostgreSQL connection string        | ✅ Yes   |
| `SECRET_KEY`   | Flask session secret (strong, random) | ✅ Yes |

> **Note:** The app will refuse to start if `SECRET_KEY` is missing or still set to `change_this_in_production`.

---

## First Admin Account

```bash
make create-admin EMAIL=admin@example.com NAME="Max Mueller" PASSWORD=yourpassword
```

---

## Adding Research Papers

Use the `make` target to add a paper. The PDF must already be in the `research/` directory:

```bash
make create-paper \
  PDF_PATH="main.pdf" \
  TITLE="My Paper Title" \
  AUTHORS="Max Mueller, Sarah Schmidt" \
  DATE="2026-01-15" \
  DESCRIPTION="Short abstract here."
```

Or insert directly via SQL:

```sql
INSERT INTO papers (pdf_path, title, authors, date, description)
VALUES ('main.pdf', 'Paper Title', 'Author Name', '2026-01-15', 'Abstract...');
```

---

## Documentation

Place `.md` files in the `docs/` directory. They are automatically rendered on the `/docs` page. Files are displayed in alphabetical order.

```
docs/
├── 01-getting-started.md
├── 02-installation.md
└── 03-api-reference.md
```

> **Note:** Docs are cached per worker process. Restart the container after adding or editing files (`make restart`).

---

## Development

```bash
make logs      # follow web container logs
make shell     # open bash inside the web container
make restart   # restart web container without a rebuild
make down      # stop all containers
```

---

## Project Structure

```
.
├── docs/                        # Markdown documentation (served at /docs)
├── research/                    # Research PDFs (served at /research/pdf/<path>)
├── static/
│   ├── css/                     # Per-page and base stylesheets
│   ├── js/                      # Particles, nav, theme, tabs, docs, scroll
│   └── img/
├── templates/
│   ├── admin/                   # Admin panel pages
│   ├── auth/                    # Login, register, account, forgot-password
│   ├── errors/                  # 403, 404, 500
│   └── legal/                   # Impressum, Datenschutz, AGB
└── src/mutau_website/
    ├── __init__.py              # App factory + init_db()
    ├── extensions.py            # db, bcrypt, login_manager, admin_required
    ├── models.py                # User, PasswordResetToken, Product, Paper, Offer
    ├── mail.py                  # Mail stubs (ready for SMTP)
    ├── seed.py                  # Initial product seed data
    └── routes/
        ├── main.py              # /, /about, /contact, /offer
        ├── auth.py              # /login, /logout, /register, /forgot-password, /account
        ├── content.py           # /docs, /research, /research/pdf/<path>
        ├── products.py          # /products, /products/<slug>
        ├── legal.py             # /impressum, /datenschutz, /agb
        └── admin.py             # /admin — dashboard, products, papers, offers, users
```

---

## Known TODOs / FIXMEs

- **E-mail verification** — `is_verified` is hardcoded to `True` in `auth.py`. Flip to `False` and implement the verification flow when SMTP is configured.
- **Password reset** — token generation is in place; the `send_password_reset_email()` call just needs to be uncommented once SMTP is set up.
- **Contact form** — currently flashes a success message but does not persist or forward the message. Hook up to SMTP or save to DB.
- **Admin paper/product management** — CRUD UI marked as coming soon in the admin panel.
- **SMTP / mail.py** — all three stubs (`send_verification_email`, `send_password_reset_email`, `send_newsletter`) are no-ops. Implement with Flask-Mail or similar.