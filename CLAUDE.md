# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate the virtual environment first
source venv/bin/activate

# Run the development server (port 5001)
python app.py

# Install dependencies
pip install -r requirements.txt

# Run tests (no tests directory exists yet — create tests/ when adding tests)
pytest
```

## Architecture

**Spendly** is a Flask expense-tracker app structured as a teaching project — students implement features in numbered steps. Routes are stubbed in `app.py` with placeholder strings until implemented.

### Stack
- **Backend**: Flask + SQLite (via stdlib `sqlite3`)
- **Templates**: Jinja2, all extending `templates/base.html`
- **Frontend**: Vanilla HTML/CSS/JS — no JS framework. Styles live in `static/css/style.css`; `static/js/main.js` is a stub students populate
- **Testing**: pytest + pytest-flask

### Key files
- `app.py` — all Flask routes; currently serves landing, login, register, terms, and privacy pages. Placeholder routes exist for logout, profile, and expense CRUD (`/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`)
- `database/db.py` — stub for `get_db()`, `init_db()`, and `seed_db()`; students write this in Step 1
- `templates/base.html` — shared nav (Sign in / Get started links) and footer (Terms + Privacy links)
- `static/css/style.css` — 748-line stylesheet with all sections pre-built (Variables, Navbar, Hero, Auth pages, Buttons, Footer, Responsive). Check here before adding new CSS classes.

### Database conventions (planned)
`database/db.py` should expose:
- `get_db()` — returns a `sqlite3.Connection` with `row_factory = sqlite3.Row` and `PRAGMA foreign_keys = ON`
- `init_db()` — creates tables using `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — inserts sample data for development

### Template pattern
All pages `{% extends "base.html" %}` and fill `{% block title %}`, `{% block content %}`, and optionally `{% block head %}` (page-scoped CSS) and `{% block scripts %}` (page-scoped JS).

### Implementation steps (teaching project)
The project is built step-by-step. Current state:
- **Done**: Landing page, login/register templates (HTML only), terms, privacy
- **Step 1** (next): Write `database/db.py` — `get_db()`, `init_db()`, `seed_db()`
- **Steps 2–3**: Wire up register/login POST handlers and sessions
- **Steps 4–9**: Profile page, expense dashboard, add/edit/delete expenses

### Known gotchas
- `login.html` and `register.html` forms use `method="POST"` but the routes in `app.py` only accept GET. When implementing auth, add `methods=["GET", "POST"]` to those route decorators.
- `app.secret_key` is not set in `app.py`. Flask sessions won't work until it is — add it before implementing any auth or flash messages.
- No `tests/` directory exists yet. Create it when adding tests.

### Currency
The app uses Indian Rupees (₹) throughout.
