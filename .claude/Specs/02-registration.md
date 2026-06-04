# Feature: User Registration

## Overview
Wire up the `/register` route to handle POST submissions from `register.html`. On success, create a user account with a hashed password and redirect to the login page. On failure, re-render the form with an inline error message.

## User Stories
- As a new visitor, I can fill in my name, email, password, and confirm password and submit the form to create an account.
- As a new visitor, I see a clear error if my passwords don't match, my email is already taken, or my input is invalid.
- As a newly registered user, I am redirected to the login page to sign in with my new credentials.

## Functional Requirements

1. **Route accepts POST** — `/register` must accept `methods=["GET", "POST"]`.
2. **Input validation** — on POST, validate:
   - `name` is non-empty.
   - `email` is non-empty and matches the pattern `^[^@\s]+@[^@\s]+\.[^@\s]+$` (must have a local part, `@`, domain, and TLD).
   - `password` is at least 8 characters.
   - `confirm_password` matches `password`.
3. **Duplicate email check** — query the `users` table; if the email already exists, re-render the form with `error="An account with that email already exists."`.
4. **Password hashing** — use `werkzeug.security.generate_password_hash(password, method="pbkdf2:sha256")`. Never store plaintext passwords. (`scrypt` is unavailable on Python 3.9 / macOS OpenSSL — always specify `pbkdf2:sha256` explicitly.)
5. **Insert user** — insert a new row into `users (name, email, password)`.
6. **No session on registration** — do not set a session after registration; the user must log in explicitly.
7. **Flash message** — flash `"Account created! Please sign in, <name>."` before redirecting.
8. **Redirect on success** — redirect to `url_for("login")`.
9. **GET request** — render `register.html` with no error (existing behaviour, unchanged).

## Non-Functional Requirements
- Passwords must be hashed before persistence; plaintext storage is not acceptable.
- Validation errors must be shown inline in the form (the template has `{% if error %}` block).
- The route must not create a session for any registration attempt.
- No external auth libraries (Flask-Login, etc.) — use raw `flask.session`.

## Implementation Details

### Files changed
| File | Change |
|------|--------|
| `app.py` | Update `/register` route — add POST handler with confirm-password check, redirect to login |
| `templates/register.html` | Add `confirm_password` field below the password field |

### Route pseudocode
```python
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name             = request.form.get("name", "").strip()
        email            = request.form.get("email", "").strip().lower()
        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or len(password) < 8:
            return render_template("register.html", error="Please fill in all fields. Password must be at least 8 characters.")

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            db.close()
            return render_template("register.html", error="An account with that email already exists.")

        hashed = generate_password_hash(password, method="pbkdf2:sha256")
        db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed))
        db.commit()
        db.close()

        flash(f"Account created! Please sign in, {name}.")
        return redirect(url_for("login"))

    return render_template("register.html")
```

### Confirm password field (register.html)
Add after the password field:
```html
<div class="form-group">
    <label for="confirm_password">Confirm password</label>
    <input type="password" id="confirm_password" name="confirm_password"
           class="form-input" placeholder="Re-enter your password"
           required>
</div>
```

### Known gotcha
`werkzeug.security.generate_password_hash` defaults to `scrypt` in Werkzeug 3.x, which is unavailable on Python 3.9 / macOS (Apple OpenSSL). Always pass `method="pbkdf2:sha256"` explicitly.

## Acceptance Criteria
- [ ] Submitting valid name / email / matching passwords creates a row in `users` with a hashed (`pbkdf2:sha256:...`) password.
- [ ] After successful registration, the user is redirected to `/login` (not auto-logged in).
- [ ] Submitting mismatched passwords re-renders the form with `"Passwords do not match."`.
- [ ] Submitting a malformed email (no `@`, no domain, no TLD) re-renders the form with `"Please enter a valid email address."`.
- [ ] Submitting a duplicate email re-renders the form with an error and does **not** create a second user row.
- [ ] Submitting a password shorter than 8 characters re-renders the form with a validation error.
- [ ] Submitting an empty name or email re-renders the form with a validation error.
- [ ] The GET `/register` route still renders the empty form with no regression.
