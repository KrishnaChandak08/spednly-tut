import os
import re
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import (
    init_db, get_db, get_user_by_email, get_user_by_id, get_monthly_stats,
    get_recent_expenses, get_category_totals, get_all_expenses,
    get_monthly_totals, get_years_with_data, get_category_totals_for_year,
    get_monthly_category_matrix,
    add_expense_record, get_expense_by_id, update_expense_record, delete_expense_record,
    create_email_confirmation, get_email_confirmation_by_token,
    get_pending_email, clear_email_confirmation,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")


@app.template_filter("inr")
def inr_format(value):
    return "{:,.2f}".format(float(value))


@app.template_filter("inr_compact")
def inr_compact(value):
    v = float(value)
    if v >= 100000:
        return f"₹{v/100000:.1f}L"
    if v >= 1000:
        return f"₹{v/1000:.1f}k"
    return f"₹{int(v)}"


@app.template_filter("friendly_date")
def friendly_date(date_str):
    try:
        return datetime.strptime(str(date_str)[:10], "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        return date_str


# ------------------------------------------------------------------ #
# Email helper                                                        #
# ------------------------------------------------------------------ #

def _email_confirmation_html(name, confirm_url):
    return f"""
    <!DOCTYPE html><html><body style="font-family:sans-serif;background:#f7f6f3;padding:2rem;">
    <div style="max-width:480px;margin:0 auto;background:#fff;border-radius:12px;padding:2rem;border:1px solid #e4e1da;">
      <p style="font-size:1.2rem;font-weight:600;color:#0f0f0f;margin-bottom:0.5rem;">◈ Spendly</p>
      <h2 style="color:#0f0f0f;margin-bottom:1rem;">Confirm your new email</h2>
      <p style="color:#444;line-height:1.6;">Hi {name},</p>
      <p style="color:#444;line-height:1.6;">
        We received a request to update your Spendly email address.
        Click the button below to confirm — this link expires in 24 hours.
      </p>
      <a href="{confirm_url}"
         style="display:inline-block;margin:1.5rem 0;background:#1a472a;color:#fff;
                padding:0.75rem 1.75rem;border-radius:6px;text-decoration:none;font-weight:500;">
        Confirm email address
      </a>
      <p style="color:#888;font-size:0.85rem;">
        If you didn't request this change, you can safely ignore this email.
      </p>
    </div>
    </body></html>
    """


def send_confirmation_email(to_email, name, confirm_url):
    smtp_user = os.environ.get("MAIL_USERNAME")
    smtp_pass = os.environ.get("MAIL_PASSWORD")
    smtp_host = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("MAIL_PORT", 587))
    mail_from = os.environ.get("MAIL_FROM", smtp_user or "noreply@spendly.in")

    if not smtp_user or not smtp_pass:
        print(f"\n[DEV] Email confirmation link for {to_email}:\n  {confirm_url}\n")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Confirm your new email address — Spendly"
    msg["From"]    = f"Spendly <{mail_from}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(_email_confirmation_html(name, confirm_url), "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as srv:
        srv.ehlo()
        srv.starttls()
        srv.login(smtp_user, smtp_pass)
        srv.sendmail(mail_from, to_email, msg.as_string())


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("landing"))
    if request.method == "POST":
        name             = request.form.get("name", "").strip()
        email            = request.form.get("email", "").strip().lower()
        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or len(password) < 8:
            return render_template("register.html", error="Please fill in all fields. Password must be at least 8 characters.")

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return render_template("register.html", error="Please enter a valid email address.")

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
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.close()

        flash(f"Account created! Please sign in, {name}.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("landing"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid email or password.")

        session.clear()
        session["user_id"]   = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


def _group_expenses_by_month(expenses):
    groups = []
    index  = {}
    for exp in expenses:
        key = exp["date"][:7]
        if key not in index:
            try:
                label = datetime.strptime(key, "%Y-%m").strftime("%B %Y")
            except Exception:
                label = key
            index[key] = len(groups)
            groups.append({"month": key, "label": label, "expenses": [], "total": 0.0})
        g = groups[index[key]]
        g["expenses"].append(exp)
        g["total"] += exp["amount"]
    return groups


