# muTau-Website

Company website for muTau-Inventions — AI Models to FPGA, Made Simple.

## Setup

```bash
git clone https://github.com/muTau-Inventions/muTau-Website.git
cd muTau-Website
make build
make up
```

The app runs on `http://localhost`.

## Create the first admin

```bash
make create-admin EMAIL=admin@example.com NAME="Max Mueller" PASSWORD=yourpassword
```

## Documentation

Place `.md` files in the `docs/` directory. They are rendered automatically on the `/docs` page.

## Research Papers

Add papers to the `research/` directory using the DB. Each paper needs a PDF file and a database entry (admin panel — coming soon).

For now, entries can be added directly to the database:

```sql
INSERT INTO papers (pdf_path, title, authors, date, description)
VALUES ('subfolder/paper.pdf', 'Paper Title', 'Author Name', '2026-01-01', 'Abstract...');
```

## Development

```bash
make logs     # follow web logs
make shell    # bash into the web container
make restart  # restart web container without rebuild
```

## Environment Variables

| Variable       | Description                        | Default                  |
|----------------|------------------------------------|--------------------------|
| `DATABASE_URL` | PostgreSQL connection string       | required                 |
| `SECRET_KEY`   | Flask session secret               | required in production   |

## Project Structure

```
src/mutau_website/
├── __init__.py          # App factory
├── extensions.py        # db, bcrypt, login_manager, admin_required
├── models.py            # User, PasswordResetToken, Product, Paper
├── mail.py              # Mail stubs (ready for SMTP)
├── seed.py              # Initial product data
└── routes/
    ├── main.py          # index, about, contact
    ├── auth.py          # login, logout, register, forgot_password, account
    ├── content.py       # docs, research
    ├── products.py      # products, product_detail
    ├── legal.py         # impressum, datenschutz, agb
    └── admin.py         # admin dashboard (stub)
```
