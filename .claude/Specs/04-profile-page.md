# Feature: Profile Page

## Overview
A user profile page at `/profile` that displays account information and a basic spending summary. Logged-in users can update their name, email, and password, and may permanently delete their account. Unauthenticated visitors are redirected to `/login`.

## User Stories
- As a logged-in user, I want to see my name and email so I know which account I'm using.
- As a logged-in user, I want to update my name or email so I can keep my account details current.
- As a logged-in user, I want to change my password so I can keep my account secure.
- As a logged-in user, I want to see my spending stats (total this month, number of expenses) so I get a quick sense of my activity.
- As a logged-in user, I want to delete my account so I can remove my data from the app.

## Functional Requirements
1. `GET /profile` — renders `profile.html` with the current user's data and monthly stats; redirects to `/login` if not authenticated.
2. `POST /profile` — accepts form data to update name and/or email; validates non-empty name and valid email format; checks for email uniqueness before saving; flashes success or error.
3. `POST /profile/change-password` — accepts `current_password`, `new_password`, `confirm_new_password`; verifies current password with `check_password_hash`; requires new password ≥ 8 characters and confirmation match; hashes new password with `pbkdf2:sha256`; flashes success or error.
4. `POST /profile/delete` — verifies the user's password before deletion (confirmation step); deletes the user row (cascade removes their expenses via `ON DELETE CASCADE`); clears the session; redirects to `/` with a goodbye flash.
5. Monthly stats are computed by querying `expenses` filtered by `user_id` and `strftime('%Y-%m', date) = strftime('%Y-%m', 'now')`: total `SUM(amount)` and `COUNT(*)`.

## Non-Functional Requirements
- All three POST routes must be protected: redirect to `/login` if `session.get("user_id")` is absent.
- Passwords must never be stored or logged in plain text.
- The delete flow requires explicit password re-entry — no one-click deletion.
- Currency displayed as `₹` with comma-formatted amounts (e.g., ₹1,250.00).

## Implementation Details

### Files to change

**`app.py`**
- Replace the stub `profile()` route with:
  ```python
  @app.route("/profile", methods=["GET", "POST"])
  def profile():
      if not session.get("user_id"):
          return redirect(url_for("login"))
      # GET: fetch user + monthly stats, render profile.html
      # POST: validate + update name/email, flash, redirect
  ```
- Add two new routes:
  ```python
  @app.route("/profile/change-password", methods=["POST"])
  def change_password():
      ...

  @app.route("/profile/delete", methods=["POST"])
  def delete_account():
      ...
  ```

**`database/db.py`**
- Add `get_user_by_id(user_id)` — fetches a user row by primary key (analogous to existing `get_user_by_email`).
- Add `get_monthly_stats(user_id)` — returns `(total_amount, expense_count)` for the current calendar month.

**`templates/profile.html`** (new file)
- Extends `base.html`.
- Sections:
  1. **Account info card** — displays name and email (read-only view).
  2. **Edit profile form** — `POST /profile` with `name` and `email` fields; pre-filled with current values.
  3. **Change password form** — `POST /profile/change-password` with `current_password`, `new_password`, `confirm_new_password`.
  4. **Spending summary card** — shows "This Month" total (₹) and expense count.
  5. **Danger zone** — "Delete Account" button that reveals an inline confirmation form (`POST /profile/delete`) asking for password.
- Display `flash` messages (success/error) at the top of the page.

**`static/css/style.css`**
- Check existing classes before adding new ones (file is 748 lines). Add a `.profile-*` section only if needed; prefer re-using `.card`, `.btn`, `.form-group`, `.danger` classes if they exist.

### Pseudocode — profile GET
```
user = get_user_by_id(session["user_id"])
total, count = get_monthly_stats(session["user_id"])
render profile.html(user=user, monthly_total=total, expense_count=count)
```

### Pseudocode — profile POST (edit)
```
name  = form["name"].strip()
email = form["email"].strip().lower()
if not name or not valid_email(email): flash error, redirect /profile
if email != user["email"]:
    if get_user_by_email(email): flash "email taken", redirect /profile
db.execute("UPDATE users SET name=?, email=? WHERE id=?", name, email, user_id)
session["user_name"] = name   # keep nav in sync
flash success, redirect /profile
```

### Pseudocode — change password POST
```
current  = form["current_password"]
new_pw   = form["new_password"]
confirm  = form["confirm_new_password"]
if not check_password_hash(user["password"], current): flash "wrong password"
if new_pw != confirm or len(new_pw) < 8: flash error
hashed = generate_password_hash(new_pw, method="pbkdf2:sha256")
db.execute("UPDATE users SET password=? WHERE id=?", hashed, user_id)
flash success, redirect /profile
```

### Pseudocode — delete account POST
```
password = form["password"]
if not check_password_hash(user["password"], password): flash "wrong password", redirect /profile
db.execute("DELETE FROM users WHERE id=?", user_id)
session.clear()
flash "Your account has been deleted."
redirect /
```

### Dependencies
- No new packages required; uses existing `werkzeug.security`, `sqlite3`, `flask.session`, `flask.flash`.

## Acceptance Criteria
- [ ] `GET /profile` returns 200 for a logged-in user and redirects to `/login` for a guest.
- [ ] Profile page displays the logged-in user's name and email.
- [ ] Profile page displays the current-month total spend (₹) and expense count.
- [ ] Submitting the edit form with valid data updates name/email in the DB and in `session["user_name"]`.
- [ ] Submitting the edit form with a duplicate email shows an error flash and does not update.
- [ ] Changing password with correct current password and matching new passwords ≥ 8 chars succeeds.
- [ ] Changing password with wrong current password shows an error and does not update.
- [ ] Delete account flow requires password entry; on correct password the user row is deleted, session cleared, and the user is redirected to `/`.
- [ ] Delete account with wrong password shows an error and does not delete.
- [ ] No plain-text passwords appear in any template, log, or DB column.