@app.route("/expenses")
def expenses():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user_id = session["user_id"]

    # Year selection (defaults to current year)
    current_year    = datetime.now().year
    try:
        selected_year = int(request.args.get("year", current_year))
    except (ValueError, TypeError):
        selected_year = current_year
    available_years = get_years_with_data(user_id) or [current_year]
    if selected_year not in available_years:
        selected_year = available_years[0]

    all_expenses                 = get_all_expenses(user_id)
    monthly_total, expense_count = get_monthly_stats(user_id)
    category_totals              = get_category_totals(user_id)
    top_category                 = category_totals[0]["category"] if category_totals else "—"
    grouped_expenses             = _group_expenses_by_month(all_expenses)

    # Bar chart: all 12 months of selected year, heights scaled to 120 px
    monthly_bars = get_monthly_totals(user_id, year=selected_year)
    bar_max = max((b["total"] for b in monthly_bars), default=0) or 1
    for bar in monthly_bars:
        bar["height"] = max(4, int(bar["total"] / bar_max * 120))

    # Per-month change vs previous month (used in compare table)
    for i, bar in enumerate(monthly_bars):
        prev = monthly_bars[i - 1]["total"] if i > 0 else None
        if prev is not None and prev > 0:
            delta             = (bar["total"] - prev) / prev * 100
            bar["change"]     = round(delta, 1)
            bar["change_dir"] = "up" if delta > 0 else ("down" if delta < 0 else "flat")
        else:
            bar["change"]     = None
            bar["change_dir"] = None

    # MoM badge: always compares real current vs previous calendar month
    last6         = get_monthly_totals(user_id)
    mom_direction = None
    mom_pct       = None
    curr_t        = last6[-1]["total"] if last6 else 0
    prev_t        = last6[-2]["total"] if len(last6) >= 2 else 0
    if prev_t > 0:
        delta         = (curr_t - prev_t) / prev_t * 100
        mom_pct       = abs(round(delta, 1))
        mom_direction = "up" if curr_t > prev_t else ("down" if curr_t < prev_t else "flat")
    elif curr_t > 0:
        mom_direction = "new"

    # Compare tab: category breakdown for selected year
    compare_categories = get_category_totals_for_year(user_id, selected_year)
    year_total = sum(c["total"] for c in compare_categories)
    cat_max    = compare_categories[0]["total"] if compare_categories else 1
    for cat in compare_categories:
        cat["bar_w"] = max(3, int(cat["total"] / cat_max * 100))
        cat["pct"]   = round(cat["total"] / year_total * 100, 1) if year_total else 0

    # Month-vs-month category matrix for interactive compare tab
    monthly_cat_matrix = get_monthly_category_matrix(user_id, selected_year)

    return render_template(
        "expenses.html",
        grouped_expenses=grouped_expenses,
        monthly_total=monthly_total,
        expense_count=expense_count,
        top_category=top_category,
        monthly_bars=monthly_bars,
        mom_direction=mom_direction,
        mom_pct=mom_pct,
        selected_year=selected_year,
        available_years=available_years,
        current_year=current_year,
        compare_categories=compare_categories,
        year_total=year_total,
        monthly_cat_matrix=monthly_cat_matrix,
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user_id = session["user_id"]

    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name:
            flash("Name cannot be empty.", "error")
            return redirect(url_for("profile"))

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("profile"))

        db = get_db()
        current_user = db.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()

        if email != current_user["email"]:
            taken = db.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id)).fetchone()
            if taken:
                db.close()
                flash("That email address is already in use.", "error")
                return redirect(url_for("profile"))

            # Update name only; hold email until confirmed
            db.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
            db.commit()
            db.close()
            session["user_name"] = name

            token      = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
            create_email_confirmation(user_id, email, token, expires_at)
            confirm_url = url_for("confirm_email_change", token=token, _external=True)

            try:
                send_confirmation_email(email, name, confirm_url)
                flash(f"A confirmation link has been sent to {email}. Your email will update once confirmed.", "success")
            except Exception:
                flash("Profile saved, but we couldn't send the confirmation email. Check your mail settings.", "error")

            return redirect(url_for("profile"))

        # Email unchanged — update name only
        db.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
        db.commit()
        db.close()
        session["user_name"] = name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    user          = get_user_by_id(user_id)
    pending_email = get_pending_email(user_id)
    try:
        member_since = datetime.strptime(user["created_at"][:10], "%Y-%m-%d").strftime("%B %Y")
    except Exception:
        member_since = ""
    monthly_total, expense_count = get_monthly_stats(user_id)
    recent_expenses  = get_recent_expenses(user_id)
    category_totals  = get_category_totals(user_id)
    top_category     = category_totals[0]["category"] if category_totals else "—"
    max_cat_total    = category_totals[0]["total"]    if category_totals else 1
    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        pending_email=pending_email,
        monthly_total=monthly_total,
        expense_count=expense_count,
        top_category=top_category,
        recent_expenses=recent_expenses,
        category_totals=category_totals,
        max_cat_total=max_cat_total,
    )


@app.route("/profile/change-password", methods=["POST"])
def change_password():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user_id = session["user_id"]

    current_pw = request.form.get("current_password", "")
    new_pw     = request.form.get("new_password", "")
    confirm_pw = request.form.get("confirm_new_password", "")

    user = get_user_by_id(user_id)
    if not check_password_hash(user["password"], current_pw):
        flash("Current password is incorrect.", "error")
        return redirect(url_for("profile"))

    if len(new_pw) < 8:
        flash("New password must be at least 8 characters.", "error")
        return redirect(url_for("profile"))

    if new_pw != confirm_pw:
        flash("New passwords do not match.", "error")
        return redirect(url_for("profile"))

    hashed = generate_password_hash(new_pw, method="pbkdf2:sha256")
    db = get_db()
    db.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
    db.commit()
    db.close()
    flash("Password changed successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/confirm-email/<token>")
