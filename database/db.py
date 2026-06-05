import sqlite3
import os

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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        DATE    NOT NULL,
            notes       TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
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
