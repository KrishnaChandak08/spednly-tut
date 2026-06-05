import sqlite3
import os
from datetime import date as _date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "spendly.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title          TEXT    NOT NULL,
            amount         REAL    NOT NULL,
            category       TEXT    NOT NULL,
            date           DATE    NOT NULL,
            payment_method TEXT,
            notes          TEXT,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS email_confirmations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            new_email  TEXT    NOT NULL,
            token      TEXT    NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    # Migrate existing DB: add payment_method if it was created before this column existed
    try:
        conn.execute("ALTER TABLE expenses ADD COLUMN payment_method TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def create_email_confirmation(user_id, new_email, token, expires_at):
    conn = get_db()
    conn.execute("DELETE FROM email_confirmations WHERE user_id = ?", (user_id,))
    conn.execute(
        "INSERT INTO email_confirmations (user_id, new_email, token, expires_at) VALUES (?, ?, ?, ?)",
        (user_id, new_email, token, expires_at),
    )
    conn.commit()
    conn.close()


def get_email_confirmation_by_token(token):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM email_confirmations WHERE token = ?", (token,)
    ).fetchone()
    conn.close()
    return row


def get_pending_email(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT new_email FROM email_confirmations WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row["new_email"] if row else None


def clear_email_confirmation(token):
    conn = get_db()
    conn.execute("DELETE FROM email_confirmations WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def add_expense_record(user_id, title, amount, category, date, payment_method, notes):
    conn = get_db()
    conn.execute(
        """INSERT INTO expenses (user_id, title, amount, category, date, payment_method, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, title, amount, category, date, payment_method or None, notes or None),
    )
    conn.commit()
    conn.close()


def get_expense_by_id(expense_id, user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_expense_record(expense_id, user_id, title, amount, category, date, payment_method, notes):
    conn = get_db()
    conn.execute(
        """UPDATE expenses
           SET title = ?, amount = ?, category = ?, date = ?, payment_method = ?, notes = ?
           WHERE id = ? AND user_id = ?""",
        (title, amount, category, date, payment_method or None, notes or None, expense_id, user_id),
    )
    conn.commit()
    conn.close()


def delete_expense_record(expense_id, user_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id),
    )
    conn.commit()
    conn.close()


def get_all_expenses(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT id, title, amount, category, date, notes
           FROM expenses WHERE user_id = ?
           ORDER BY date DESC, id DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_expenses(user_id, limit=5):
    conn = get_db()
    rows = conn.execute(
        """SELECT title, amount, category, date
           FROM expenses WHERE user_id = ?
           ORDER BY date DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_totals(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT category, SUM(amount) AS total
           FROM expenses WHERE user_id = ?
           GROUP BY category ORDER BY total DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_stats(user_id):
    conn = get_db()
    row = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count
           FROM expenses
           WHERE user_id = ?
             AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')""",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["total"], row["count"]


def get_years_with_data(user_id):
    conn = get_db()
    rows = conn.execute(
        """SELECT DISTINCT strftime('%Y', date) AS year
           FROM expenses WHERE user_id = ?
           ORDER BY year DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [int(r["year"]) for r in rows]


def get_monthly_totals(user_id, year=None):
    """
    year given  → all 12 months of that year (for bar chart / compare tab).
    year=None   → last 6 calendar months (for MoM badge).
    """
    conn = get_db()
    rows = conn.execute(
        """SELECT strftime('%Y-%m', date) AS month,
                  SUM(amount) AS total, COUNT(*) AS cnt
           FROM expenses WHERE user_id = ?
           GROUP BY month""",
        (user_id,),
    ).fetchall()
    conn.close()
    db_data = {r["month"]: {"total": r["total"], "cnt": r["cnt"]} for r in rows}

    today = _date.today()
    if year:
        result = []
        for m in range(1, 13):
            key  = f"{year:04d}-{m:02d}"
            d    = _date(year, m, 1)
            data = db_data.get(key, {"total": 0.0, "cnt": 0})
            result.append({
                "month":      key,
                "label":      d.strftime("%b"),
                "label_full": d.strftime("%B"),
                "total":      data["total"],
                "count":      data["cnt"],
            })
        return result
    else:
        result = []
        for i in range(5, -1, -1):
            yr = today.year
            mo = today.month - i
            while mo <= 0:
                mo += 12; yr -= 1
            key  = f"{yr:04d}-{mo:02d}"
            d    = _date(yr, mo, 1)
            data = db_data.get(key, {"total": 0.0, "cnt": 0})
            result.append({
                "month":      key,
                "label":      d.strftime("%b '%y"),
                "label_full": d.strftime("%B %Y"),
                "total":      data["total"],
                "count":      data["cnt"],
            })
        return result


def get_category_totals_for_year(user_id, year):
    conn = get_db()
    rows = conn.execute(
        """SELECT category, SUM(amount) AS total, COUNT(*) AS cnt
           FROM expenses WHERE user_id = ? AND strftime('%Y', date) = ?
           GROUP BY category ORDER BY total DESC""",
        (user_id, str(year)),
    ).fetchall()
    conn.close()
    return [{"category": r["category"], "total": r["total"], "count": r["cnt"]} for r in rows]


def get_monthly_category_matrix(user_id, year):
    conn = get_db()
    rows = conn.execute(
        """SELECT strftime('%Y-%m', date) AS month, category, SUM(amount) AS total
           FROM expenses WHERE user_id = ? AND strftime('%Y', date) = ?
           GROUP BY month, category""",
        (user_id, str(year)),
    ).fetchall()
    conn.close()
    matrix = {}
    for r in rows:
        m = r["month"]
        if m not in matrix:
            matrix[m] = {}
        matrix[m][r["category"]] = round(r["total"], 2)
    return matrix


def seed_db():
    conn = get_db()

    # Skip seeding if data already exists
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    conn.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.in", "hashed_password_placeholder"),
    )
    user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    sample_expenses = [
        (user_id, "Groceries",       1250.00, "Food",          "2026-05-28", "Weekly grocery run"),
        (user_id, "Metro card",       500.00, "Transport",     "2026-05-27", None),
        (user_id, "Netflix",          649.00, "Entertainment", "2026-05-25", "Monthly subscription"),
        (user_id, "Electricity bill", 980.00, "Utilities",     "2026-05-20", "May bill"),
        (user_id, "Lunch",            320.00, "Food",          "2026-05-30", "Office cafeteria"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, title, amount, category, date, notes) VALUES (?,?,?,?,?,?)",
        sample_expenses,
    )

    conn.commit()
    conn.close()
