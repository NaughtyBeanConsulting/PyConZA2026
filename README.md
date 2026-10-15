# PyCon ZA 2026 Blog

A small CMS blog: **Django 6.1**, **htmx**, **Alpine.js**, **Tailwind CSS v4** and **Postgres**.
Content is managed in the Django admin, themed with **Django Unfold**. Static files are served
by **WhiteNoise**, and configuration comes from environment variables (`python-dotenv` reads `.env`).

## What's in it

- **Posts**: draft or published, scheduled publishing (a future `published_at`), category, tags,
  excerpt, and a WYSIWYG editor. Staff can preview drafts on the live site.
- **Pages**: standalone CMS pages such as About, served at `/<slug>/` and optionally listed in the nav.
- **Live search** (htmx, search as you type) and **Load more** pagination, both served from one
  Django template partial (`{% partialdef post-cards %}`).
- **Alpine.js**: mobile menu, dark-mode toggle (remembered per browser), copy-link button.
- **RSS feed** at `/feed/`.
- **Custom user model**: users log in with their **email**. There is no username field, and
  emails are case-insensitive.
- Rich text is cleaned with `nh3` when saved and again when rendered.

## Local setup

Needs Python 3.14, Node 20+, and Postgres with the database named in `.env`.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

npm install
npm run build            # Tailwind CSS + htmx + Alpine -> static/dist/

cp .env.example .env     # if you don't have one, then fill in DB_* values
python manage.py migrate
python manage.py createsuperuser      # prompts for email, not username
python manage.py seed_demo            # optional: demo posts + an About page
python manage.py runserver
```

- Site: http://localhost:8000
- Admin: http://localhost:8000/admin/

While you work on templates, run `npm run dev` in a second terminal to rebuild the CSS on save.

Run the tests with `python manage.py test`.

## Settings

```
app/settings/
├── base.py         # shared: apps, middleware, Postgres, auth, static, Unfold
├── development.py  # DEBUG on, console email, WhiteNoise serves from static/ directly
└── production.py   # DEBUG off, required secrets, HTTPS hardening, compressed hashed static
```

`DJANGO_SETTINGS_MODULE` chooses the settings module. `manage.py` defaults to development, and
`wsgi.py`/`asgi.py` default to production. A value in `.env` or the real environment overrides
both defaults, and real environment variables take precedence over `.env`.

## Production

Set these in the environment (or in a `.env` on the server):

| Variable | Notes |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `app.settings.production` |
| `DJANGO_SECRET_KEY` | Long and random. Required. |
| `ALLOWED_HOSTS` | e.g. `blog.example.com`. Required. |
| `CSRF_TRUSTED_ORIGINS` | e.g. `https://blog.example.com` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Postgres |
| `SECURE_HSTS_SECONDS` | Defaults to `3600`. Raise it to `31536000` once HTTPS is confirmed. |
| `SECURE_HSTS_PRELOAD` | Off by default. Turn it on only if you'll submit the domain to the preload list. |
| `SECURE_SSL_REDIRECT` | Defaults to `True`. |

Deploy steps:

```bash
pip install -r requirements.txt
npm ci && npm run build
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py check --deploy
gunicorn app.wsgi --bind 0.0.0.0:8000 --workers 3
```

TLS is expected to end at a proxy or load balancer in front of gunicorn, and that proxy must
set `X-Forwarded-Proto`. WhiteNoise serves `/static/` with content-hashed filenames, pre-compressed
Brotli and gzip copies, and year-long cache headers, so no separate static server is needed.

There are no user uploads, so no media storage is configured. Adding images would need
object storage such as S3, because WhiteNoise serves static files only.
