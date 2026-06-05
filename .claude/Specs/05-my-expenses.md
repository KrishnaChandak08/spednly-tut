# Spec: My Expenses

## Overview
This step replaces the `/expenses` stub with a fully functional expense dashboard for logged-in users. The page lists every expense belonging to the current user in reverse-chronological order, displays summary cards (total spend this month, total all-time, expense count), and provides action links to add, edit, and delete expenses. Unauthenticated visitors are redirected to `/login`. This is the central hub of the app — all expense CRUD features in Steps 6–9 branch from here.

## Depends On
- Step 01 — Database Setup (`expenses` table and `get_db()` must exist)
- Step 02 — Registration (users must be creatable)
- Step 03 — Login and Logout (`session["user_id"]` must be set for access control)
- Step 04 — Profile Page (`get_monthly_stats`, `get_category_totals` helpers already in `db.py`)

## Routes
* **GET /expenses** — Render the expense dashboard showing the current user's expenses and summary stats — Access Level: `logged-in`

## Database Changes
No new tables or columns. The `expenses` table already exists with: `id`, `user_id`, `title`, `amount`, `category`, `date`, `notes`, `created_at`.

One new helper function is required in `database/db.py`:

**`get_all_expenses(user_id)`** — returns all expense rows for a user ordered by `date DESC, id DESC`. Each row must include: `id`, `title`, `amount`, `category`, `date`, `notes`.

The existing helpers `get_monthly_stats(user_id)` and `get_category_totals(user_id)` are already present and should be reused — do not duplicate them.

## Templates
* **Create:** `templates/expenses.html`
* **Modify:** `templates/base.html` — add a "My Expenses" nav link visible only to logged-in users (link to `url_for("expenses")`)

## Files to Change
- `app.py` — replace the `expenses()` stub (currently returns a plain string) with a real route handler
- `database/db.py` — add `get_all_expenses(user_id)` helper; update the import in `app.py` accordingly
- `templates/base.html` — add nav link for logged-in users

## Files to Create
- `templates/expenses.html`

## New Dependencies
No new dependencies.

## Rules for Implementation
1. **No SQLAlchemy or ORMs:** Interact with the database using direct `sqlite3` connections via `get_db()`.
2. **Parameterized Queries Only:** Never build SQL with string concatenation or f-strings.
3. **Password Security:** No password handling in this step — N/A.
4. **Design/CSS Variables:** Use existing CSS custom properties from `static/css/style.css`; check the file before adding any new classes. Never hardcode hex colour values.
5. **Template Inheritance:** `expenses.html` must extend `base.html` and fill `{% block title %}` and `{% block content %}`.
6. **Auth guard:** The `/expenses` route must redirect to `url_for("login")` if `session.get("user_id")` is falsy — do not rely on the template to enforce this.
7. **Reuse existing helpers:** Call `get_monthly_stats` and `get_category_totals` from `db.py` — do not inline equivalent SQL in the route.
8. **Currency formatting:** Use the existing `{{ amount | inr }}` Jinja filter (defined in `app.py`) and always prefix with `₹`.
9. **Stub links are acceptable:** The Add, Edit, and Delete action links may point to their existing stub routes — they do not need to be functional in this step.
10. **No JS required:** The page must be fully functional with zero JavaScript for the list and summary display.

## Definition of Done
- [ ] Visiting `GET /expenses` while logged out redirects to `/login`
- [ ] Visiting `GET /expenses` while logged in returns HTTP 200 and renders the expense list
- [ ] The page displays a "This Month" total spend in ₹ (matches `get_monthly_stats` output)
- [ ] The page displays the total number of expenses for the current user
- [ ] Every expense row shows: title, amount (₹), category, and date
- [ ] Expenses are ordered most-recent first
- [ ] An "Add expense" link is visible on the page (may point to the stub route)
- [ ] Each expense row has Edit and Delete action links (may point to stub routes)
- [ ] If the user has no expenses, the page shows an empty-state message (e.g. "No expenses yet") instead of an empty table
- [ ] The base nav shows a "My Expenses" link for logged-in users
- [ ] `get_all_expenses` is defined in `database/db.py` and uses a parameterized query