def confirm_email_change(token):
    confirmation = get_email_confirmation_by_token(token)

    if not confirmation:
        flash("This confirmation link is invalid or has already been used.", "error")
        return redirect(url_for("login"))

    if datetime.utcnow() > datetime.fromisoformat(confirmation["expires_at"]):
        clear_email_confirmation(token)
        flash("This confirmation link has expired. Please update your email again.", "error")
        target = url_for("profile") if session.get("user_id") == confirmation["user_id"] else url_for("login")
        return redirect(target)

    db = get_db()
    taken = db.execute(
        "SELECT id FROM users WHERE email = ? AND id != ?",
        (confirmation["new_email"], confirmation["user_id"]),
    ).fetchone()
    if taken:
        db.close()
        clear_email_confirmation(token)
        flash("That email address is no longer available.", "error")
        target = url_for("profile") if session.get("user_id") == confirmation["user_id"] else url_for("login")
        return redirect(target)

    db.execute("UPDATE users SET email = ? WHERE id = ?", (confirmation["new_email"], confirmation["user_id"]))
    db.execute("DELETE FROM email_confirmations WHERE token = ?", (token,))
    db.commit()
    db.close()

    flash("Your email address has been updated successfully.", "success")
    return redirect(url_for("profile") if session.get("user_id") == confirmation["user_id"] else url_for("login"))


@app.route("/profile/delete", methods=["POST"])
def delete_account():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    user_id = session["user_id"]

    password = request.form.get("password", "")
    user = get_user_by_id(user_id)
    if not check_password_hash(user["password"], password):
        flash("Incorrect password. Account not deleted.", "error")
        return redirect(url_for("profile"))

    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    db.close()
    session.clear()
    flash("Your account has been permanently deleted.", "success")
    return redirect(url_for("landing"))


CATEGORIES = [
    "Food", "Transport", "Bills", "Health", "Entertainment",
    "Shopping", "Education", "Travel", "Other",
]
PAYMENT_METHODS = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title          = request.form.get("title", "").strip()
        amount_str     = request.form.get("amount", "").strip()
        category       = request.form.get("category", "").strip()
        date           = request.form.get("date", "").strip()
        payment_method = request.form.get("payment_method", "").strip()
        notes          = request.form.get("notes", "").strip()

        error = None
        if not title:
            error = "Title is required."
        elif not amount_str:
            error = "Amount is required."
        else:
            try:
                amount = float(amount_str)
                if amount <= 0:
                    error = "Amount must be greater than zero."
            except ValueError:
                error = "Please enter a valid amount."
        if not error and not category:
            error = "Category is required."
        if not error and not date:
            error = "Date is required."

        if error:
            return render_template(
                "expense_form.html", mode="add", error=error,
                form=request.form, categories=CATEGORIES, payment_methods=PAYMENT_METHODS,
            )

        add_expense_record(
            session["user_id"], title, float(amount_str),
            category, date, payment_method or None, notes or None,
        )
        flash("Expense added successfully.", "success")
        return redirect(url_for("expenses"))

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template(
        "expense_form.html", mode="add",
        categories=CATEGORIES, payment_methods=PAYMENT_METHODS, today=today,
    )


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])
    if not expense:
        flash("Expense not found.", "error")
        return redirect(url_for("expenses"))

    if request.method == "POST":
        title          = request.form.get("title", "").strip()
        amount_str     = request.form.get("amount", "").strip()
        category       = request.form.get("category", "").strip()
        date           = request.form.get("date", "").strip()
        payment_method = request.form.get("payment_method", "").strip()
        notes          = request.form.get("notes", "").strip()

        error = None
        if not title:
            error = "Title is required."
        elif not amount_str:
            error = "Amount is required."
        else:
            try:
                amount = float(amount_str)
                if amount <= 0:
                    error = "Amount must be greater than zero."
            except ValueError:
                error = "Please enter a valid amount."
        if not error and not category:
            error = "Category is required."
        if not error and not date:
            error = "Date is required."

        if error:
            return render_template(
                "expense_form.html", mode="edit", expense=expense, error=error,
                form=request.form, categories=CATEGORIES, payment_methods=PAYMENT_METHODS,
            )

        update_expense_record(
            id, session["user_id"], title, float(amount_str),
            category, date, payment_method or None, notes or None,
        )
        flash("Expense updated successfully.", "success")
        return redirect(url_for("expenses"))

    return render_template(
        "expense_form.html", mode="edit", expense=expense,
        categories=CATEGORIES, payment_methods=PAYMENT_METHODS,
    )


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])
    if not expense:
        flash("Expense not found.", "error")
    else:
        delete_expense_record(id, session["user_id"])
        flash(f"“{expense['title']}” deleted.", "success")
    return redirect(url_for("expenses"))


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
